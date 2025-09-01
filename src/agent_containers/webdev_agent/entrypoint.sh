#!/bin/bash
set -e


if [ -z "$JOB_PROMPT" ]; then
    echo "❌ Error: JOB_PROMPT is required. Pass it as an env var."
    exit 1
fi

JOB_ID=${JOB_ID:-$(date +%s)}
echo "🚀 Starting agent for job $JOB_ID"
echo "   Prompt: $JOB_PROMPT"

chown -R agentuser:agentuser /workspace 2>/dev/null || true

# Create handler for SIGTERM
cleanup() {
    echo "📦 Creating project archive..."
    cd /workspace
    zip -r "agent_project_${JOB_ID}.zip" . -x "*.zip"
    echo "✅ Project archived to /workspace/agent_project_${JOB_ID}.zip"
    exit 0
}
trap cleanup SIGTERM

# Start supervisord (this becomes PID 1)
echo "🔧 Starting services..."
exec supervisord -c /etc/supervisord.conf