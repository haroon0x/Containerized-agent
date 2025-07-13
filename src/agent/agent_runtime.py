import os
import json
import logging
import tempfile
import shutil
from pathlib import Path
from src.agent.flow import create_qa_flow

class AgentRuntime:
    def __init__(self, task: str, job_id: str, output_dir: str = None):
        self.task = task
        self.job_id = job_id
        
        if output_dir is None:
            is_container = (
                os.path.exists("/.dockerenv") or 
                os.path.exists("/proc/1/cgroup") and "docker" in open("/proc/1/cgroup").read() or
                os.environ.get("CONTAINER_ENV") == "true"
                )
            
            if is_container and os.path.exists("/workspace"):
                self.output_dir = f"/workspace/output/{job_id}"
            else:
                self.output_dir = os.path.join(os.getcwd(), "output", job_id)
        else:
            self.output_dir = os.path.join(output_dir, job_id)
        
        os.makedirs(self.output_dir, exist_ok=True)
        self.result_file = os.path.join(self.output_dir, "result.json")
        
        self.workspace_dir = os.path.join(self.output_dir, "workspace")
        os.makedirs(self.workspace_dir, exist_ok=True)
        
        self.original_cwd = os.getcwd()
        
        try:
            os.chdir(self.workspace_dir)
            logging.info(f"Changed to workspace directory: {self.workspace_dir}")
        except Exception as e:
            logging.warning(f"Could not change to workspace directory {self.workspace_dir}: {e}")
            self.workspace_dir = self.output_dir
            os.chdir(self.workspace_dir)
        
        self.flow = create_qa_flow()

    def run(self):
        shared = {"question": self.task}
        try:
            logging.info(f"Starting agent execution for task: {self.task}")
            self.flow.run(shared)
            
            created_files = []
            if os.path.exists(self.workspace_dir):
                for root, dirs, files in os.walk(self.workspace_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, self.workspace_dir)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            created_files.append({
                                "filename": rel_path,
                                "content": content,
                                "size": len(content)
                            })
                            logging.info(f"Found created file: {rel_path} ({len(content)} bytes)")
                        except Exception as e:
                            logging.warning(f"Could not read file {file_path}: {e}")
            
            result = {
                "task": self.task,
                "job_id": self.job_id,
                "analysis": shared.get("task_analysis", {}),
                "shell_results": shared.get("shell_results", []),
                "python_results": shared.get("python_results", []),
                "file_results": shared.get("file_results", []),
                "created_files": created_files,
                "workspace_dir": self.workspace_dir,
                "output_dir": self.output_dir,
                "status": "completed"
            }
            
            with open(self.result_file, "w") as f:
                json.dump(result, f, indent=2)
            logging.info(f"Results saved to {self.result_file}")
            
            os.chdir(self.original_cwd)
            
            return result
        except Exception as e:
            logging.error(f"AgentRuntime failed: {e}")
            error_result = {
                "job_id": self.job_id,
                "task": self.task,
                "error": str(e),
                "status": "failed"
            }
            with open(self.result_file, "w") as f:
                json.dump(error_result, f, indent=2)
            
            os.chdir(self.original_cwd)
            
            return error_result 