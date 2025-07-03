# JobManager Implementation Notes

## Overview
The `JobManager` class is responsible for launching, tracking, and cleaning up jobs (agent containers) in the containerized-agent system. It ensures jobs are reliably managed, persisted, and their outputs are accessible.

---

## Key Features

- **Persistent Job Storage:**
  - Jobs are saved to a `jobs.json` file in the output directory (`/tmp/agent_jobs` by default).
  - All job state changes (launch, status update, cleanup) are persisted, so jobs survive orchestrator restarts.

- **Error Handling:**
  - If a container fails to start or an error occurs, the job is marked as `error` and the error message is stored.
  - Errors during status checks are also recorded in the job state.

- **Cleanup:**
  - Exited or errored containers are removed from Docker.
  - Old job output directories (older than 7 days) are deleted to save space.
  - Cleanup runs on startup and can be triggered manually.

- **Artifact Packaging:**
  - When a job completes, its output directory is zipped (`output.zip`).
  - The API returns the path to the zip file for download if available.

---

## Usage

- **Launching a Job:**
  - `launch_job(prompt)` creates a new container, tracks its state, and persists the job info.
- **Checking Status:**
  - `get_status(job_id)` returns the current status (`running`, `complete`, `error`, etc.) and updates the job state.
- **Getting Output:**
  - `get_output(job_id)` returns the path to the zipped output if the job is complete, or the output directory otherwise.
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

## Example Directory Structure

```
/tmp/agent_jobs/
  jobs.json
  <job_id_1>/
    ...
    output.zip
  <job_id_2>/
    ...
```

---

## Future Improvements
- Add log file collection and API for log download
- Support for job prioritization and resource quotas
- Integration with distributed job stores (e.g., Redis, DB)
- More granular artifact packaging (select files, logs, etc.) 