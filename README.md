# 🚀 Containerized Agent System

> **AI-Powered Task Execution in Isolated Environments**

A practical system for running AI agents in Docker containers that can execute shell commands and Python code based on natural language prompts. Built for developers who want to automate repetitive tasks, prototype ideas quickly, or experiment with AI-driven automation. It primarily uses [alchemystai](https://getalchemystai.com) for the agent andgemini as a fallback.

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

## 🏗️ System Architecture

### High-Level Flow
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

### Detailed System Architecture
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   REST API  │    │   Web UI    │    │   CLI Tool  │    │   Scripts   │ │
│  │   Client    │    │  Dashboard  │    │   Client    │    │   & Bots    │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATOR LAYER                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    FastAPI Orchestrator                            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │
│  │  │   /schedule │  │  /status/   │  │   /jobs     │  │  /cancel/   │ │   │
│  │  │   Endpoint  │  │  Endpoint   │  │  Endpoint   │  │  Endpoint   │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │   │
│  │                                                                       │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │  │                    Job Manager                                 │   │   │
│  │  │  • Job Scheduling    • Container Lifecycle    • Status Tracking│   │   │
│  │  │  • Log Management    • Output Packaging       • Error Handling │   │   │
│  │  └─────────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CONTAINER LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Agent Container                                 │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │
│  │  │   Task      │  │   Shell     │  │   Python    │  │   Result    │ │   │
│  │  │ Analysis    │  │  Command    │  │    Code     │  │ Compilation │ │   │
│  │  │   Node      │  │   Node      │  │    Node     │  │    Node     │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │   │
│  │                                                                       │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │  │                    PocketFlow                                 │   │   │
│  │  │  • Workflow Orchestration    • Node Execution    • Data Flow  │   │   │
│  │  │  • Error Handling            • State Management  • Logging    │   │   │
│  │  └─────────────────────────────────────────────────────────────────┘   │   │
│  │                                                                       │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │  │                    Execution Environment                        │   │   │
│  │  │  • Python 3.11+    • Shell Access    • File System    • Network│   │   │
│  │  │  • Package Manager  • Git Access      • Environment    • Permissions│   │   │
│  │  └─────────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MONITORING LAYER                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   noVNC     │    │   Jupyter   │    │   Log       │    │   Output    │ │
│  │   Server    │    │    Lab      │    │  Streaming  │    │  Storage    │ │
│  │ • Real-time │    │ • Interactive│   │ • Real-time │    │ • ZIP Files │ │
│  │   GUI       │    │   Dev Env   │    │   Logs      │    │ • Downloads │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         INFRASTRUCTURE LAYER                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   Docker    │    │   Volume    │    │   Network   │    │   Security   │ │
│  │  Engine     │    │ Management  │    │  Isolation  │    │   Sandbox    │ │
│  │ • Container │    │ • Persistent│    │ • Port      │    │ • Resource   │ │
│  │   Runtime   │    │   Storage   │    │   Mapping   │    │   Limits     │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow
```
1. CLIENT REQUEST
   └── Natural language prompt sent to /schedule endpoint

2. ORCHESTRATOR PROCESSING
   └── Job Manager creates new job and spawns container

3. AGENT EXECUTION
   └── Task Analysis → Shell Commands → Python Code → Result Compilation

4. MONITORING & OUTPUT
   └── Real-time logs → VNC monitoring → Result packaging → Download links

5. CLEANUP
   └── Container termination → Resource cleanup → Log retention
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
ALCHEMYST_API_KEY=your_alchemyst_api_key_here
AGENT_IMAGE=containerized-agent:latest
AGENT_OUTPUT_DIR=/tmp/agent_jobs
RETENTION_DAYS=1
EOF


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



---



---



---



---



---



---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---


