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

# Ensure workspace is ready
chown -R agentuser:agentuser /workspace 2>/dev/null || true

echo "Starting Gemini agent..." 

gemini --prompt "$JOB_PROMPT" \
       --all-files \
       --approval-mode=yolo \
       --model "gemini-2.5-flash"

# Zip the workspace
echo "📦 Creating project archive..."
cd /workspace
zip -r "agent_project_${JOB_ID}.zip" . -x "*.zip"
echo "✅ Project archived to /workspace/agent_project_${JOB_ID}.zip"

echo "Agent completed for job $JOB_ID"
tail -f /dev/null