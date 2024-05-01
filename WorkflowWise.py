# Imports
from ProductionPlanningPage import *
from QualityPage import *
from ExpeditionPage import *
from SupervisorPage import *
from AssemblyPage import *
from OtherPage import *

from streamlit_option_menu import option_menu
import streamlit_authenticator as stauth
from SignUp import sign_up, fetch_users, get_key


# Define a function named 'website' where it is all the design part of the application
def website():
    try:
        users = fetch_users()
        emails = []
        usernames = []
        passwords = []
        time = 0

        # Extract emails, usernames, and passwords from user data
        for user in users:
            emails.append(user['email'])
            usernames.append(user['username'])
            passwords.append(user['password'])

        # Create a dictionary of user credentials for authentication
        credentials = {'usernames': {}}

        for index in range(len(emails)):
            credentials['usernames'][usernames[index]] = {'name': emails[index], 'password': passwords[index]}

        # Authenticate users using the provided credentials and create a session cookie
        Authenticator = stauth.Authenticate(credentials, cookie_name='Streamlit',
                                            key='login_authentication', cookie_expiry_days=4)

        email, authentication_status, username = Authenticator.login(':blue[Login]', 'main')

        info, info1 = st.columns(2)

        if not authentication_status:
            sign_up()

        if username:
            if username in usernames:
                if authentication_status:
                    session_key = str(get_key(username))
                    permission = []

                    if session_key == 'Supervisor':
                        permission = ["Supervisory Page", "Production Planning", 'Assembly Process',
                                      "Quality Control", "Expedition", "Production Trajectory"]

                    if session_key == 'Production Planning':
                        permission = ["Production Planning"]

                    if session_key == 'Quality Control':
                        permission = ["Quality Control"]

                    if session_key == 'Expedition':
                        permission = ["Expedition"]

                    if session_key == 'Assembly Process':
                        permission = ["Assembly Process"]

                    if session_key == 'Production Trajectory':
                        permission = ["Production Trajectory"]

                    # Create a sidebar menu with different options for the user
                    with st.sidebar:
                        st.image('images/FCTUC_logo_horizontal.jpeg')
                        selected = option_menu(
                            menu_title="Main Menu",
                            options=permission,
                            icons=["bar-chart", "envelope", "screwdriver", "pencil",
                                   "journal-check", "box-arrow-up-right"],
                            menu_icon="house",
                            default_index=0)

                        # User is authenticated, display the main application interface
                        Authenticator.logout('Log Out', 'sidebar')

                    if selected == "Supervisory Page":
                        supervisor_page()

                    if selected == "Production Planning":
                        production_page()

                    if selected == "Assembly Process":
                        assembly_page()

                    if selected == 'Quality Control':
                        quality_page()

                    if selected == 'Expedition':
                        expedition_page()

                    if selected == 'Production Trajectory':
                        other_page()

                elif not authentication_status:
                    with info:
                        st.error('Invalid username or password. Please check your credentials and try again.')
                else:
                    with info:
                        st.warning('Please provide valid credentials to proceed.')
            else:
                with info:
                    st.warning('The provided username does not exist. Please sign up to create an account.')

    except:
        st.success('Refresh Page')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    website()
