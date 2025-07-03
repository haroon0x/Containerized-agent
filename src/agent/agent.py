from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid, os, subprocess
from job_manager import job_manager

app = FastAPI()

@app.get("/")
async def root():
    return JSONResponse(content={"message": "Agent API is running."})

class ScheduleRequest(BaseModel):
    prompt: str

@app.post("/schedule")
async def schedule_job(req: ScheduleRequest, background_tasks: BackgroundTasks):
    """
    Launch a new job as a Docker container using JobManager.
    """
    job_id = job_manager.launch_job(req.prompt)
    return {"job_id": job_id, "status": "scheduled"}

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    """
    Get the status and output path for a job.
    """
    status = job_manager.get_status(job_id)
    output = job_manager.get_output(job_id) if status == "complete" else None
    return {"job_id": job_id, "status": status, "output": output}
