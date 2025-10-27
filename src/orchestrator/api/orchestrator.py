import logging
import os
import uuid
from typing import Any, Dict
from fastapi import FastAPI, BackgroundTasks, Request, Query, Depends, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse
from src.orchestrator.api.job_manager import job_manager
from schema import ScheduleRequest

logging.basicConfig(level=logging.INFO)

app = FastAPI()

def is_valid_job_id(job_id: str) -> bool:
    try:
        uuid.UUID(job_id)
        return True
    except Exception:
        return False

async def validate_job_id(job_id: str) -> str:
    """
    A FastAPI dependency that checks if a job_id is a valid UUID.
    If not, it raises an HTTPException. Otherwise, it returns the job_id.
    """
    if not is_valid_job_id(job_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job_id format (must be a UUID)",
        )
    return job_id

@app.post("/schedule")
async def schedule_job(req: ScheduleRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Launch a new job as a Docker container using JobManager."""
    job_id = job_manager.launch_job(req.prompt)
    logging.info(f"Scheduled job {job_id} for prompt: {req.prompt}")
    return {"job_id": job_id, "status": "scheduled"}

@app.get("/status/{job_id}")
async def get_status(request: Request, job_id: str = Depends(validate_job_id)) -> Dict[str, Any]:
    """Get the status and output path for a job. If complete, include download and logs links."""
    status = job_manager.get_status(job_id)
    output = job_manager.get_output(job_id) if status == "complete" else None
    base_url = str(request.base_url).rstrip("/")
    download_link = f"{base_url}/download/{job_id}" if output else None
    logs_link = f"{base_url}/logs/{job_id}"
    logging.info(f"Status for job {job_id}: {status}")
    return {
        "job_id": job_id,
        "status": status,
        "output": output,
        "download_link": download_link,
        "logs_link": logs_link
    }

@app.post("/cancel/{job_id}")
async def cancel_job(job_id: str = Depends(validate_job_id)) -> Dict[str, Any]:
    """Cancel a running job. Returns success/failure and updated status."""
    success = job_manager.cancel_job(job_id)
    status = job_manager.get_status(job_id)
    logging.info(f"Cancelled job {job_id}: {success}")
    return {"job_id": job_id, "cancelled": success, "status": status}

@app.get("/jobs")
async def list_jobs() -> Dict[str, Any]:
    """List all jobs and their statuses."""
    jobs = []
    for job_id, job in job_manager.jobs.items():
        jobs.append({
            "job_id": job_id,
            "status": job.get("status"),
            "created": job.get("created"),
            "started": job.get("started"),
            "completed": job.get("completed"),
            "error": job.get("error"),
        })
    logging.info(f"Listing {len(jobs)} jobs.")
    return {"jobs": jobs}

@app.get("/")
async def root() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse(content={"message": "orchestration server is running."})

@app.get("/job/{job_id}")
async def get_job_details(job_id: str = Depends(validate_job_id)) -> Any:
    """Get the full job state/details for a job."""
    job = job_manager.jobs.get(job_id)
    if not job:
        logging.warning(f"Job not found: {job_id}")
        return JSONResponse(status_code=404, content={"error": "Job not found"})
    return job

@app.get("/logs/{job_id}")
async def get_job_logs(job_id: str = Depends(validate_job_id), log_type: str = Query("stdout", enum=["stdout", "stderr"])) -> Any:
    """Get the last 1000 lines and full log for a job (stdout or stderr)."""
    if log_type not in ("stdout", "stderr"):
        logging.warning(f"Invalid log_type: {log_type}")
        return JSONResponse(status_code=400, content={"error": "log_type must be 'stdout' or 'stderr'"})
    logs = job_manager.get_logs(job_id) if log_type == "stdout" else None
    full_log = job_manager.get_full_log(job_id, log_type)
    if logs is None and full_log is None:
        logging.warning(f"Logs not found for job {job_id}")
        return JSONResponse(status_code=404, content={"error": "Logs not found or job does not exist"})
    return {"job_id": job_id, "log_type": log_type, "last_1000_lines": logs, "full_log": full_log}

@app.get("/logs/{job_id}/{log_type}")
async def download_log_file(log_type: str, job_id: str = Depends(validate_job_id)) -> Any:
    """Download the full log file (stdout or stderr) for a job as plain text."""
    if log_type not in ("stdout", "stderr"):
        logging.warning(f"Invalid log_type for download: {log_type}")
        return JSONResponse(status_code=400, content={"error": "log_type must be 'stdout' or 'stderr'"})
    log_file = job_manager.get_log_file(job_id, log_type)
    if not log_file:
        logging.warning(f"Log file not found for job {job_id}, type {log_type}")
        return JSONResponse(status_code=404, content={"error": f"{log_type} log file not found"})
    return FileResponse(log_file, filename=os.path.basename(log_file), media_type="text/plain")

@app.get("/download/{job_id}")
async def download_job_output(job_id: str = Depends(validate_job_id)) -> Any:
    """Download the zipped output file for a completed job."""
    output = job_manager.get_output(job_id)
    if not output or not output.endswith(".zip") or not os.path.exists(output):
        logging.warning(f"Output zip not found for job {job_id}")
        return JSONResponse(status_code=404, content={"error": "Output zip not found or job not complete"})
    return FileResponse(output, filename=os.path.basename(output), media_type="application/zip")
