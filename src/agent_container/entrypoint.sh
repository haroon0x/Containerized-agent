#!/bin/bash

# Get job details from environment variables
JOB_PROMPT=${JOB_PROMPT:-"Default task"}
JOB_ID=${JOB_ID:-"unknown"}

echo "Starting agent for job $JOB_ID with prompt: $JOB_PROMPT"

# Create output directory
mkdir -p /workspace/output
chown -R agentuser:agentuser /workspace/output 2>/dev/null || true

echo "Starting Gemini agent..." 


gemini --prompt "$JOB_PROMPT" \
       --all-files \
       --approval-mode=yolo \
       | tee /workspace/output/result.log

echo "Agent completed for job $JOB_ID"