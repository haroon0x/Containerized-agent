import logging
import subprocess
import os
import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List
from pocketflow import Node
from src.agent.utils.call_llm import call_llm
import time

class TaskAnalysisNode(Node):
    """Analyze the task prompt and determine what actions to take."""
    
    def prep(self, shared: Dict[str, Any]) -> str:
        return shared.get("question", "No task provided")
    
    def exec(self, task: str) -> Dict[str, Any]:
        try:
            analysis_prompt = f"""
            Assume the environment is Ubuntu Linux. All shell commands should be written for bash on Ubuntu.
            Analyze the following task and return a JSON list of actions needed to accomplish it. 
            If the task involves writing, modifying, or executing code, always include a 'python_code' action with the code to be executed, and a 'file_operation' action if a file should be created or modified. 
            
            For file operations, use these operation types:
            - "write": Create or overwrite a file with content
            - "append": Add content to an existing file
            - "create_directory": Create a directory structure
            
            Use this JSON structure:
            {{
                "actions": [
                    {{
                        "type": "shell_command" | "python_code" | "file_operation" | "web_scraping" | "gui_automation",
                        "description": "what this action does",
                        "command": "the actual command, code, or file content to execute",
                        "filename": "(required for file_operation) the filename to write to",
                        "operation": "(optional for file_operation) write|append|create_directory, defaults to write"
                    }}
                ],
                "estimated_time": "time estimate",
                "requirements": ["list", "of", "requirements"]
            }}
            
            Examples:
            - For "create a Python file called hello.py": use file_operation with filename="hello.py"
            - For "create a directory structure": use file_operation with operation="create_directory"
            - For "add to existing file": use file_operation with operation="append"
            
            Task: {task}
            """
            analysis = call_llm(analysis_prompt)
            logging.info(f"Raw LLM analysis response: {analysis}")
            try:
                result = json.loads(analysis)
                actions = result.get("actions", [])
                # Do not add a python_code action for .py file creation
                result["actions"] = actions
                return result
            except json.JSONDecodeError:
                return {
                    "actions": [{"type": "shell_command", "description": "Basic task", "command": "echo 'Task completed'"}],
                    "estimated_time": "1 minute",
                    "requirements": []
                }
        except Exception as e:
            logging.error(f"Error analyzing task: {e}")
            return {"actions": [], "estimated_time": "unknown", "requirements": []}
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Dict[str, Any]) -> None:
        shared["task_analysis"] = exec_res
        shared["actions"] = exec_res.get("actions", [])
        
        actions = exec_res.get("actions", [])
        logging.info(f"Generated {len(actions)} actions:")
        for i, action in enumerate(actions):
            logging.info(f"  Action {i+1}: {action.get('type')} - {action.get('description', 'No description')}")
            if action.get('type') == 'file_operation':
                logging.info(f"    Filename: {action.get('filename')}")
                logging.info(f"    Operation: {action.get('operation', 'write')}")
                logging.info(f"    Content length: {len(action.get('command', ''))}")

class ShellCommandNode(Node):
    """Execute shell commands in the container."""
    
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        actions = shared.get("actions", [])
        shell_commands = [action for action in actions if action.get("type") == "shell_command"]
        self._shared = shared
        return shell_commands

    def exec(self, actions) -> List[Dict[str, Any]]:
        if not actions:
            return [{"success": False, "output": "No shell commands to execute"}]
        if isinstance(actions, dict):
            actions = [actions]
        results = []
        file_results = getattr(self, '_shared', {}).get('file_results', [])
        created_files = set()
        created_files_full = set()
        for fr in file_results:
            if fr.get("success") and fr.get("operation") in ("write", "append") and fr.get("filename"):
                p = Path(fr["filename"])
                created_files.add(p.name.lower())
                created_files.add(p.as_posix().lower())
                created_files_full.add(str(p.resolve().as_posix().lower()))
        linux_only_cmds = {"ls", "ls -la", "pwd", "cat", "touch", "rm", "mv", "cp"}
        import platform
        is_windows = platform.system().lower() == "windows"
        for action in actions:
            command = action.get("command", "")
            description = action.get("description", "")
            try:
                logging.info(f"Executing shell command: {description}")
                parts = command.strip().replace('"', '').replace("'", '').split()
                referenced_files = set()
                for part in parts[1:]:
                    part_norm = part.replace('\\', '/').lower()
                    if part_norm in created_files or os.path.basename(part_norm) in created_files or part_norm in created_files_full:
                        referenced_files.add(part)
                if is_windows and (parts[0] in linux_only_cmds or command in linux_only_cmds):
                    results.append({
                        "success": False,
                        "output": "",
                        "error": f"Command '{command}' is Linux-only and was skipped on Windows.",
                        "command": command
                    })
                    continue
                for fname in referenced_files:
                    file_path = Path(fname)
                    if not file_path.is_absolute():
                        file_path = Path(os.getcwd()) / file_path
                    for _ in range(10):
                        if file_path.exists():
                            break
                        time.sleep(0.1)
                    if not file_path.exists():
                        results.append({
                            "success": False,
                            "output": "",
                            "error": f"File {file_path} not found before execution.",
                            "command": command
                        })
                        break
                else:
                    result = subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        cwd=os.getcwd()
                    )
                    results.append({
                        "success": result.returncode == 0,
                        "output": result.stdout,
                        "error": result.stderr,
                        "return_code": result.returncode,
                        "command": command
                    })
            except Exception as e:
                logging.error(f"Error executing shell command: {e}")
                results.append({"success": False, "output": "", "error": str(e), "command": command})
        return results

    def post(self, shared: Dict[str, Any], prep_res, exec_res) -> None:
        """Store the results and remove the executed actions."""
        if "shell_results" not in shared:
            shared["shell_results"] = []
        if isinstance(exec_res, dict):
            exec_res = [exec_res]
        shared["shell_results"].extend(exec_res)
        actions = shared.get("actions", [])
        shared["actions"] = [a for a in actions if a.get("type") != "shell_command"]

