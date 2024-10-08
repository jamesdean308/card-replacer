import requests
import time

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
        print("result_response", result_response)
        result_data = result_response.json()
        task_status = result_data.get("status")
        print(f"Task Status: {task_status}")
        if task_status == "SUCCESS":
            return result_data.get("result")
        elif task_status in ("FAILURE", "REVOKED"):
            return result_data.get("result")
        time.sleep(2)


if __name__ == "__main__":
    username = "testuser"
    password = "testpassword"

    token = login_user(username, password)
    print("token:", token)

    if token:
        delete_response = delete_user(token)
        print(delete_response.status_code)
        print(delete_response.json())

    print("Registering user...")
    register_response = register_user(username, password)
    print(register_response.status_code, register_response.json())

    if register_response.status_code == 201:

        print("Logging in user...")
        token = login_user(username, password)
        if token:
            print("Login successful, token received.")
            print("Requesting card...")
            card_response = request_card(token)
            print(card_response.status_code, card_response.json())
            task_id = card_response.json().get("task_id")

            if task_id:
                print("Fetching task result...")
                result = get_task_result(task_id)
                print(f"Task Result: {result}")
            else:
                print("No task ID returned in card request response.")
        else:
            print("Login failed.")
    else:
        print("User registration failed.")
