FROM node:22-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv \
    curl wget gnupg ca-certificates \
    git \
    supervisor \
    tigervnc-standalone-server \
    tigervnc-common \
    twm \
    xterm \
    netcat-openbsd \
    sudo \
    zip \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash agentuser \
    && usermod -aG sudo agentuser \
    && echo 'agentuser ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers \
    && mkdir -p /home/agentuser/workspace \
    && chown -R agentuser:agentuser /home/agentuser

USER root

RUN npm install -g @google/gemini-cli

RUN git clone https://github.com/novnc/noVNC.git /opt/noVNC \
    && git clone https://github.com/novnc/websockify /opt/noVNC/utils/websockify \
    && chown -R agentuser:agentuser /opt/noVNC

USER agentuser
WORKDIR /home/agentuser

RUN mkdir -p ~/.vnc \
    && echo "passw0rd" | vncpasswd -f > ~/.vnc/passwd \
    && chmod 600 ~/.vnc/passwd

COPY src/agent_containers/webdev_agent/xstartup ~/.vnc/xstartup
RUN chmod +x ~/.vnc/xstartup


RUN ln -s /home/agentuser/workspace /workspace

COPY src/agent_containers/webdev_agent/supervisord.conf /etc/supervisord.conf
COPY src/agent_containers/webdev_agent/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY src/agent_containers/webdev_agent/vnc-healthcheck.sh /usr/local/bin/vnc-healthcheck.sh
RUN chmod +x /usr/local/bin/vnc-healthcheck.sh
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD /usr/local/bin/vnc-healthcheck.sh

WORKDIR /home/agentuser/workspace

EXPOSE 6080 8888 8000

ENTRYPOINT ["/entrypoint.sh"]
