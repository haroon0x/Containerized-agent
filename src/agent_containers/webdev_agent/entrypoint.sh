#!/bin/bash
set -e

# Validate required environment variables
if [ -z "$JOB_PROMPT" ]; then
    echo "❌ Error: JOB_PROMPT is required. Pass it as an env var."
    exit 1
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ Error: GEMINI_API_KEY is required. Pass it as an env var."
    exit 1
fi

JOB_ID=${JOB_ID:-$(date +%s)}

echo "🚀 Starting agent for job $JOB_ID"
echo "   Prompt: $JOB_PROMPT"

mkdir -p /workspace
chown -R agentuser:agentuser /workspace 2>/dev/null || true

cleanup() {
    echo "📦 Creating project archive..."
    cd /workspace
    if [ "$(ls -A .)" ]; then
        zip -r "project_${JOB_ID}.zip" . -x "*.zip" -x "*/.zip"    2>/dev/null || true
        echo "✅ Project archived to /workspace/project_${JOB_ID}.zip"
    else
        echo "⚠️  No files found in workspace to archive"
    fi
    exit 0
}
trap cleanup SIGTERM SIGINT

export JOB_PROMPT
export JOB_ID
export GEMINI_API_KEY

echo "🔧 Starting services..."
exec supervisord -c /etc/supervisord.conf