import requests
import time

# Set the base URL for your Flask API
base_url = "http://localhost:49305"


# Function to register a new user
def register_user(username, password):
    url = f"{base_url}/register"
    data = {"username": username, "password": password}
    response = requests.post(url, json=data)
    return response


# Function to log in and get a JWT token
def login_user(username, password):
    url = f"{base_url}/login"
    data = {"username": username, "password": password}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        return None


# Function to request a card using the JWT token
def request_card(token):
    url = f"{base_url}/request_card"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, headers=headers)
    return response


# Function to check task status and fetch result
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


# Main script
if __name__ == "__main__":
    username = "testuser"
    password = "testpassword"

    # Register the user
    print("Registering user...")
    register_response = register_user(username, password)
    print(register_response.status_code, register_response.json())

    # if register_response.status_code == 201:
    if True:  # Assuming the user is registered successfully
        # Log in the user
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
