# 🚀 Containerized Agent System

> **AI-Powered Task Execution in Isolated Environments**

A practical system for running AI agents in Docker containers that can execute shell commands and Python code based on natural language prompts. Built for developers who want to automate repetitive tasks, prototype ideas quickly, or experiment with AI-driven automation.

---

## 🎯 What This Actually Does

This system takes your natural language request (like "Create a Python script that calculates fibonacci numbers") and:

1. **Analyzes** your request using AI to break it down into executable steps
2. **Executes** shell commands and Python code in an isolated container
3. **Compiles** the results and packages everything for download
4. **Provides** real-time monitoring through logs and GUI access

### Current Capabilities
- ✅ **Shell Command Execution**: Run any shell command in isolated containers
- ✅ **Python Code Execution**: Execute Python scripts with full environment
- ✅ **Task Analysis**: AI breaks down complex requests into executable steps
- ✅ **Real-time Monitoring**: Watch execution through logs and VNC
- ✅ **Result Packaging**: Download completed work as ZIP files
- ✅ **Job Management**: Schedule, monitor, and cancel tasks via REST API

### What It's Not (Yet)
- ❌ **Full GUI Automation**: While VNC is available, complex GUI automation is limited
- ❌ **Multi-language Support**: Currently focused on Python and shell commands
- ❌ **Production Deployment**: This is a research/development tool, not production-ready
- ❌ **Advanced AI Reasoning**: Uses basic task analysis, not complex reasoning

---

## 🏗️ How It Works

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Your Request  │    │   Orchestrator   │    │  Agent Container │
│                 │    │   (FastAPI)      │    │                 │
│ "Build a React  │◄──►│ • Job Management │◄──►│ • Task Analysis │
│  app"           │    │ • Container Mgmt │    │ • Shell Commands│
│                 │    │ • API Gateway    │    │ • Python Code   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   noVNC Server   │
                       │ • Real-time GUI  │
                       │ • Live Monitoring│
                       └──────────────────┘
```

### The Flow
1. **Task Analysis**: AI analyzes your prompt and creates a list of actions
2. **Shell Execution**: Runs shell commands (npm install, git clone, etc.)
3. **Python Execution**: Executes Python code for data processing or scripting
4. **Result Compilation**: Packages everything into a downloadable ZIP

---

## 🚀 Quick Start

### 1. **Clone & Setup**
```bash
git clone <your-repo-url>
cd containerized-agent

# Create environment file
cat > .env << EOF
GEMINI_API_KEY=your_gemini_api_key_here
AGENT_IMAGE=containerized-agent:latest
AGENT_OUTPUT_DIR=/tmp/agent_jobs
RETENTION_DAYS=1
EOF
```

### 2. **Launch the System**
```bash
docker-compose up --build -d
```

### 3. **Test with a Simple Task**
```bash
# Health check
curl http://localhost:8000/

# Try a simple task
curl -X POST http://localhost:8000/schedule \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a Python script that prints hello world"}'

# Get your job ID and check status
curl http://localhost:8000/status/{job_id}
```

### 4. **Access the Interfaces**
- **API Docs**: http://localhost:8000/docs
- **Live GUI**: http://localhost:6080 (watch your agent work!)
- **Jupyter Lab**: http://localhost:8888

---

## 📡 API Reference

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /schedule` | Schedule a new task | `{"prompt": "your task description"}` |
| `GET /status/{id}` | Check job status | Returns status and download links |
| `GET /jobs` | List all jobs | See all scheduled/completed tasks |
| `POST /cancel/{id}` | Cancel running job | Stop a job in progress |

### Example Usage
```bash
# Schedule a task
curl -X POST http://localhost:8000/schedule \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a simple web scraper in Python"}'

# Check status
curl http://localhost:8000/status/abc123

# Download results (when complete)
curl -O http://localhost:8000/download/abc123
```

---

## 🎯 Real Use Cases

### **Development & Prototyping**
- **Quick Scripts**: "Create a Python script that processes CSV files"
- **Data Analysis**: "Download stock data and create a simple chart"
- **Web Scraping**: "Scrape a website and save the data to JSON"
- **File Processing**: "Convert all images in a folder to thumbnails"

