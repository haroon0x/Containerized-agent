# --- Agent Container Dockerfile ---
FROM ubuntu:22.04

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
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

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Switch to non-root user
USER agentuser

# Expose ports
EXPOSE 6080 8888 8000

# Entrypoint
ENTRYPOINT ["/entrypoint.sh"] 