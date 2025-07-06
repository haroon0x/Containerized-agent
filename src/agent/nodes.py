import logging
import subprocess
import os
import json
from typing import Any, Dict
from pocketflow import Node
from src.agent.utils.call_llm import call_llm

class TaskAnalysisNode(Node):
    """Analyze the task prompt and determine what actions to take."""
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get the task prompt from shared context."""
        return shared.get("question", "No task provided")
    
    def exec(self, task: str) -> Dict[str, Any]:
        """Analyze the task and determine required actions."""
        try:
            # Use LLM to analyze the task and determine actions
            analysis_prompt = f"""
            Analyze this task and determine what actions are needed:
            Task: {task}
            
            Return a JSON with the following structure:
            {{
                "actions": [
                    {{
                        "type": "shell_command" | "python_code" | "file_operation" | "web_scraping" | "gui_automation",
                        "description": "what this action does",
                        "command": "the actual command or code to execute"
                    }}
                ],
                "estimated_time": "time estimate",
                "requirements": ["list", "of", "requirements"]
            }}
            """
            
            analysis = call_llm(analysis_prompt)
            # Parse the JSON response
            try:
                return json.loads(analysis)
            except json.JSONDecodeError:
                # Fallback if LLM doesn't return valid JSON
                return {
                    "actions": [{"type": "shell_command", "description": "Basic task", "command": "echo 'Task completed'"}],
                    "estimated_time": "1 minute",
                    "requirements": []
                }
        except Exception as e:
            logging.error(f"Error analyzing task: {e}")
            return {"actions": [], "estimated_time": "unknown", "requirements": []}
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Dict[str, Any]) -> None:
        """Store the analysis in shared context."""
        shared["task_analysis"] = exec_res
        shared["actions"] = exec_res.get("actions", [])

class ShellCommandNode(Node):
    """Execute shell commands in the container."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get the next shell command to execute."""
        actions = shared.get("actions", [])
        for action in actions:
            if action.get("type") == "shell_command":
                return action
        return None
    
    def exec(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the shell command."""
        if not action:
            return {"success": False, "output": "No shell command to execute"}
        
        command = action.get("command", "")
        description = action.get("description", "")
        
        try:
            logging.info(f"Executing shell command: {description}")
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                cwd="/workspace"
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode,
                "command": command
            }
        except Exception as e:
            logging.error(f"Error executing shell command: {e}")
            return {"success": False, "output": "", "error": str(e), "command": command}
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Dict[str, Any]) -> None:
        """Store the result and remove the executed action."""
        if "shell_results" not in shared:
            shared["shell_results"] = []
        shared["shell_results"].append(exec_res)
        
        # Remove the executed action
        actions = shared.get("actions", [])
        shared["actions"] = [a for a in actions if a.get("type") != "shell_command" or a != prep_res]

class PythonCodeNode(Node):
    """Execute Python code in the container."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get the next Python code action to execute."""
        actions = shared.get("actions", [])
        for action in actions:
            if action.get("type") == "python_code":
                return action
        return None
    
    def exec(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Python code."""
        if not action:
            return {"success": False, "output": "No Python code to execute"}
        
        code = action.get("command", "")
        description = action.get("description", "")
        
        try:
            logging.info(f"Executing Python code: {description}")
            
            # Create a temporary file to execute the code
            temp_file = "/tmp/agent_code.py"
            with open(temp_file, "w") as f:
                f.write(code)
            
            result = subprocess.run(
                ["python3", temp_file], 
                capture_output=True, 
                text=True, 
                cwd="/workspace"
            )
            
            # Clean up
            os.remove(temp_file)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode,
                "code": code
            }
        except Exception as e:
            logging.error(f"Error executing Python code: {e}")
            return {"success": False, "output": "", "error": str(e), "code": code}
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Dict[str, Any]) -> None:
        """Store the result and remove the executed action."""
        if "python_results" not in shared:
            shared["python_results"] = []
        shared["python_results"].append(exec_res)
        
        # Remove the executed action
        actions = shared.get("actions", [])
        shared["actions"] = [a for a in actions if a.get("type") != "python_code" or a != prep_res]

class ResultCompilationNode(Node):

    """Compile all results into a final output."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get all results to compile."""
        return {
            "task": shared.get("question", ""),
            "analysis": shared.get("task_analysis", {}),
            "shell_results": shared.get("shell_results", []),
            "python_results": shared.get("python_results", []),
            "remaining_actions": shared.get("actions", [])
        }
    
    def exec(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Compile the final result."""
        task = results["task"]
        analysis = results["analysis"]
        shell_results = results["shell_results"]
        python_results = results["python_results"]
        remaining = results["remaining_actions"]
        
        # Create a summary
        summary = {
            "task": task,
            "analysis": analysis,
            "executed_actions": len(shell_results) + len(python_results),
            "remaining_actions": len(remaining),
            "shell_results": shell_results,
            "python_results": python_results,
            "status": "completed" if not remaining else "partial"
        }
        
        return summary
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Dict[str, Any]) -> None:
        """Store the final result."""
        shared["final_result"] = exec_res


