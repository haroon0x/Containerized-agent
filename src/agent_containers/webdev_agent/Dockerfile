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
    x11-xserver-utils \
    netcat-openbsd \
    sudo \
    zip \
    procps \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash agentuser \
    && usermod -aG sudo agentuser \
    && echo 'agentuser ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers \
    && mkdir -p /home/agentuser/workspace \
    && chown -R agentuser:agentuser /home/agentuser

RUN npm install -g @google/gemini-cli

RUN git clone https://github.com/novnc/noVNC.git /opt/noVNC \
    && git clone https://github.com/novnc/websockify /opt/noVNC/utils/websockify \
    && chown -R agentuser:agentuser /opt/noVNC


RUN mkdir -p /home/agentuser/.vnc \
    && chown -R agentuser:agentuser /home/agentuser/.vnc

RUN ln -sf /home/agentuser/workspace /workspace

COPY src/agent_containers/webdev_agent/supervisord.conf /etc/supervisord.conf
COPY src/agent_containers/webdev_agent/entrypoint.sh /entrypoint.sh
COPY src/agent_containers/webdev_agent/vnc-healthcheck.sh /usr/local/bin/vnc-healthcheck.sh

RUN chmod +x /entrypoint.sh \
    && chmod +x /usr/local/bin/vnc-healthcheck.sh

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD /usr/local/bin/vnc-healthcheck.sh

USER agentuser
WORKDIR /home/agentuser/workspace

EXPOSE 5901 6080 8888 8000

ENTRYPOINT ["/entrypoint.sh"]