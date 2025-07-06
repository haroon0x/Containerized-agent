import os
import json
import logging
from src.agent.flow import create_qa_flow

class AgentRuntime:
    def __init__(self, task: str, job_id: str):
        self.task = task
        self.job_id = job_id
        self.output_dir = f"/workspace/output/{job_id}"
        os.makedirs(self.output_dir, exist_ok=True)
        self.result_file = os.path.join(self.output_dir, "result.json")
        self.flow = create_qa_flow()

    def run(self):
        shared = {"question": self.task}
        try:
            self.flow.run(shared)
            result = {
                "task": self.task,
                "job_id": self.job_id,
                "analysis": shared.get("task_analysis", {}),
                "shell_results": shared.get("shell_results", []),
                "python_results": shared.get("python_results", []),
                "status": "completed"
            }
            with open(self.result_file, "w") as f:
                json.dump(result, f, indent=2)
            logging.info(f"Results saved to {self.result_file}")
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
            return error_result 