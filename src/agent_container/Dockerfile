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

# Install uv globally
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set uv environment variables for optimal performance
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

# Create a non-root user
RUN adduser -D -s /bin/bash agentuser \
    && echo 'agentuser ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

WORKDIR /home/agentuser/workspace
RUN chown -R agentuser:agentuser /home/agentuser
RUN mkdir -p /home/agentuser/workspace/output && chown -R agentuser:agentuser /home/agentuser/workspace/output
RUN ln -s /home/agentuser/workspace /workspace

# Copy project files
COPY pyproject.toml /home/agentuser/workspace/
COPY src/ /home/agentuser/workspace/src/

# Install dependencies and project using uv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev

# Install noVNC after Python environment is ready
RUN git clone https://github.com/novnc/noVNC.git /opt/noVNC \
    && git clone https://github.com/novnc/websockify /opt/noVNC/utils/websockify

COPY src/agent_container/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY src/agent_container/supervisord.conf /etc/supervisord.conf

USER agentuser

EXPOSE 6080 8888 8000

# Use entrypoint for job execution, supervisor for development
ENTRYPOINT ["/entrypoint.sh"]