### **Learning & Experimentation**
- **Code Examples**: "Show me how to use pandas for data analysis"
- **Algorithm Implementation**: "Implement quicksort in Python"
- **API Testing**: "Create a script to test a REST API"

### **Automation Tasks**
- **File Organization**: "Sort files by type and create folders"
- **Data Cleaning**: "Clean and validate a dataset"
- **Report Generation**: "Generate a summary report from log files"

---

## 🛠️ Technology Stack

### **Core Components**
- **FastAPI**: REST API for job management
- **Docker**: Container isolation and execution
- **Google Gemini**: AI for task analysis and execution
- **PocketFlow**: Workflow orchestration framework

### **Execution Environment**
- **Python 3.11+**: Primary execution environment
- **Shell Commands**: Full shell access in containers
- **noVNC**: Real-time GUI monitoring
- **Jupyter Lab**: Interactive development environment

### **Infrastructure**
- **Docker Compose**: Multi-service orchestration
- **Volume Management**: Persistent job storage
- **Logging**: Comprehensive execution tracking

---

## 🔧 Configuration

### **Environment Variables**
```bash
# Required
GEMINI_API_KEY=your_api_key_here

# Optional (with defaults)
AGENT_IMAGE=containerized-agent:latest
AGENT_OUTPUT_DIR=/tmp/agent_jobs
RETENTION_DAYS=1
```

### **Resource Limits**
```yaml
# In docker-compose.yml
services:
  orchestrator:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
```

---

## 🚨 Troubleshooting

### **Common Issues**

#### **Container Won't Start**
```bash
# Check Docker daemon
sudo systemctl status docker

# Clean and rebuild
docker-compose down
docker system prune -f
docker-compose up --build
```

#### **API Connection Issues**
```bash
# Check if ports are free
sudo netstat -tulpn | grep :8000

# View container logs
docker-compose logs orchestrator
```

#### **Job Stuck in "Scheduled"**
```bash
# Check agent container logs
docker-compose logs agent-builder

# Verify API key is set
docker-compose exec orchestrator env | grep GEMINI
```

---

## 🔮 Future Development

### **Short-term Goals**
- [ ] **Better Error Handling**: More informative error messages
- [ ] **Job Templates**: Predefined task types
- [ ] **Web UI**: Dashboard for job management
- [ ] **Authentication**: API key protection
- [ ] **Job Queuing**: Better resource management

### **Long-term Vision**
- [ ] **Multi-language Support**: JavaScript, Go, Rust execution
- [ ] **Advanced AI Reasoning**: More sophisticated task analysis
- [ ] **GUI Automation**: Full desktop automation capabilities
- [ ] **Distributed Execution**: Run across multiple nodes
- [ ] **Plugin System**: Extensible agent capabilities

---

## 🤝 Contributing

This is a research project focused on exploring AI-driven automation. We welcome contributions that help improve:

- **Task Analysis**: Better AI prompt engineering
- **Execution Nodes**: New types of task execution
- **Error Handling**: More robust failure recovery
- **Documentation**: Better guides and examples
- **Testing**: More comprehensive test coverage

### **Getting Started**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Commit with clear messages: `git commit -m "Add amazing feature"`
5. Push and create a pull request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google Gemini Team**: For providing the AI capabilities
- **Docker Community**: For containerization technology
- **FastAPI Team**: For the excellent web framework
- **PocketFlow**: For the workflow orchestration framework

---

## 📞 Support & Community

- **GitHub Issues**: [Report bugs or request features](https://github.com/your-repo/issues)
- **Discussions**: [Join the community](https://github.com/your-repo/discussions)
- **Documentation**: [Comprehensive guides](https://docs.your-project.com)

---

## ⭐ Star This Project

If this project helps you explore AI automation or build interesting things, please give it a star! It motivates us to keep improving and adding new features.

---

**Ready to experiment with AI-driven automation?** 🚀

*Start exploring the future of intelligent task execution today.*


