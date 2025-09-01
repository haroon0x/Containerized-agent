import logging
import docker
import uuid
import os
import json
import shutil
import time
import tempfile
from threading import Lock
from typing import Any, Dict, Optional
from src.orchestrator.utils import save_json, load_json

logging.basicConfig(level=logging.INFO)

OUTPUT_DIR = os.getenv("AGENT_OUTPUT_DIR", "/tmp/agent_jobs")
AGENT_IMAGE = os.getenv("AGENT_IMAGE", "containerized-agent:latest")
RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", "1"))
JOBS_FILE = os.path.join(OUTPUT_DIR, "jobs.json")
LOGS_SUBDIR = "logs"

class JobManager:
    def __init__(self) -> None:
        """Initialize the JobManager with Docker client and job state."""
        self.docker_client = docker.from_env()
        self.lock = Lock()
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        self.jobs: Dict[str, Any] = self._load_jobs()
        self.cleanup_jobs()

    def _save_jobs(self) -> None:
        """Atomically save jobs to disk."""
        with self.lock:
            tmp_fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(JOBS_FILE), prefix="jobs_", suffix=".json")
            try:
                with os.fdopen(tmp_fd, 'w', encoding='utf-8') as f:
                    json.dump(self.jobs, f, indent=2, ensure_ascii=False)
                os.replace(tmp_path, JOBS_FILE)
            except Exception as e:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                logging.error(f"Failed to save jobs: {e}")
                raise e

    def _load_jobs(self) -> Dict[str, Any]:
        """Load jobs from disk."""
        jobs = load_json(JOBS_FILE)
        return jobs if jobs is not None else {}

    def launch_job(self, prompt: str) -> str:
        """Launch a new agent job as a Docker container."""
        job_id = str(uuid.uuid4())
        output_path = os.path.join(OUTPUT_DIR, job_id)
        os.makedirs(output_path, exist_ok=True)
        logs_path = os.path.join(output_path, LOGS_SUBDIR)
        os.makedirs(logs_path, exist_ok=True)
        created_time = time.time()
        try:
            container = self.docker_client.containers.run(
                AGENT_IMAGE,
                detach=True,
                environment={"JOB_PROMPT": prompt, "JOB_ID": job_id},
                volumes={output_path: {"bind": "/workspace/output", "mode": "rw"}},
                name=f"agent_job_{job_id[:8]}",
                mem_limit="2g",
                cpu_period=100000,
                cpu_quota=50000,
                stdout=True,
                stderr=True,
                log_config=docker.types.LogConfig(type=docker.types.LogConfig.types.JSON),
            )
            with self.lock:
                self.jobs[job_id] = {
                    "container_id": container.id,
                    "status": "running",
                    "output_path": output_path,
                    "logs_path": logs_path,
                    "error": None,
                    "created": created_time,
                    "started": time.time(),
                    "completed": None,
                    "cancelled": None,
                    "exit_code": None,
                }
                self._save_jobs()
            logging.info(f"Launched job {job_id} with container {container.id}")
        except Exception as e:
            with self.lock:
                self.jobs[job_id] = {
                    "container_id": None,
                    "status": "error",
                    "output_path": output_path,
                    "logs_path": logs_path,
                    "error": str(e),
                    "created": created_time,
                    "started": None,
                    "completed": None,
                    "cancelled": None,
                    "exit_code": None,
                }
                self._save_jobs()
            logging.error(f"Failed to launch job {job_id}: {e}")
        return job_id

    def get_status(self, job_id: str) -> str:
        """Get the status of a job."""
        with self.lock:
            job = self.jobs.get(job_id)
        if not job:
            return "not_found"
        if job.get("status") == "error":
            return "error"
        try:
            container = self.docker_client.containers.get(job["container_id"])
            container.reload()
            exit_code = None
            if container.status == "exited":
                status = "complete"
                exit_code = container.attrs.get("State", {}).get("ExitCode")
                completed_time = time.time()
            elif container.status == "running":
                status = "running"
                completed_time = None
            else:
                status = container.status
                completed_time = None
            with self.lock:
                self.jobs[job_id]["status"] = status
                self.jobs[job_id]["exit_code"] = exit_code
                if completed_time and not self.jobs[job_id]["completed"]:
                    self.jobs[job_id]["completed"] = completed_time
                self._save_jobs()
            return status
        except docker.errors.NotFound:
            with self.lock:
                self.jobs[job_id]["status"] = "not_found"
                self.jobs[job_id]["error"] = "Container not found."
                self._save_jobs()
            logging.warning(f"Container not found for job {job_id}")
            return "not_found"
        except Exception as e:
            with self.lock:
                self.jobs[job_id]["status"] = "error"
                self.jobs[job_id]["error"] = str(e)
                self._save_jobs()
            logging.error(f"Error getting status for job {job_id}: {e}")
            return "error"

    def get_output(self, job_id: str) -> Optional[str]:
        """Get the output zip file for a completed job."""
        with self.lock:
            job = self.jobs.get(job_id)
        if not job:
            return None
        output_dir = job["output_path"]
        zip_path = os.path.join(output_dir, "output.zip")
        if job.get("status") == "complete" and os.path.exists(output_dir):
            if not os.path.exists(zip_path):
                base_name = os.path.splitext(zip_path)[0]
                shutil.make_archive(base_name, 'zip', output_dir)
            if os.path.exists(zip_path):
                return zip_path
        return None

    def get_logs(self, job_id: str) -> Optional[str]:
        """Get the last 1000 lines of stdout logs for a job."""
        return self.get_full_log(job_id, "stdout")

    def get_log_file(self, job_id: str, log_type: str = "stdout") -> Optional[str]:
        """Return the path to the log file (stdout or stderr) for the job, if available."""
        with self.lock:
            job = self.jobs.get(job_id)
        if not job:
            return None
        logs_dir = job.get("logs_path")
        if not logs_dir or not os.path.exists(logs_dir):
            return None
        if log_type not in ("stdout", "stderr"):
            return None
        log_file = os.path.join(logs_dir, f"{log_type}.log")
        return log_file if os.path.exists(log_file) else None

    def get_full_log(self, job_id: str, log_type: str = "stdout") -> Optional[str]:
        """Return the full contents of the log file (stdout or stderr) for the job, if available."""
        log_file = self.get_log_file(job_id, log_type)
        if not log_file:
            return None
        try:
            with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except Exception as e:
            logging.error(f"Error reading log file for job {job_id}: {e}")
            return f"Error reading log file: {e}"

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job by removing its container."""
        with self.lock:
            job = self.jobs.get(job_id)
        if not job or not job.get("container_id"):
            return False
        try:
            container = self.docker_client.containers.get(job["container_id"])
            container.remove(force=True)
            with self.lock:
                self.jobs[job_id]["status"] = "cancelled"
                self.jobs[job_id]["cancelled"] = time.time()
                self._save_jobs()
            logging.info(f"Cancelled job {job_id}")
            return True
        except Exception as e:
            logging.error(f"Failed to cancel job {job_id}: {e}")
            return False

    def cleanup_jobs(self) -> None:
        """Clean up old jobs and containers based on retention policy."""
        with self.lock:
            to_remove = []
            for job_id, job in self.jobs.items():
                if job.get("container_id") and job.get("status") in ("complete", "error", "exited", "cancelled"):
                    try:
                        container = self.docker_client.containers.get(job["container_id"])
                        container.remove(force=True)
                    except Exception:
                        pass
                if os.path.exists(job["output_path"]):
                    try:
                        mtime = os.path.getmtime(job["output_path"])
                        if time.time() - mtime > RETENTION_DAYS * 24 * 3600:
                            shutil.rmtree(job["output_path"])
                            to_remove.append(job_id)
                    except Exception:
                        pass
            for job_id in to_remove:
                self.jobs.pop(job_id, None)
            self._save_jobs()

job_manager = JobManager() 