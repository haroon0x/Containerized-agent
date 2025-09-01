FROM node:22-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive


RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    curl wget gnupg ca-certificates \
    git \
    supervisor \
    tigervnc-standalone-server \
    tigervnc-common \
    xterm \
    netcat-openbsd \
    sudo \
    xfce4-session \
    xfce4-panel \
    xfce4-terminal \
    xfwm4 \
    xfdesktop4 \
    dbus-x11 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash agentuser \
    && usermod -aG sudo agentuser \
    && echo 'agentuser ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers \
    && mkdir -p /home/agentuser/workspace/ \
    && chown -R agentuser:agentuser /home/agentuser


RUN su - agentuser -c "mkdir -p /home/agentuser/.vnc" \
    && su - agentuser -c "echo 'passw0rd' | vncpasswd -f > /home/agentuser/.vnc/passwd" \
    && chmod 600 /home/agentuser/.vnc/passwd \
    && chown agentuser:agentuser /home/agentuser/.vnc/passwd


USER agentuser

RUN mkdir -p ~/.vnc && \
    cat > ~/.vnc/xstartup <<'EOF'
#!/bin/bash
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS
export XDG_SESSION_TYPE=x11
export XDG_CURRENT_DESKTOP=XFCE
export XDG_SESSION_DESKTOP=xfce
dbus-launch --exit-with-session startxfce4 &
EOF
RUN chmod +x ~/.vnc/xstartup

RUN npm install -g @google/gemini-cli


RUN git clone https://github.com/novnc/noVNC.git /opt/noVNC \
    && git clone https://github.com/novnc/websockify /opt/noVNC/utils/websockify

RUN ln -s /home/agentuser/workspace /workspace


# Copy configuration files
COPY src/agent_containers/webdev_agent/supervisord.conf /etc/supervisord.conf
COPY src/agent_containers/webdev_agent/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Health check for VNC
COPY src/agent_containers/webdev_agent/vnc-healthcheck.sh /usr/local/bin/vnc-healthcheck.sh
RUN chmod +x /usr/local/bin/vnc-healthcheck.sh


HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD /usr/local/bin/vnc-healthcheck.sh

WORKDIR /home/agentuser/workspace

EXPOSE 6080 8888 8000

ENTRYPOINT ["/entrypoint.sh"]
