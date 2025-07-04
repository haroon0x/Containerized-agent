import requests
import time
import uuid

BASE_URL = "http://localhost:8000"

# 1. Schedule a job
print("Scheduling job...")
resp = requests.post(f"{BASE_URL}/schedule", json={"prompt": "echo Hello World"})
assert resp.status_code == 200, resp.text
job_id = resp.json()["job_id"]
print(f"Job scheduled: {job_id}")

# 2. Poll status until complete or timeout
print("Polling status...")
for _ in range(30):
    status_resp = requests.get(f"{BASE_URL}/status/{job_id}")
    assert status_resp.status_code == 200, status_resp.text
    status = status_resp.json()["status"]
    print(f"Status: {status}")
    if status == "complete":
        break
    time.sleep(2)
else:
    print("Job did not complete in time.")

# 3. Attempt to download output
print("Attempting to download output...")
download_resp = requests.get(f"{BASE_URL}/download/{job_id}")
if download_resp.status_code == 200:
    with open(f"output_{job_id}.zip", "wb") as f:
        f.write(download_resp.content)
    print(f"Downloaded output to output_{job_id}.zip")
else:
    print(f"Download failed: {download_resp.text}")

# 4. Attempt to fetch logs
print("Fetching logs...")
logs_resp = requests.get(f"{BASE_URL}/logs/{job_id}")
if logs_resp.status_code == 200:
    print("Logs:", logs_resp.json()["last_1000_lines"][:200], "...")
else:
    print(f"Logs fetch failed: {logs_resp.text}")

# 5. Cancel a job (should be already complete, so expect no effect)
print("Cancelling job...")
cancel_resp = requests.post(f"{BASE_URL}/cancel/{job_id}")
print(f"Cancel response: {cancel_resp.json()}")

# 6. Try error cases
print("Testing error cases...")
invalid_id = "not-a-uuid"
err_resp = requests.get(f"{BASE_URL}/status/{invalid_id}")
print(f"Invalid job_id status: {err_resp.status_code}, {err_resp.text}")

random_uuid = str(uuid.uuid4())
err_resp2 = requests.get(f"{BASE_URL}/status/{random_uuid}")
print(f"Nonexistent job_id status: {err_resp2.status_code}, {err_resp2.text}")

# 7. Double cancel
print("Double cancelling...")
cancel_resp2 = requests.post(f"{BASE_URL}/cancel/{job_id}")
print(f"Double cancel response: {cancel_resp2.json()}")

print("Test script complete.") 