# Containerized Agent System - Complete Testing Instructions

## 🚀 Quick Start Guide

This guide will walk you through setting up and testing the containerized agent system on Ubuntu with Docker. You can either run the webdev_agent in isolation or use docker-compose to run the complete system.

---

## 📋 Prerequisites

### 1. System Requirements
- Ubuntu 20.04+ (you have this on VM)
- Docker installed and running
- Git installed
- At least 4GB RAM available
- Internet connection for downloading images

### 2. Verify Docker Installation
```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker-compose --version

# Verify Docker is running
sudo systemctl status docker

# If Docker is not running, start it:
sudo systemctl start docker
sudo systemctl enable docker
```

---

## 🖥️ Running the WebDev Agent in Isolation

### 1. Build the WebDev Agent Docker Image
```bash
# Navigate to the project directory
cd Containerized-agent

# Build the webdev_agent Docker image
docker build -t webdev-agent:latest -f src/agent_containers/webdev_agent/Dockerfile .
```

### 2. Run the WebDev Agent Container
```bash
# Create an output directory on your host machine
mkdir -p ./output
chmod 777 ./output

# Run the container with your job prompt
docker run -it --rm \
  -e JOB_PROMPT="Create a simple React application with a counter component" \
  -e GEMINI_API_KEY="your_gemini_api_key" \
  -p 6080:6080 -p 8888:8888 -p 8000:8000 \
  -v $(pwd)/output:/workspace/output \
  webdev-agent:latest
```

### 3. Access the WebDev Agent
- VNC Interface: Open your browser and navigate to `http://localhost:6080`
- Web Application (if created): `http://localhost:8000`

---

## 🔄 Running the Complete System with Docker Compose

### 1. Set Up Environment Variables
```bash
# Create a .env file in the project root directory
echo "GEMINI_API_KEY=your_gemini_api_key" > .env
```

### 2. Build and Start All Services
```bash
# Navigate to the project directory
cd Containerized-agent

# Build and start all services in detached mode
docker-compose up --build -d
```

### 3. Access the Services
- Orchestrator API: `http://localhost:8000`
- General Agent VNC Interface: `http://localhost:6080`
- Jupyter Lab Interface: `http://localhost:8888`

### 4. Submit a Job to the Orchestrator
```bash
# Submit a job using curl
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a simple React application with a counter component", "agent_type": "general"}'
```

### 5. Monitor and Manage Containers
```bash
# View logs for all services
docker-compose logs -f

# View logs for a specific service
docker-compose logs -f orchestrator

# Stop all services
docker-compose down
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Conflicts
If you encounter port conflicts, you can modify the port mappings in the `docker-compose.yml` file or when running the container:
```bash
# Example: Change host port from 6080 to 6081
docker run -it --rm -e JOB_PROMPT="Your prompt" -p 6081:6080 webdev-agent:latest
```

#### 2. Permission Issues with Output Directory
If you encounter permission issues with the output directory:
```bash
# Fix permissions on the output directory
sudo chown -R 1000:1000 ./output
```

#### 3. Container Exits Immediately
Check the logs for error messages:
```bash
# For individual container
docker logs <container_id>

# For docker-compose services
docker-compose logs orchestrator
```

#### 4. API Key Issues
Ensure your Gemini API key is correctly set in the environment variables or .env file.

---
