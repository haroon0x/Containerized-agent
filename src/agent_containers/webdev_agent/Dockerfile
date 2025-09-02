FROM node:22-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv \
    curl wget gnupg ca-certificates \
    git \
    supervisor \
    sudo \
    zip \
    procps \
    sysstat \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash agentuser \
    && usermod -aG sudo agentuser \
    && echo 'agentuser ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers \
    && mkdir -p /home/agentuser/workspace \
    && chown -R agentuser:agentuser /home/agentuser

RUN npm install -g @google/gemini-cli

# Creates a symlink for access
RUN ln -sf /home/agentuser/workspace /workspace 

COPY src/agent_containers/webdev_agent/supervisord.conf /etc/supervisord.conf
COPY src/agent_containers/webdev_agent/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh 

USER agentuser
WORKDIR /home/agentuser/workspace

ENTRYPOINT ["/entrypoint.sh"]