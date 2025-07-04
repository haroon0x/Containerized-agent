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

### Core API (Minimal Orchestration)

- `POST /schedule`  
  Accepts a task prompt (e.g., "Build a React app") and spawns an agent container/VM. Returns a job ID.
  
  **Example:**
  ```http
  POST /schedule
  Content-Type: application/json
  {
    "prompt": "Build me a todo app in React"
  }
  => { "job_id": "abc123", "status": "scheduled" }
  ```

- `GET /status/:id`  
  Returns the job status and a link to download the final output when ready.
  
  **Example:**
  ```http
  GET /status/abc123
  => {
    "job_id": "abc123",
    "status": "complete",
    "output": "/tmp/agent_jobs/abc123/output.zip",
    "download_link": "http://localhost:8000/download/abc123",
    "logs_link": "http://localhost:8000/logs/abc123"
  }
  ```

### Advanced & Debugging Endpoints

These endpoints are not required for minimal orchestration, but are highly recommended for debugging, monitoring, and extensibility:

- `POST /cancel/{job_id}`  
  Cancel a running job. Returns success/failure and updated status.
  
  **Example:**
  ```http
  POST /cancel/abc123
  => { "job_id": "abc123", "cancelled": true, "status": "cancelled" }
  ```

- `GET /jobs`  
  List all jobs and their statuses.
  
  **Example:**
  ```http
  GET /jobs
  => { "jobs": [
    { "job_id": "abc123", "status": "complete", "created": ..., "started": ..., "completed": ..., "error": null },
    ...
  ]}
  ```

- `GET /job/{job_id}`  
  Returns full job details and metadata (timestamps, error info, etc.).

- `GET /logs/{job_id}`  
  Returns the last 1000 lines and full log for a job (stdout or stderr).

- `GET /logs/{job_id}/{log_type}`  
  Download the full log file (stdout or stderr) for a job as plain text.

- `GET /download/{job_id}`  
  Download the zipped output file for a completed job.

> Advanced endpoints are useful for troubleshooting failed jobs, monitoring job progress, and integrating with UIs or admin tools. They are optional for a minimal system, but strongly recommended for real-world use.

---

## 🛠️ Error Handling & Job Lifecycle
- All endpoints return clear error messages and status codes for missing jobs, failed jobs, or invalid requests.
- Jobs can be scheduled, monitored, cancelled, and their outputs/logs retrieved at any time.
- Completed jobs' outputs are available as zipped downloads; logs are available for debugging.

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


