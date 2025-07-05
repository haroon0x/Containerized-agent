#!/usr/bin/env python3
import requests
import time
import json

ORCHESTRATOR_URL = "http://localhost:8000"

def test_system():
    print("Testing Containerized Agent System")
    print("=" * 40)
    
    # Test 1: Health check
    try:
        response = requests.get(f"{ORCHESTRATOR_URL}/")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test 2: Schedule a job
    try:
        job_data = {"prompt": "What is 2 + 2? Answer in one sentence."}
        response = requests.post(f"{ORCHESTRATOR_URL}/schedule", json=job_data)
        print(f"✅ Schedule job: {response.status_code}")
        result = response.json()
        job_id = result["job_id"]
        print(f"   Job ID: {job_id}")
    except Exception as e:
        print(f"❌ Schedule job failed: {e}")
        return
    
    # Test 3: Check job status
    print("\nMonitoring job status...")
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get(f"{ORCHESTRATOR_URL}/status/{job_id}")
            status_data = response.json()
            status = status_data["status"]
            print(f"   Status: {status}")
            
            if status == "complete":
                print(f"✅ Job completed!")
                if "download_link" in status_data:
                    print(f"   Download: {status_data['download_link']}")
                if "logs_link" in status_data:
                    print(f"   Logs: {status_data['logs_link']}")
                break
            elif status in ["error", "cancelled"]:
                print(f"❌ Job failed with status: {status}")
                break
                
        except Exception as e:
            print(f"❌ Status check failed: {e}")
            break
            
        time.sleep(2)
    else:
        print("⏰ Job timed out")
    
    # Test 4: List all jobs
    try:
        response = requests.get(f"{ORCHESTRATOR_URL}/jobs")
        jobs = response.json()["jobs"]
        print(f"\n✅ List jobs: {len(jobs)} jobs found")
        for job in jobs:
            print(f"   {job['job_id']}: {job['status']}")
    except Exception as e:
        print(f"❌ List jobs failed: {e}")

if __name__ == "__main__":
    test_system() 