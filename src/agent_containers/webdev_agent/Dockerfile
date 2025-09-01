FROM node:22-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive


RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    curl wget gnupg ca-certificates \
    git \
    xvfb xdotool x11-utils x11-apps \
    supervisor \
    net-tools lsof procps \
    sudo \
    tigervnc-standalone-server \
    tigervnc-common \
    xterm 


RUN npm install -g @google/gemini-cli


RUN git clone https://github.com/novnc/noVNC.git /opt/noVNC \
    && git clone https://github.com/novnc/websockify /opt/noVNC/utils/websockify


RUN useradd -ms /bin/bash agentuser \
    && usermod -aG sudo agentuser \
    && echo 'agentuser ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers \
    && mkdir -p /home/agentuser/workspace/output \
    && chown -R agentuser:agentuser /home/agentuser


RUN ln -s /home/agentuser/workspace /workspace

# Copy configs
COPY src/agent_containers/webdev_agent/entrypoint.sh /entrypoint.sh
COPY src/agent_containers/webdev_agent/supervisord.conf /etc/supervisord.conf
RUN chmod +x /entrypoint.sh

USER agentuser
WORKDIR /home/agentuser/workspace



EXPOSE 6080 8888 8000   

ENTRYPOINT ["/entrypoint.sh"]
