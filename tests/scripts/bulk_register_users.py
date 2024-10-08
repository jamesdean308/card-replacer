import requests

base_url = "http://localhost:5000"


def register_user(username, password):
    url = f"{base_url}/register"
    data = {"username": username, "password": password}
    response = requests.post(url, json=data)
    return response


def bulk_register_users(base_username, password, count):
    created_users = []
    for i in range(1, count + 1):
        username = f"{base_username}_{i}"
        response = register_user(username, password)
        if response.status_code == 201:
            created_users.append(username)
            print(f"User {username} registered successfully.")
        else:
            print(
                f"Failed to register user {username}. Status: {response.status_code}, Response: {response.json()}"
            )
    return created_users


if __name__ == "__main__":
    base_username = "testuser"
    password = "testpassword"
    count = 100

    print(f"Creating {count} users...")
    created_users = bulk_register_users(base_username, password, count)
    print(f"Total users created: {len(created_users)}")
