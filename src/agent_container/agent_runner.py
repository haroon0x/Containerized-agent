#!/usr/bin/env python3
"""
This is the actual agent that runs inside the container.
"""

import os
import logging
from src.agent.agent_runtime import AgentRuntime

def main():
    logging.basicConfig(level=logging.INFO)
    task = os.getenv("JOB_PROMPT", " write a hello function ina python file")
    job_id = os.getenv("JOB_ID", "unknown")
    output_dir = os.getenv("AGENT_OUTPUT_DIR", "output")
    logging.info(f"Agent runner started for job {job_id}")
    AgentRuntime(task, job_id, output_dir=output_dir).run()

if __name__ == "__main__":
    main()