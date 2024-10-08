import requests
import time
from concurrent.futures import ThreadPoolExecutor


base_url = "http://localhost:5000"


def register_user(username, password):
    url = f"{base_url}/register"
    data = {"username": username, "password": password}
    response = requests.post(url, json=data)
    if response.status_code == 201:
        print(f"User {username} registered successfully.")
    else:
        print(f"Failed to register user {username}: {response.text}")


def login_user(username, password):
    url = f"{base_url}/login"
    data = {"username": username, "password": password}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Failed to log in user: {username}")
        return None


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
        if task_status == "SUCCESS":
            return result_data.get("result")
        elif task_status in ("FAILURE", "REVOKED"):
            return result_data.get("result")
        time.sleep(2)


def register_login_and_request_card(username, password):

    token = login_user(username, password)
    if token:
        print(f"User {username} logged in successfully.")
        card_response = request_card(token)
        if card_response.status_code == 201:
            task_id = card_response.json().get("task_id")
            if task_id:
                result = get_task_result(task_id)
                print(f"Task Result for {username}: {result}")
            else:
                print(f"No task ID returned for user {username}")
        else:
            print(f"Failed to request card for user {username}")
    else:
        print(f"Failed to log in user {username}")


if __name__ == "__main__":
    users = [{"username": f"user{i}", "password": "testpassword"} for i in range(1, 21)]

    print("Registering users...")
    with ThreadPoolExecutor(max_workers=20) as executor:
        register_futures = [
            executor.submit(register_user, user["username"], user["password"])
            for user in users
        ]

    print("All users have been registered.")

    print("Logging in users and requesting cards...")
    with ThreadPoolExecutor(max_workers=20) as executor:
        request_futures = [
            executor.submit(
                register_login_and_request_card, user["username"], user["password"]
            )
            for user in users
        ]

    print("All card requests have been initiated.")
