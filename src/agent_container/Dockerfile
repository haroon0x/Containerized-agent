FROM debian:bookworm-slim

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
    xterm \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs 

# Install Jupyter Lab
#RUN pip3 install jupyterlab

RUN npm install -g @google/gemini-cli


#COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv


#RUN npm install -g typescript

RUN git clone https://github.com/novnc/noVNC.git /opt/noVNC \
    && git clone https://github.com/novnc/websockify /opt/noVNC/utils/websockify

RUN useradd -ms /bin/bash agentuser \
    && usermod -aG sudo agentuser \
    && echo 'agentuser ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers \
    && chown -R agentuser:agentuser /home/agentuser \
    && mkdir -p /home/agentuser/workspace/output \
    && chown -R agentuser:agentuser /home/agentuser/workspace/output \
    && ln -s /home/agentuser/workspace /workspace

WORKDIR /home/agentuser/workspace

COPY src/agent_container/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY src/agent_container/supervisord.conf /etc/supervisord.conf

USER agentuser

EXPOSE 6080 8888 8000

ENTRYPOINT ["/entrypoint.sh"]
