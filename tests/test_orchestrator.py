import pytest
import requests
import time
import uuid

BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="session")
def scheduled_job():
    resp = requests.post(f"{BASE_URL}/schedule", json={"prompt": "echo Hello World"})
    assert resp.status_code == 200, resp.text
    job_id = resp.json()["job_id"]
    yield job_id


def test_poll_status_until_complete(scheduled_job):
    job_id = scheduled_job
    for _ in range(30):
        status_resp = requests.get(f"{BASE_URL}/status/{job_id}")
        assert status_resp.status_code == 200, status_resp.text
        status = status_resp.json()["status"]
        if status == "complete":
            break
        time.sleep(2)
    else:
        pytest.fail("Job did not complete in time.")

def test_download_output(scheduled_job):
    job_id = scheduled_job
    # Wait for job to complete
    for _ in range(30):
        status = requests.get(f"{BASE_URL}/status/{job_id}").json()["status"]
        if status == "complete":
            break
        time.sleep(2)
    download_resp = requests.get(f"{BASE_URL}/download/{job_id}")
    assert download_resp.status_code == 200, download_resp.text
    assert download_resp.headers["content-type"] == "application/zip"

def test_fetch_logs(scheduled_job):
    job_id = scheduled_job
    logs_resp = requests.get(f"{BASE_URL}/logs/{job_id}")
    assert logs_resp.status_code == 200, logs_resp.text
    logs = logs_resp.json()["last_1000_lines"]
    assert isinstance(logs, str)
    assert "Hello" in logs or "hello" in logs.lower()

def test_cancel_job(scheduled_job):
    job_id = scheduled_job
    cancel_resp = requests.post(f"{BASE_URL}/cancel/{job_id}")
    assert cancel_resp.status_code == 200
    data = cancel_resp.json()
    assert data["job_id"] == job_id
    assert "cancelled" in data

def test_error_cases():
    invalid_id = "not-a-uuid"
    err_resp = requests.get(f"{BASE_URL}/status/{invalid_id}")
    assert err_resp.status_code == 400
    random_uuid = str(uuid.uuid4())
    err_resp2 = requests.get(f"{BASE_URL}/status/{random_uuid}")
    assert err_resp2.status_code in (400, 404)

def test_double_cancel(scheduled_job):
    job_id = scheduled_job
    cancel_resp1 = requests.post(f"{BASE_URL}/cancel/{job_id}")
    cancel_resp2 = requests.post(f"{BASE_URL}/cancel/{job_id}")
    assert cancel_resp2.status_code == 200
    data = cancel_resp2.json()
    assert data["job_id"] == job_id
    assert "cancelled" in data 