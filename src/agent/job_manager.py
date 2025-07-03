import docker
import uuid
import os
from threading import Lock
from utils.utils import save_json, load_json
import shutil

# Path where job outputs will be stored (should be a shared/mounted volume in real deployment)
OUTPUT_DIR = "/tmp/agent_jobs"
AGENT_IMAGE = "containerized-agent:latest"  # TODO: Set your built agent image name/tag
RETENTION_DAYS = 7  # Set retention period to 7 days
JOBS_FILE = os.path.join(OUTPUT_DIR, "jobs.json")
LOGS_SUBDIR = "logs"

class JobManager:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.lock = Lock()
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        self.jobs = self._load_jobs()
        self.cleanup_jobs()

    def _save_jobs(self):
        with self.lock:
            save_json(self.jobs, JOBS_FILE)

    def _load_jobs(self):
        jobs = load_json(JOBS_FILE)
        return jobs if jobs is not None else {}

    def launch_job(self, prompt: str) -> str:
        job_id = str(uuid.uuid4())
        output_path = os.path.join(OUTPUT_DIR, job_id)
        os.makedirs(output_path, exist_ok=True)
        logs_path = os.path.join(output_path, LOGS_SUBDIR)
        os.makedirs(logs_path, exist_ok=True)
        try:
            container = self.docker_client.containers.run(
                AGENT_IMAGE,
                detach=True,
                environment={"JOB_PROMPT": prompt, "JOB_ID": job_id},
                volumes={output_path: {"bind": "/workspace/output", "mode": "rw"}},
                name=f"agent_job_{job_id[:8]}",
                mem_limit="2g",  # Resource limits
                cpu_period=100000,
                cpu_quota=50000,  # 0.5 CPU
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
                }
                self._save_jobs()
        except Exception as e:
            with self.lock:
                self.jobs[job_id] = {
                    "container_id": None,
                    "status": "error",
                    "output_path": output_path,
                    "logs_path": logs_path,
                    "error": str(e),
                }
                self._save_jobs()
        return job_id

    def get_status(self, job_id: str) -> str:
        with self.lock:
            job = self.jobs.get(job_id)
        if not job:
            return "not_found"
        if job.get("status") == "error":
            return "error"
        try:
            container = self.docker_client.containers.get(job["container_id"])
            container.reload()
            if container.status == "exited":
                status = "complete"
            elif container.status == "running":
                status = "running"
            else:
                status = container.status
            with self.lock:
                self.jobs[job_id]["status"] = status
                self._save_jobs()
            return status
        except docker.errors.NotFound:
            with self.lock:
                self.jobs[job_id]["status"] = "not_found"
                self.jobs[job_id]["error"] = "Container not found."
                self._save_jobs()
            return "not_found"
        except Exception as e:
            with self.lock:
                self.jobs[job_id]["status"] = "error"
                self.jobs[job_id]["error"] = str(e)
                self._save_jobs()
            return "error"

    def get_output(self, job_id: str):
        with self.lock:
            job = self.jobs.get(job_id)
        if not job:
            return None
        output_dir = job["output_path"]
        zip_path = os.path.join(output_dir, "output.zip")
        # If job is complete and zip does not exist, create it
        if job.get("status") == "complete" and os.path.exists(output_dir):
            if not os.path.exists(zip_path):
                base_name = os.path.splitext(zip_path)[0]  # Remove '.zip' extension
                shutil.make_archive(base_name, 'zip', output_dir)
        if os.path.exists(zip_path):
            return zip_path
        return output_dir

    def get_logs(self, job_id: str):
        with self.lock:
            job = self.jobs.get(job_id)
        if not job or not job.get("container_id"):
            return None
        try:
            container = self.docker_client.containers.get(job["container_id"])
            logs = container.logs(stdout=True, stderr=True, tail=1000)
            return logs.decode("utf-8") if isinstance(logs, bytes) else logs
        except Exception as e:
            return f"Error retrieving logs: {e}"

    def cancel_job(self, job_id: str) -> bool:
        with self.lock:
            job = self.jobs.get(job_id)
        if not job or not job.get("container_id"):
            return False
        try:
            container = self.docker_client.containers.get(job["container_id"])
            container.remove(force=True)
            with self.lock:
                self.jobs[job_id]["status"] = "cancelled"
                self._save_jobs()
            return True
        except Exception:
            return False

    def cleanup_jobs(self):
        import time
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

# TODO: Add persistence (save jobs to disk/db)
# TODO: Add error handling, cleanup, and artifact packaging

# Singleton instance
job_manager = JobManager() 