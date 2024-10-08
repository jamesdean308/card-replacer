import requests
import time
import pytest

base_url = "http://localhost:5000"


def register_user(username, password):
    url = f"{base_url}/register"
    data = {"username": username, "password": password}
    response = requests.post(url, json=data)
    return response


def login_user(username, password):
    url = f"{base_url}/login"
    data = {"username": username, "password": password}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        return None


def delete_user(token):
    url = f"{base_url}/delete_user"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(url, headers=headers)
    return response


def request_card(token):
    url = f"{base_url}/request_card"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, headers=headers)
    return response


def get_task_result(task_id):
    task_result_url = f"{base_url}/tasks/{task_id}"
    while True:
        result_response = requests.get(task_result_url)
        result_data = result_response.json()
        task_status = result_data.get("status")
        print(f"Task Status: {task_status}")
        if task_status == "SUCCESS":
            return result_data.get("result")
        elif task_status in ("FAILURE", "REVOKED"):
            return result_data.get("result")
        time.sleep(2)


def test_card_replacement_flow():
    username = "testuser"
    password = "testpassword"

    # Log in and delete the user if they exist
    token = login_user(username, password)
    if token:
        delete_response = delete_user(token)
        assert delete_response.status_code == 200
    register_response = register_user(username, password)
    assert register_response.status_code == 201

    token = login_user(username, password)
    assert token is not None

    card_response = request_card(token)
    assert card_response.status_code == 201
    task_id = card_response.json().get("task_id")
    assert task_id is not None

    result = get_task_result(task_id)
    assert result == "Card request processed successfully"
