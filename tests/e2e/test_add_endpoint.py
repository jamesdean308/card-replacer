import requests
import time
import pytest

BASE_URL = "http://localhost:5000"


@pytest.fixture
def base_url():
    return BASE_URL


def get_task_result(task_id, base_url):
    task_result_url = f"{base_url}/tasks/{task_id}"
    while True:
        result_response = requests.get(task_result_url)
        result_data = result_response.json()
        task_status = result_data.get("status")
        if task_status == "SUCCESS":
            return result_data.get("result")
        elif task_status in ("FAILURE", "REVOKED"):
            return result_data.get("result")
        time.sleep(2)


def test_add_task(base_url):
    add_task_payload = {"x": 10, "y": 6}
    response = requests.post(f"{base_url}/add", json=add_task_payload)
    response_data = response.json()
    task_id = response_data.get("task_id")
    assert response.status_code == 202
    assert "task_id" in response_data

    result = get_task_result(task_id, base_url)
    assert result == 16
