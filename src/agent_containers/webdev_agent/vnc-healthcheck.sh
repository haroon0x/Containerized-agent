#!/bin/bash

# Check if Xvnc is running and port 5901 is open
if ! pgrep Xvnc > /dev/null || ! nc -z localhost 5901; then
    exit 1
fi

# Check if noVNC proxy is running and port 6080 is open
if ! nc -z localhost 6080; then
    exit 1
fi

exit 0