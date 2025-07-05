#!/bin/bash

# Get job details from environment variables
JOB_PROMPT=${JOB_PROMPT:-"Default task"}
JOB_ID=${JOB_ID:-"unknown"}

echo "Starting agent for job $JOB_ID with prompt: $JOB_PROMPT"

# Create output directory
mkdir -p /workspace/output

# Run the agent with the job prompt
cd /home/agentuser/workspace
python3 -m agent.main --prompt "$JOB_PROMPT" --job-id "$JOB_ID"

echo "Agent completed for job $JOB_ID"