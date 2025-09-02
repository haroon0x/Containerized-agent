#!/bin/bash

# Health check script for VNC services
set -e

# Check if Xvnc process is running
if ! pgrep -f "Xvnc :1" > /dev/null 2>&1; then
    echo "❌ Xvnc process not running"
    exit 1
fi

# Check if VNC port 5901 is listening
if ! nc -z localhost 5901 2>/dev/null; then
    echo "❌ VNC port 5901 not listening"
    exit 1
fi

# Check if noVNC port 6080 is listening
if ! nc -z localhost 6080 2>/dev/null; then
    echo "❌ noVNC port 6080 not listening"
    exit 1
fi

# Optional: Check if we can connect to the display
if ! timeout 5 xdpyinfo -display :1 >/dev/null 2>&1; then
    echo "⚠️  Display :1 not responding (but services are running)"
    exit 0  # Don't fail the health check for this
fi

echo "✅ VNC services healthy"
exit 0