# Containerized Agent System

> AI-powered task execution in isolated environments

A system for running AI agents in Docker containers that execute shell commands and Python code based on natural language prompts. Built for developers who want to automate tasks, prototype ideas, or experiment with AI-driven automation securely.

## Capabilities

- **Isolated Execution**: All code runs in sandboxed containers
- **Shell & Python**: Execute commands and scripts safely
- **Real-time Monitoring**: Watch execution through logs and VNC
- **Result Packaging**: Download completed work as ZIP files
- **Job Management**: Schedule, monitor, and cancel tasks via REST API

## Architecture

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

## Components

- **Orchestrator**: FastAPI service managing job lifecycle and containers
- **Agent Container**: Debian-based environment running Gemini AI agent
- **Monitoring**: noVNC, Jupyter Lab, and log streaming



## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/schedule` | POST | Schedule a new task |
| `/status/{id}` | GET | Check job status |
| `/jobs` | GET | List all jobs |
| `/cancel/{id}` | POST | Cancel a job |
| `/download/{id}` | GET | Download results |

## Security

- Isolated containers with resource limits
- Non-root user execution
- Volume and network isolation

