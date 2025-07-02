# --- Agent Container Dockerfile ---
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    nodejs npm \
    xvfb xdotool x11-utils \
    supervisor \
    git curl wget \
    net-tools lsof \
    sudo \
    tigervnc-standalone-server \
    tigervnc-common \
    xterm \
    && rm -rf /var/lib/apt/lists/*

# Install noVNC and websockify
RUN git clone https://github.com/novnc/noVNC.git /opt/noVNC \
    && git clone https://github.com/novnc/websockify /opt/noVNC/utils/websockify

# Install Jupyter and TypeScript
RUN pip3 install --no-cache-dir jupyterlab notebook \
    && npm install -g typescript

# Create a non-root user
RUN useradd -ms /bin/bash agentuser \
    && usermod -aG sudo agentuser \
    && echo 'agentuser ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Set up working directory
WORKDIR /home/agentuser/workspace
RUN chown -R agentuser:agentuser /home/agentuser

# either use entrypoint.sh or supervisord.conf for starting all services 
# COPY entrypoint.sh /entrypoint.sh
COPY "supervisorvisord.conf" "/etc/supervisord.conf"
#using supervisor since it relaods processes automatically if they fails

USER agentuser

EXPOSE 6080 8888 8000

ENTRYPOINT ["supervisord", "-c", "/etc/supervisord.conf"]
