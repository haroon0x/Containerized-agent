import pytest
import requests
import uuid
import time

BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="session")
def schedule_job():
    resp = requests.post(f"{BASE_URL}/schedule", json={"prompt": "echo Hello World"})
    assert resp.status_code == 200
    data = resp.json()
    assert "job_id" in data
    return data["job_id"]

def test_root():
    resp = requests.get(f"{BASE_URL}/")
    assert resp.status_code == 200
    assert "message" in resp.json()

def test_schedule():
    resp = requests.post(f"{BASE_URL}/schedule", json={"prompt": "test"})
    assert resp.status_code == 200
    data = resp.json()
    assert "job_id" in data and "status" in data

def test_status_invalid():
    resp = requests.get(f"{BASE_URL}/status/not-a-uuid")
    assert resp.status_code == 400
    assert "error" in resp.json()

def test_status(schedule_job):
    job_id = schedule_job
    for _ in range(10):
        resp = requests.get(f"{BASE_URL}/status/{job_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["job_id"] == job_id
        assert "status" in data
        if data["status"] == "complete":
            break
        time.sleep(1)

def test_jobs():
    resp = requests.get(f"{BASE_URL}/jobs")
    assert resp.status_code == 200
    assert "jobs" in resp.json()

def test_job_details(schedule_job):
    job_id = schedule_job
    resp = requests.get(f"{BASE_URL}/job/{job_id}")
    assert resp.status_code == 200
    assert "status" in resp.json() or "container_id" in resp.json()

def test_cancel(schedule_job):
    job_id = schedule_job
    resp = requests.post(f"{BASE_URL}/cancel/{job_id}")
    assert resp.status_code == 200
    assert "cancelled" in resp.json()

def test_logs(schedule_job):
    job_id = schedule_job
    resp = requests.get(f"{BASE_URL}/logs/{job_id}")
    assert resp.status_code in (200, 404, 400)

def test_download(schedule_job):
    job_id = schedule_job
    resp = requests.get(f"{BASE_URL}/download/{job_id}")
    assert resp.status_code in (200, 404, 400)

def test_logs_invalid():
    resp = requests.get(f"{BASE_URL}/logs/not-a-uuid")
    assert resp.status_code == 400
    assert "error" in resp.json()

def test_download_invalid():
    resp = requests.get(f"{BASE_URL}/download/not-a-uuid")
    assert resp.status_code == 400
    assert "error" in resp.json() 