import requests
import time


BASE_URL = "http://localhost:5000"

add_task_payload = {"x": 10, "y": 6}

response = requests.post(f"{BASE_URL}/add", json=add_task_payload)
response_data = response.json()
task_id = response_data.get("task_id")
print("Add Task Response:", response_data)


def get_task_result(task_id):
    task_result_url = f"{BASE_URL}/tasks/{task_id}"
    while True:
        result_response = requests.get(task_result_url)
        result_data = result_response.json()
        task_status = result_data.get("status")
        print(f"Task Status: {task_status}, Task ID: {task_id}")
        if task_status == "SUCCESS":
            return result_data.get("result")
        elif task_status in ("FAILURE", "REVOKED"):
            return result_data.get("result")
        time.sleep(2)


result = get_task_result(task_id)
print(f"Task Result: {result}")
