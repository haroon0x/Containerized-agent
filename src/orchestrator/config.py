
import os

class Config:
    # Job Manager settings
    AGENT_OUTPUT_DIR = os.getenv("AGENT_OUTPUT_DIR", "/tmp/agent_jobs")
    AGENT_IMAGE = os.getenv("AGENT_IMAGE", "containerized-agent:latest")
    RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", "1"))
    JOBS_FILE = os.path.join(AGENT_OUTPUT_DIR, "jobs.json")
    LOGS_SUBDIR = "logs"
    CONTAINER_MEM_LIMIT = "2g"
    CONTAINER_CPU_PERIOD = 100000
    CONTAINER_CPU_QUOTA = 50000

    # Health Monitor settings
    HEALTH_CHECK_INTERVAL = 30  # seconds
    CPU_WARNING_THRESHOLD = 80.0
    CPU_CRITICAL_THRESHOLD = 95.0
    MEMORY_WARNING_THRESHOLD = 80.0
    MEMORY_CRITICAL_THRESHOLD = 95.0
    DISK_WARNING_THRESHOLD = 85.0
    DISK_CRITICAL_THRESHOLD = 95.0

    # API settings
    API_HOST = "0.0.0.0"
    API_PORT = 8000

config = Config()
