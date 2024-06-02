# Imports
from ProductionPlanningPage import *
from QualityPage import *
from ExpeditionPage import *
from SupervisorPage import *
from AssemblyPage import *
from OptimizationPage import *
from SignUp import sign_up, fetch_users, get_key
from LogisticsPage import *

from streamlit_option_menu import option_menu
from streamlit_authenticator import Authenticate


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
        authenticator = Authenticate(credentials, cookie_name='Streamlit', cookie_key='key', cookie_expiry_days=4)

        email, authentication_status, username = authenticator.login()

        c = st.container()

        if not authentication_status:
            sign_up()

        if username:
            if username in usernames:
                if authentication_status:
                    session_key = str(get_key(username))
                    permission = []

                    if session_key == 'Supervisor':
                        permission = ["Supervisor", "Production Planning", "Logistics Operator",
                                      'Assembly Process', "Quality Control", "Expedition", "Production Trajectory"]

                    if session_key == 'Production Planning':
                        permission = ["Production Planning"]

                    if session_key == 'Assembly Process':
                        permission = ["Assembly Process"]

                    if session_key == 'Logistics Operator':
                        permission = ["Logistics Operator"]

                    if session_key == 'Quality Control':
                        permission = ["Quality Control"]

                    if session_key == 'Expedition':
                        permission = ["Expedition"]

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
                        authenticator.logout('Log Out', 'sidebar')

                    if selected == "Supervisor":
                        supervisor_page()

                    if selected == "Production Planning":
                        production_page()

                    if selected == "Assembly Process":
                        assembly_page()

                    if selected == "Logistics Operator":
                        logistics_page()

                    if selected == 'Quality Control':
                        quality_page()

                    if selected == 'Expedition':
                        expedition_page()

                    if selected == 'Production Trajectory':
                        other_page()

        if authentication_status is False and username is None:
            with c:
                st.error('Invalid username or password. Please check your credentials and try again.')

    except:
        st.success('Refresh Page')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    website()
