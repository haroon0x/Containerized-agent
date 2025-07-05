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


RUN git clone https://github.com/novnc/noVNC.git /opt/noVNC \
    && git clone https://github.com/novnc/websockify /opt/noVNC/utils/websockify


RUN pip3 install --no-cache-dir jupyterlab notebook \
    && npm install -g typescript

# Create a non-root user
RUN useradd -ms /bin/bash agentuser \
    && usermod -aG sudo agentuser \
    && echo 'agentuser ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers


WORKDIR /home/agentuser/workspace
RUN chown -R agentuser:agentuser /home/agentuser

# Copy the agent source code
COPY src/agent/ /home/agentuser/workspace/agent/
COPY src/agent_container/agent_runner.py /home/agentuser/workspace/src/agent_container/
COPY pyproject.toml /home/agentuser/workspace/

# Install Python dependencies directly
RUN pip3 install --no-cache-dir \
    fastapi>=0.115.14 \
    uvicorn>=0.35.0 \
    requests>=2.32.0 \
    google-genai>=1.24.0 \
    python-dotenv>=1.1.1 \
    pocketflow>=0.0.2 \
    pydantic>=2.0.0 \
    typing-extensions>=4.0.0

# Copy entrypoint script
COPY src/agent_container/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy supervisor configuration
COPY src/agent_container/supervisord.conf /etc/supervisord.conf

USER agentuser

EXPOSE 6080 8888 8000

# Use entrypoint for job execution, supervisor for development
ENTRYPOINT ["/entrypoint.sh"]
