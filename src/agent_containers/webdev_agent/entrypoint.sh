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

# Set defaults
JOB_ID=${JOB_ID:-$(date +%s)}
VNC_PASSWORD=${VNC_PASSWORD:-passw0rd}

echo "🚀 Starting agent for job $JOB_ID"
echo "   Prompt: $JOB_PROMPT"

# Ensure X11 directory exists and has correct permissions
sudo mkdir -p /tmp/.X11-unix
sudo chmod 1777 /tmp/.X11-unix
sudo chown root:root /tmp/.X11-unix

# Ensure workspace permissions
mkdir -p /workspace
sudo chown -R agentuser:agentuser /workspace 2>/dev/null || true

# Set up VNC directory and password
mkdir -p /home/agentuser/.vnc
if [ ! -f "/home/agentuser/.vnc/passwd" ]; then
    echo "$VNC_PASSWORD" | vncpasswd -f > /home/agentuser/.vnc/passwd
    chmod 600 /home/agentuser/.vnc/passwd
fi

# Create xstartup if it doesn't exist
if [ ! -f "/home/agentuser/.vnc/xstartup" ]; then
    cat > /home/agentuser/.vnc/xstartup << 'EOF'
#!/bin/bash
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS
export DISPLAY=${DISPLAY:-:1}

# Load user X resources
[ -r "$HOME/.Xresources" ] && xrdb "$HOME/.Xresources"

# Background settings
xsetroot -solid '#2e3440' 2>/dev/null || true
vncconfig -iconic & disown

# Wait until DISPLAY is ready
i=0
while ! xdpyinfo -display "$DISPLAY" >/dev/null 2>&1; do
    sleep 1
    i=$((i+1))
    if [ $i -ge 15 ]; then
        echo "❌ Display $DISPLAY not ready after 15 attempts"
        exit 1
    fi
done

echo "✅ Display $DISPLAY is ready"

# Start window manager and terminal
twm & disown
xterm -geometry 80x24+10+10 -ls -title 'Agent Terminal' -e bash & disown

# Keep script alive
wait
EOF
    chmod +x /home/agentuser/.vnc/xstartup
fi

# Set up cleanup handler
cleanup() {
    echo "📦 Creating project archive..."
    cd /workspace
    if [ "$(ls -A .)" ]; then
        zip -r "agent_project_${JOB_ID}.zip" . -x "*.zip" 2>/dev/null || true
        echo "✅ Project archived to /workspace/agent_project_${JOB_ID}.zip"
    else
        echo "⚠️  No files found in workspace to archive"
    fi
    exit 0
}
trap cleanup SIGTERM SIGINT

# Export environment variables for supervisord
export JOB_PROMPT
export JOB_ID
export GEMINI_API_KEY
export DISPLAY=":1"

echo "🔧 Starting services..."
echo "🖥️  VNC will be available at: http://localhost:6080"
echo "🔑 VNC Password: $VNC_PASSWORD"

# Start supervisord as the main process
exec supervisord -c /etc/supervisord.conf