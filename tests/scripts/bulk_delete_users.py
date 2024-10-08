import requests

base_url = "http://localhost:5000"


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


def bulk_delete_users(base_username, password, count):
    deleted_users = []
    for i in range(1, count + 1):
        username = f"{base_username}_{i}"
        token = login_user(username, password)
        if token:
            response = delete_user(token)
            if response.status_code == 200:
                deleted_users.append(username)
                print(f"User {username} deleted successfully.")
            else:
                print(
                    f"Failed to delete user {username}. Status: {response.status_code}, Response: {response.json()}"
                )
        else:
            print(f"Failed to log in user {username}.")
    return deleted_users


if __name__ == "__main__":
    base_username = "testuser"
    password = "testpassword"
    count = 100

    print(f"Deleting {count} users...")
    deleted_users = bulk_delete_users(base_username, password, count)
    print(f"Total users deleted: {len(deleted_users)}")