class PythonCodeNode(Node):
    """Execute Python code in the container."""
    
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        actions = shared.get("actions", [])
        python_actions = [action for action in actions if action.get("type") == "python_code"]
        return python_actions

    def exec(self, actions) -> List[Dict[str, Any]]:
        if not actions:
            return [{"success": False, "output": "No Python code to execute"}]
        if isinstance(actions, dict):
            actions = [actions]
        results = []
        for action in actions:
            code = action.get("command", "")
            description = action.get("description", "")
            try:
                logging.info(f"Executing Python code: {description}")
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    f.write(code)
                    temp_file = f.name
                
                result = subprocess.run(
                    ["python", temp_file], 
                    capture_output=True, 
                    text=True, 
                    cwd=os.getcwd(),
                    timeout=30
                )
                
                try:
                    os.remove(temp_file)
                except:
                    pass
                
                results.append({
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr,
                    "return_code": result.returncode,
                    "code": code
                })
            except subprocess.TimeoutExpired:
                logging.error(f"Python code execution timed out: {description}")
                results.append({"success": False, "output": "", "error": "Execution timed out", "code": code})
            except Exception as e:
                logging.error(f"Error executing Python code: {e}")
                results.append({"success": False, "output": "", "error": str(e), "code": code})
        return results

    def post(self, shared: Dict[str, Any], prep_res, exec_res) -> None:
        if "python_results" not in shared:
            shared["python_results"] = []
        if isinstance(exec_res, dict):
            exec_res = [exec_res]
        shared["python_results"].extend(exec_res)
        actions = shared.get("actions", [])
        shared["actions"] = [a for a in actions if a.get("type") != "python_code"]

class FileOperationNode(Node):
    
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        actions = shared.get("actions", [])
        file_operations = [action for action in actions if action.get("type") == "file_operation"]
        return file_operations

    def exec(self, actions) -> List[Dict[str, Any]]:
        if not actions:
            return [{"success": False, "output": "No file operations to execute"}]
        if isinstance(actions, dict):
            actions = [actions]
        results = []
        for action in actions:
            filename = action.get("filename")
            content = action.get("command", "")
            operation_type = action.get("operation", "write")
            if not filename:
                results.append({"success": False, "output": "No filename specified for file operation"})
                continue
            try:
                # Always create files relative to the current working directory
                file_path = Path(filename)
                if not file_path.is_absolute():
                    file_path = Path(os.getcwd()) / file_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                if operation_type == "write":
                    with open(file_path, "w", encoding='utf-8') as f:
                        f.write(content)
                    results.append({
                        "success": True, 
                        "output": f"Created file {file_path} with {len(content)} characters", 
                        "filename": str(file_path),
                        "operation": "write",
                        "size": len(content)
                    })
                elif operation_type == "append":
                    with open(file_path, "a", encoding='utf-8') as f:
                        f.write(content)
                    results.append({
                        "success": True, 
                        "output": f"Appended to file {file_path}", 
                        "filename": str(file_path),
                        "operation": "append"
                    })
                elif operation_type == "create_directory":
                    file_path.mkdir(parents=True, exist_ok=True)
                    results.append({
                        "success": True, 
                        "output": f"Created directory {file_path}", 
                        "filename": str(file_path),
                        "operation": "create_directory"
                    })
                else:
                    results.append({
                        "success": False, 
                        "output": f"Unknown operation type: {operation_type}", 
                        "filename": str(file_path)
                    })
            except Exception as e:
                logging.error(f"Error in file operation: {e}")
                results.append({
                    "success": False, 
                    "output": str(e), 
                    "filename": str(file_path),
                    "operation": operation_type
                })
        return results

    def post(self, shared: Dict[str, Any], prep_res, exec_res) -> None:
        if "file_results" not in shared:
            shared["file_results"] = []
        if isinstance(exec_res, dict):
            exec_res = [exec_res]
        shared["file_results"].extend(exec_res)
        actions = shared.get("actions", [])
        shared["actions"] = [a for a in actions if a.get("type") != "file_operation"]

class ResultCompilationNode(Node):

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "task": shared.get("question", ""),
            "analysis": shared.get("task_analysis", {}),
            "shell_results": shared.get("shell_results", []),
            "python_results": shared.get("python_results", []),
            "remaining_actions": shared.get("actions", [])
        }
    
    def exec(self, results: Dict[str, Any]) -> Dict[str, Any]:
        task = results["task"]
        analysis = results["analysis"]
        shell_results = results["shell_results"]
        python_results = results["python_results"]
        remaining = results["remaining_actions"]
        
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
        shared["final_result"] = exec_res


