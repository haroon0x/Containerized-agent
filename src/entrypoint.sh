set -e #exits if command fails

Xvfb :1 -screen 0 1280x800x24 &
export DISPLAY=:1


vncserver :1 -geometry 1280x800 -SecurityTypes None & 

/opt/noVNC/utils/novnc_proxy --vnc localhost:5901 --listen 6080 &


jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password='' &

# Wait forever (or tail a log file)
wait