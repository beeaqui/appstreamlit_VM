import json
from streamlit_authenticator.utilities.hasher import Hasher


def load_plain_credentials():
    with open('credentials.json', 'r') as file:
        data = json.load(file)
    return data['users']


def save_updated_credentials(users):
    with open('credentials.json', 'w') as file:
        json.dump({"users": users}, file, indent=4)


def initialize_credentials():
    users = load_plain_credentials()
    hashed_users = []

    for user in users:
        hashed_password = Hasher([user['password']]).generate()[0]
        user['hashed_password'] = hashed_password
        hashed_users.append(user)

    save_updated_credentials(hashed_users)
    print("Updated credentials with hashed passwords saved to credentials.json")


def load_credentials():
    with open('credentials.json', 'r') as file:
        data = json.load(file)
    return data['users']


def fetch_users():
    users = load_credentials()
    return users


def get_key(username):
    users = load_credentials()
    for user in users:
        if user['username'] == username:
            return user['key']
    return None

# Uncomment the following line to initialize credentials (run only once)
# initialize_credentials()
