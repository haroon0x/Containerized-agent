# JobManager Implementation Notes

## Overview
The `JobManager` class is responsible for launching, tracking, and cleaning up jobs (agent containers) in the containerized-agent system. It ensures jobs are reliably managed, persisted, and their outputs are accessible.

---

## Key Features

- **Atomic, Persistent Job Storage:**
  - Jobs are saved to a `jobs.json` file in the output directory (`/tmp/agent_jobs` by default) using atomic writes (temp file + move).
  - All job state changes (launch, status update, cleanup) are persisted, so jobs survive orchestrator restarts.
  - Each job state includes timestamps (`created`, `started`, `completed`, `cancelled`), exit code, and error message if any.

- **Reliable Job Launching and Cancellation:**
  - Jobs are launched as Docker containers with resource limits and tracked by container ID.
  - Jobs can be cancelled, which removes the container and updates the job state with a cancellation timestamp.

- **Status and Output Retrieval:**
  - Users can query job status at any time.
  - When a job is complete, the output directory is zipped and made available for download.

- **Log Retrieval:**
  - Logs (stdout/stderr) for each job can be retrieved for debugging.

- **Automatic Cleanup:**
  - Exited, errored, or cancelled containers are removed from Docker.
  - Old job output directories (older than 7 days) are deleted to save space.
  - Cleanup runs on startup and can be triggered manually.

---

## Job State Fields
Each job in `jobs.json` includes:
- `container_id`: Docker container ID
- `status`: Job status (`running`, `complete`, `error`, `cancelled`, etc.)
- `output_path`: Path to job output directory
- `logs_path`: Path to job logs directory
- `error`: Error message if any
- `created`: Timestamp when job was created
- `started`: Timestamp when job started
- `completed`: Timestamp when job completed
- `cancelled`: Timestamp when job was cancelled
- `exit_code`: Container exit code (if available)

### Example Job State
```json
{
  "container_id": "abcdef123456",
  "status": "complete",
  "output_path": "/tmp/agent_jobs/1234abcd",
  "logs_path": "/tmp/agent_jobs/1234abcd/logs",
  "error": null,
  "created": 1718000000.0,
  "started": 1718000001.0,
  "completed": 1718000020.0,
  "cancelled": null,
  "exit_code": 0
}
```

---

## Usage

- **Launching a Job:**
  - `launch_job(prompt)` creates a new container, tracks its state, and persists the job info.
- **Checking Status:**
  - `get_status(job_id)` returns the current status (`running`, `complete`, `error`, etc.) and updates the job state.
- **Getting Output:**
  - `get_output(job_id)` returns the path to the zipped output if the job is complete, or the output directory otherwise.
- **Getting Logs:**
  - `get_logs(job_id)` returns the last 1000 lines of logs for the job.
- **Cancelling a Job:**
  - `cancel_job(job_id)` removes the container and marks the job as cancelled.
- **Cleanup:**
  - `cleanup_jobs()` removes old containers and output directories.

---

## Design Considerations

- **Thread Safety:**
  - All job state changes are protected by a lock to ensure thread safety.
- **Extensibility:**
  - The manager can be extended to support other backends (e.g., Firecracker, Kubernetes) or more advanced artifact management.
- **Security:**
  - Output directories should be sandboxed and not expose sensitive host data.

---

## Future Improvements
- Add log file collection and API for log download
- Support for job prioritization and resource quotas
- Integration with distributed job stores (e.g., Redis, DB)
- More granular artifact packaging (select files, logs, etc.) 