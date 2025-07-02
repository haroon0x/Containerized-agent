# containerized-agent

containerized-agent is a backend system that spins up isolated agent environments inside containers to execute shell commands, run code (Python, TypeScript, etc.), manage files, and control a GUI via xdot. It includes a REST API to schedule tasks, monitor their status, and return results. Designed with sandboxing, scalability, and context management in mind, it’s ideal for building secure coding agents, automation systems, or workflow runners.


---

## ✨ Features

- Run shell and code execution (Python, TypeScript, etc.)
- GUI automation via `xdot` inside a container
- View container in real-time via noVNC
- REST API to schedule tasks and check status
- Context management (beyond token limits)
- Easily extensible, horizontally scalable
- Built with Docker; Firecracker and k8s ready

---

## 📦 API Endpoints

- `POST /schedule`  
  Accepts a task prompt (e.g., "Build a React app") and spawns an agent container/VM.

- `GET /status/:id`  
  Returns the job status and a link to download the final output when ready.

---

## 🚀 Quick Start (WIP)

1. Clone the repo  
2. Run `docker-compose up --build`  
3. Access the noVNC session at [localhost:6080](http://localhost:6080)  
4. Use the API to schedule jobs and monitor them  

> Note: Ensure Docker is installed and supports GUI containers (X11/VNC).

---

## 🧱 Tech Stack

- Python (FastAPI or Flask) for orchestration
- Shell subprocesses for command execution
- Jupyter (optional) for code execution
- xdot + Xvfb + noVNC for GUI
- Docker (or Firecracker) for sandboxing

---


