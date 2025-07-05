#!/bin/bash

# Get job details from environment variables
JOB_PROMPT=${JOB_PROMPT:-"Default task"}
JOB_ID=${JOB_ID:-"unknown"}

echo "Starting agent for job $JOB_ID with prompt: $JOB_PROMPT"

# Create output directory
mkdir -p /workspace/output

# Set up Python path
export PYTHONPATH="/home/agentuser/workspace:$PYTHONPATH"

# Run the agent runner with the job prompt
cd /home/agentuser/workspace
python3 src/agent_container/agent_runner.py

echo "Agent completed for job $JOB_ID"