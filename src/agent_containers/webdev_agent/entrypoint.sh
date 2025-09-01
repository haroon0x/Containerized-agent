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
chown -R agentuser:agentuser /home/agentuser/.vnc 2>/dev/null || true

# Create handler for SIGTERM
cleanup() {
    echo "📦 Creating project archive..."
    cd /workspace
    zip -r "agent_project_${JOB_ID}.zip" . -x "*.zip"
    echo "✅ Project archived to /workspace/agent_project_${JOB_ID}.zip"
    exit 0
}
trap cleanup SIGTERM

if [ ! -d "/home/agentuser/.vnc" ]; then
    mkdir -p /home/agentuser/.vnc
fi

# Create VNC password if it doesn't exist
if [ ! -f "/home/agentuser/.vnc/passwd" ]; then
    echo "passw0rd" | vncpasswd -f > /home/agentuser/.vnc/passwd
    chmod 600 /home/agentuser/.vnc/passwd
    chown agentuser:agentuser /home/agentuser/.vnc/passwd
fi

# Create xstartup if it doesn't exist
if [ ! -f "/home/agentuser/.vnc/xstartup" ]; then
    cat > /home/agentuser/.vnc/xstartup << 'EOF'
#!/bin/bash
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS
export XDG_SESSION_TYPE=x11
export XDG_CURRENT_DESKTOP=XFCE
export XDG_SESSION_DESKTOP=xfce
dbus-launch --exit-with-session startxfce4 &
EOF
    chmod +x /home/agentuser/.vnc/xstartup
    chown agentuser:agentuser /home/agentuser/.vnc/xstartup
fi

# Start supervisord (this becomes PID 1)
echo "🔧 Starting services..."
echo "🖥️  VNC will be available at: http://localhost:6080"
exec supervisord -c /etc/supervisord.conf