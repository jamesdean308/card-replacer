import requests
import time

# Set the base URL of your Flask application running in Minikube
# Assuming your Flask application is exposed on localhost:5000
# You might need to port-forward the service if it is not directly accessible
BASE_URL = "http://localhost:49305"

# Payload to send to the add task
add_task_payload = {"x": 10, "y": 6}

# Send the request to trigger the add task
response = requests.post(f"{BASE_URL}/add", json=add_task_payload)
response_data = response.json()
task_id = response_data.get("task_id")
print("Add Task Response:", response_data)


# Function to check task status and fetch result
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


# Fetch and print the task result
result = get_task_result(task_id)
print(f"Task Result: {result}")
