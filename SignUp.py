# Imports
import streamlit as st
from pymongo import MongoClient
import datetime
import re
from streamlit_authenticator.utilities.hasher import Hasher

# Connect to MongoDB database
client = MongoClient("mongodb://localhost:27017/")
db = client['local']
collection0 = db['userCredentials']


def get_key(username):
    ds_users = collection0.find({'username': username})
    keys = []
    for username in ds_users:
        keys.append(username['key'])
    return keys[0]


# Function to insert user data into the database
def insert_user(email, username, key, password):
    # hashed_password = hashlib.sha256(password.encode()).hexdigest()
    date_joined = str(datetime.datetime.now())

    return collection0.insert_one(
        {'email': email, 'username': username, 'key': key, 'password': password, 'date_joined': date_joined})


# Function to fetch all users from the database
def fetch_users():
    db_users = collection0.find({}, {'_id': 0, 'email': 1, 'username': 1, 'key': 1, 'password': 1, 'date_joined': 1})
    users = [user for user in db_users]
    return users


# Function to get all user emails from the database
def get_user_emails():
    db_emails = collection0.find({}, {'_id': 0, 'email': 1})
    emails = []
    for email in db_emails:
        emails.append(email['email'])
    return emails


# Function to get all usernames from the database
def get_usernames():
    db_usernames = collection0.find({}, {'_id': 0, 'username': 1})
    usernames = []
    for username in db_usernames:
        usernames.append(username['username'])
    return usernames


# Function to validate email format
def validate_email(email):
    pattern = '^[a-zA-Z0-9_]+@[a-zA-Z0-9-]+\.[a-zA-Z.]+$'

    if re.match(pattern, email):
        return True
    return False


# Function to validate username format
def validate_username(username):
    pattern = '^[a-zA-Z0-9_ ]*$'

    if re.match(pattern, username):
        return True
    return False


# Function to handle user sign-up process
def sign_up():
    with st.form(key='signup'):
        st.subheader(':gray98[Sign Up]')

        email = st.text_input('Email', placeholder='Enter your Email')

        username = st.text_input('Username', placeholder='Enter your Username')

        key = st.selectbox('Choose your key', ("Supervisor", "Production Planning",
                                               "Assembly Process", "Quality Control", "Expedition", "Other"))

        password = st.text_input('Password', placeholder='Enter your Password', type='password')
        conf_password = st.text_input('Confirm Password', placeholder='Confirm your Password', type='password')

        if email and key:
            if validate_email(email):
                if email not in get_user_emails():
                    if validate_username(username):
                        if username not in get_usernames():
                            if len(username) >= 2:
                                if len(password) >= 3:
                                    if password == conf_password:
                                        hashed_password = Hasher([conf_password]).generate()
                                        insert_user(email, username, key, hashed_password[0])
                                        st.success('Account created successfully. Log in to get started!')
                                    else:
                                        st.warning('Passwords do not match. '
                                                   'Please ensure your passwords match before proceeding.')
                                else:
                                    st.warning('Password is too short. '
                                               'Please choose a longer password for better security.')
                            else:
                                st.warning('Username is too short. Please choose a longer username.')
                        else:
                            st.warning('The chosen username already exists. Please select a different username.')
                    else:
                        st.warning('Invalid username. Please choose a different username.')
                else:
                    st.warning('The provided email address is already associated with an existing account. '
                               'Please use a different email address.')
            else:
                st.warning('Invalid email address. Please provide a valid email address.')

        bt1, bt2, bt3, bt4, bt5 = st.columns(5)

        with bt1:
            st.form_submit_button('Sign In')


sign_up()
