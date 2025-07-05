# Containerized Agent System - Complete Testing Instructions

## 🚀 Quick Start Guide

This guide will walk you through setting up and testing the complete containerized agent system on Ubuntu with Docker.

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

## 🔧 Setup Instructions

### Step 1: Clone and Navigate to Project
```bash
# Navigate to your project directory
cd /path/to/your/containerized-agent

# Verify you're in the right directory
ls -la
# You should see: docker-compose.yml, requirements.txt, src/, etc.
```

### Step 2: Set Up Environment Variables
```bash
# Create .env file for API keys
cat > .env << EOF
GEMINI_API_KEY=your_gemini_api_key_here
AGENT_IMAGE=containerized-agent:latest
AGENT_OUTPUT_DIR=/tmp/agent_jobs
RETENTION_DAYS=1
EOF

# Replace 'your_gemini_api_key_here' with your actual Gemini API key
# Get one from: https://makersuite.google.com/app/apikey
```

### Step 3: Build and Start the System
```bash
# Build all containers (this may take 5-10 minutes on first run)
docker-compose up --build -d

# Check if containers are running
docker-compose ps

# View logs to ensure everything started correctly
docker-compose logs -f
```

### Step 4: Verify Services Are Running
```bash
# Check orchestrator API health
curl http://localhost:8000/

# Expected response: {"message": "orchestraion server is running."}

# Check if agent container is built
docker images | grep containerized-agent
```

---

## 🧪 Testing Instructions

### Test 1: Basic API Health Check
```bash
# Test the orchestrator API
curl -X GET http://localhost:8000/

# Expected output:
# {"message": "orchestraion server is running."}
```

### Test 2: Schedule a Simple Job
```bash
# Schedule a test job
curl -X POST http://localhost:8000/schedule \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is 2 + 2? Answer in one sentence."}'

# Expected output:
# {"job_id": "uuid-here", "status": "scheduled"}
```

### Test 3: Monitor Job Status
```bash
# Replace JOB_ID with the actual job ID from previous step
JOB_ID="your-job-id-here"

# Check job status
curl http://localhost:8000/status/$JOB_ID

# Monitor status until completion (run this multiple times)
while true; do
  curl -s http://localhost:8000/status/$JOB_ID | jq .
  sleep 5
done
```

### Test 4: List All Jobs
```bash
# List all jobs
curl http://localhost:8000/jobs | jq .
```

### Test 5: Download Job Results
```bash
# Download job output (when job is complete)
curl -O http://localhost:8000/download/$JOB_ID

# View job logs
curl http://localhost:8000/logs/$JOB_ID | jq .
```

### Test 6: Run Automated Test Script
```bash
# Install Python dependencies locally for testing
pip install requests

# Run the automated test script
python test_system.py
```

---

## 🌐 Access Web Interfaces

### 1. Orchestrator API Documentation
- **URL**: http://localhost:8000/docs
- **Purpose**: Interactive API documentation (Swagger UI)

### 2. noVNC (GUI Access)
- **URL**: http://localhost:6080
- **Purpose**: Access the agent container's GUI environment
- **Note**: May take a moment to load

### 3. Jupyter Lab
- **URL**: http://localhost:8888
- **Purpose**: Interactive development environment
- **Note**: No authentication required in container

---

## 🔍 Troubleshooting

### Common Issues and Solutions

#### Issue 1: Docker Compose Build Fails
```bash
# Clean up and rebuild
docker-compose down
docker system prune -f
docker-compose up --build
```

#### Issue 2: Port Already in Use
```bash
# Check what's using the ports
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :6080

# Kill processes if needed
sudo kill -9 <PID>
```

#### Issue 3: Container Won't Start
```bash
# Check container logs
docker-compose logs orchestrator
docker-compose logs agent-builder

# Check Docker daemon
sudo systemctl status docker
```

#### Issue 4: API Key Issues
```bash
# Verify .env file exists and has correct API key
cat .env

# Restart containers after changing .env
docker-compose down
docker-compose up -d
```

#### Issue 5: Memory Issues
```bash
# Check available memory
free -h

# Increase Docker memory limit if needed
# Edit /etc/docker/daemon.json and restart Docker
```

---

## 📊 Monitoring and Debugging

### View Real-time Logs
```bash
# View all container logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f orchestrator
docker-compose logs -f agent-builder
```

### Check Container Status
```bash
# List running containers
docker ps

# Check container resource usage
docker stats
```

### Access Container Shell
```bash
# Access orchestrator container
docker-compose exec orchestrator bash

# Access agent container
docker-compose exec agent-builder bash
```

---

## 🧹 Cleanup

### Stop the System
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes all job data)
docker-compose down -v
```

### Clean Docker Resources
```bash
# Remove unused containers, networks, images
docker system prune -a

# Remove specific images
docker rmi containerized-agent:latest
```

---

## 📈 Performance Testing

### Test Multiple Jobs
```bash
# Schedule multiple jobs simultaneously
for i in {1..5}; do
  curl -X POST http://localhost:8000/schedule \
    -H "Content-Type: application/json" \
    -d "{\"prompt\": \"Test job $i: What is $i + $i?\"}"
done
```

### Monitor Resource Usage
```bash
# Watch container resource usage
watch docker stats

# Check job queue
curl http://localhost:8000/jobs | jq '.jobs | length'
```

---

## 🎯 Success Criteria

Your system is working correctly if:

✅ **Health Check**: `curl http://localhost:8000/` returns success  
✅ **Job Scheduling**: Can schedule jobs and get job IDs  
✅ **Job Completion**: Jobs complete and return results  
✅ **File Downloads**: Can download job output ZIP files  
✅ **Log Access**: Can access job logs via API  
✅ **GUI Access**: noVNC loads at http://localhost:6080  
✅ **Jupyter Access**: Jupyter Lab loads at http://localhost:8888  

---

## 🚀 Next Steps After Testing

1. **Extend Agent Capabilities**: Add more nodes to `src/agent/nodes.py`
2. **Add Authentication**: Implement API key authentication
3. **Create Web UI**: Build a dashboard for job management
4. **Add Job Templates**: Predefined job types
5. **Implement Queuing**: Better resource management
6. **Add Monitoring**: Prometheus/Grafana integration

---

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review container logs: `docker-compose logs`
3. Verify Docker installation: `docker --version`
4. Check system resources: `free -h`, `df -h`
5. Ensure ports are available: `netstat -tulpn`

---

**Happy Testing! 🎉** 