import os
import logging
from src.agent.agent_runtime import AgentRuntime

def main():
    logging.basicConfig(level=logging.INFO)
    task = os.getenv("JOB_PROMPT", "echo 'Hello from agent'" )
    job_id = os.getenv("JOB_ID", "unknown")
    logging.info(f"Agent main started for job {job_id}")
    AgentRuntime(task, job_id).run()

if __name__ == "__main__":
    main() 