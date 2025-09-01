#!/bin/bash
set -e

if [ -z "$JOB_PROMPT" ]; then
    echo "❌ Error: JOB_PROMPT is required. Pass it as an env var."
    exit 1
fi

JOB_ID=${JOB_ID:-$(date +%s)}
echo "🚀 Starting agent for job $JOB_ID"
echo "   Prompt: $JOB_PROMPT"

mkdir -p /tmp/.X11-unix
chmod 1777 /tmp/.X11-unix
chown root:root /tmp/.X11-unix

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

if [ ! -f "/home/agentuser/.vnc/passwd" ]; then
    echo "passw0rd" | vncpasswd -f > /home/agentuser/.vnc/passwd
    chmod 600 /home/agentuser/.vnc/passwd
    chown agentuser:agentuser /home/agentuser/.vnc/passwd
fi

if [ ! -f "/home/agentuser/.vnc/xstartup" ]; then
cat > /home/agentuser/.vnc/xstartup << 'EOF'
#!/bin/bash
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS

export DISPLAY=${DISPLAY:-:1}

# Load user resources
[ -r "$HOME/.Xresources" ] && xrdb "$HOME/.Xresources"

# Set background and basic X defaults
xsetroot -solid '#2e3440' 2>/dev/null || true
vncconfig -iconic & disown

# Wait for DISPLAY to become available
i=0
while ! xdpyinfo -display "$DISPLAY" >/dev/null 2>&1; do
    sleep 1
    i=$((i+1))
    if [ $i -ge 15 ]; then
        echo "❌ Display $DISPLAY not ready after 15 attempts"
        exit 1
    fi
done

# Start terminal and window manager
xterm -geometry 80x24+10+10 -ls -title 'Agent Terminal' -e bash & disown
twm & disown

# Keep the script alive until VNC server stops
wait
EOF
    chmod +x /home/agentuser/.vnc/xstartup
    chown agentuser:agentuser /home/agentuser/.vnc/xstartup
fi

# Start supervisord (this becomes PID 1)
echo "🔧 Starting services..."
echo "🖥️  VNC will be available at: http://localhost:6080"
exec supervisord -c /etc/supervisord.conf