#!/bin/bash
set -e

# Ensure JOB_PROMPT is provided
if [ -z "$JOB_PROMPT" ]; then
    echo "❌ Error: JOB_PROMPT is required. Pass it as an env var."
    exit 1
fi

JOB_ID=${JOB_ID:-$(date +%s)}

echo "🚀 Starting agent for job $JOB_ID"
echo "   Prompt: $JOB_PROMPT"
# Create output directory
mkdir -p /workspace/output
chown -R agentuser:agentuser /workspace/output 2>/dev/null || true

echo "Starting Gemini agent..." 

gemini --prompt "$JOB_PROMPT" \
       --all-files \
       --approval-mode=yolo

echo "Agent completed for job $JOB_ID"