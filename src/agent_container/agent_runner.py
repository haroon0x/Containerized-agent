#!/usr/bin/env python3
"""
This is the actual agent that runs inside the container.
"""

import logging
import subprocess
import os
import json
import sys
from typing import Dict, Any, List
from src.agent.utils.call_llm import call_llm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentRunner:
    """Main agent runner that executes tasks in the container."""

    def __init__(self):
        self.workspace_dir = "/workspace"
        self.output_dir = "/workspace/output"

    def analyze_task(self, task: str) -> Dict[str, Any]:
        """Analyze the task and determine required actions."""
        try:
            analysis_prompt = f"""
            Analyze this task and determine what actions are needed:
            Task: {task}

            You are in a Linux container with these capabilities:
            - Shell commands (bash, git, curl, wget, etc.)
            - Python 3.11 with many packages
            - Node.js and npm
            - File operations in /workspace directory
            - GUI automation tools (xdotool)
            - Web scraping capabilities

            Return a JSON with the following structure:
            {{
                "actions": [
                    {{
                        "type": "shell_command",
                        "description": "what this command does",
                        "command": "the actual shell command to execute",
                        "working_dir": "/workspace"
                    }},
                    {{
                        "type": "python_code",
                        "description": "what this code does", 
                        "code": "the Python code to execute",
                        "output_file": "optional output file path"
                    }}
                ],
                "estimated_time": "time estimate",
                "requirements": ["list", "of", "requirements"]
            }}
            """

            analysis = call_llm(analysis_prompt)
            return json.loads(analysis)
        except Exception as e:
            logger.error(f"Error analyzing task: {e}")
            return {"actions": [], "estimated_time": "unknown", "requirements": []}

    def execute_shell_command(self, command: str, working_dir: str = "/workspace") -> Dict[str, Any]:
        """Execute a shell command in the container."""
        try:
            logger.info(f"Executing shell command: {command}")

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=working_dir,
                timeout=300  
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode,
                "command": command,
                "working_dir": working_dir
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "Command timed out after 5 minutes",
                "command": command,
                "working_dir": working_dir
            }
        except Exception as e:
            logger.error(f"Error executing shell command: {e}")
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "command": command,
                "working_dir": working_dir
            }

    def execute_python_code(self, code: str, output_file: str = None) -> Dict[str, Any]:
        """Execute Python code in the container."""
        try:
            logger.info(f"Executing Python code")

            temp_file = "/tmp/agent_code.py"
            with open(temp_file, "w") as f:
                f.write(code)

            result = subprocess.run(
                ["python3", temp_file],
                capture_output=True,
                text=True,
                cwd="/workspace",
                timeout=300
            )

            os.remove(temp_file)

            if output_file and result.stdout:
                output_path = os.path.join("/workspace", output_file)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "w") as f:
                    f.write(result.stdout)

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode,
                "code": code,
                "output_file": output_file
            }
        except Exception as e:
            logger.error(f"Error executing Python code: {e}")
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "code": code,
                "output_file": output_file
            }

    def run_task(self, task: str) -> Dict[str, Any]:
        """Run a complete task with all actions."""
        logger.info(f"Starting task: {task}")

        analysis = self.analyze_task(task)
        actions = analysis.get("actions", [])

        results = {
            "task": task,
            "analysis": analysis,
            "shell_results": [],
            "python_results": [],
            "status": "completed"
        }

        for action in actions:
            action_type = action.get("type")

            if action_type == "shell_command":
                command = action.get("command", "")
                working_dir = action.get("working_dir", "/workspace")
                result = self.execute_shell_command(command, working_dir)
                results["shell_results"].append(result)

            elif action_type == "python_code":
                code = action.get("code", "")
                output_file = action.get("output_file")
                result = self.execute_python_code(code, output_file)
                results["python_results"].append(result)

            else:
                logger.warning(f"Unknown action type: {action_type}")

        logger.info(f"Task completed. Executed {len(results['shell_results'])} shell commands and {len(results['python_results'])} Python scripts")
        return results

def main():
    """Main entry point for the agent container."""

    task = os.getenv("JOB_PROMPT", "echo 'Hello from agent container'")
    job_id = os.getenv("JOB_ID", "unknown")

    logger.info(f"Agent container started for job {job_id}")
    logger.info(f"Task: {task}")

    os.makedirs("/workspace/output", exist_ok=True)

    try:

        runner = AgentRunner()

        results = runner.run_task(task)

        result_file = "/workspace/output/result.json"
        with open(result_file, "w") as f:
            json.dump(results, f, indent=2)

        logger.info(f"Results saved to {result_file}")
        logger.info(f"Job {job_id} completed successfully")

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")

        error_result = {
            "job_id": job_id,
            "task": task,
            "error": str(e),
            "status": "failed"
        }

        with open("/workspace/output/result.json", "w") as f:
            json.dump(error_result, f, indent=2)

        sys.exit(1)

if __name__ == "__main__":
    main()