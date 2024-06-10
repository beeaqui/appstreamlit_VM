import json
from streamlit_authenticator.utilities.hasher import Hasher


# Load plain text credentials from JSON file
def load_plain_credentials():
    with open('credentials.json', 'r') as file:
        data = json.load(file)
    return data['users']


# Save updated credentials to a new JSON file
def save_updated_credentials(users):
    with open('credentials.json', 'w') as file:
        json.dump({"users": users}, file, indent=4)


# Function to initialize credentials (hash passwords and save to a new file)
def initialize_credentials():
    users = load_plain_credentials()
    hashed_users = []

    for user in users:
        # Generate hashed password using Hasher module
        hashed_password = Hasher([user['password']]).generate()[0]
        user['hashed_password'] = hashed_password
        hashed_users.append(user)

    # Save updated credentials with hashed passwords to credentials.json
    save_updated_credentials(hashed_users)
    print("Updated credentials with hashed passwords saved to credentials.json")


# Load credentials from the JSON file
def load_credentials():
    with open('credentials.json', 'r') as file:
        data = json.load(file)
    return data['users']


# Function to fetch all users from the credentials file
def fetch_users():
    users = load_credentials()
    return users


# Function to get the key (role) of a user
def get_key(username):
    users = load_credentials()
    for user in users:
        if user['username'] == username:
            return user['key']
    return None

# Uncomment the following line to initialize credentials (run only once)
# initialize_credentials()
