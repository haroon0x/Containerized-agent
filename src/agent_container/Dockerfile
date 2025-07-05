# --- Agent Container Dockerfile ---
FROM alpine:3.19

# Install system packages
RUN apk add --no-cache \
    python3 py3-pip \
    nodejs npm \
    xvfb xdotool xterm \
    supervisor \
    git curl wget \
    net-tools lsof \
    sudo \
    tigervnc \
    bash \
    gcc musl-dev python3-dev \
    libffi-dev \
    openssl-dev \
    && rm -rf /var/cache/apk/*

# Clone noVNC
RUN git clone https://github.com/novnc/noVNC.git /opt/noVNC \
    && git clone https://github.com/novnc/websockify /opt/noVNC/utils/websockify

# Install Python packages
RUN pip3 install --no-cache-dir jupyterlab notebook \
    && npm install -g typescript

# Create a non-root user
RUN adduser -D -s /bin/bash agentuser \
    && echo 'agentuser ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

WORKDIR /home/agentuser/workspace
RUN chown -R agentuser:agentuser /home/agentuser
RUN mkdir -p /home/agentuser/workspace/output && chown -R agentuser:agentuser /home/agentuser/workspace/output
RUN ln -s /home/agentuser/workspace /workspace

# Copy the entire src directory to maintain the correct structure
COPY src/ /home/agentuser/workspace/src/
COPY pyproject.toml /home/agentuser/workspace/
COPY requirements.txt /home/agentuser/workspace/

# Install Python dependencies from requirements.txt
RUN pip3 install --no-cache-dir -r /home/agentuser/workspace/requirements.txt

# Copy entrypoint script
COPY src/agent_container/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy supervisor configuration
COPY src/agent_container/supervisord.conf /etc/supervisord.conf

USER agentuser

EXPOSE 6080 8888 8000

# Use entrypoint for job execution, supervisor for development
ENTRYPOINT ["/entrypoint.sh"]
