# Imports
from ProductionPlanningPage import *
from QualityPage import *
from ExpeditionPage import *
from SupervisorPage import *
from AssemblyPage import *
from OptimizationPage import *
from SignUp import *
from LogisticsPage import *

import time

from streamlit_option_menu import option_menu
from streamlit_authenticator import Authenticate
from streamlit_autorefresh import st_autorefresh

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False


def unique_key(page_name):
    return f"{page_name}_{int(time.time())}"


# Define a function named 'website' where it is all the design part of the application
def website():
    users = fetch_users()
    usernames = [user['username'] for user in users]

    # Create a dictionary of user credentials for authentication
    credentials = {'usernames': {}}

    for user in users:
        credentials['usernames'][user['username']] = {'name': user['email'], 'password': user['hashed_password']}

    if not st.session_state.logged_in:
        c1, c2, c3 = st.columns(3)
        with c2:
            st.image('images/UC_logo.png')

        st.write(
            "<div style='text-align: center;'>"
            "<strong style='color: #003366;'>Welcome to the UC Factory Lab Optimizer!</strong><br><br>"
            "</div>"
            "<div style='text-align: left;'>"
            "This app enhances your experience within the UC Factory Lab, where hands-on learning meets cutting-edge "
            "industrial technology. By streamlining production tasks, our app allows you to efficiently interact with "
            "the assembly line, working seamlessly with robots and advanced systems to perform assembly and other "
            "tasks. Leverage the principles of Lean Manufacturing and Continuous Improvement as you engage in "
            "real-world production scenarios. Enjoy a smarter, more efficient assembly process with the UC Factory "
            "Lab Optimizer.<br><br>"
            "</div>",
            unsafe_allow_html=True)

        organization = st.text_input(f":blue[**Insert your organization**]", key='org')
        key = unique_key('login')
        st_autorefresh(limit=10, interval=15000, key='key')

    authenticator = Authenticate(credentials, cookie_name='Streamlit', cookie_key='key', cookie_expiry_days=4)

    email, authentication_status, username = authenticator.login()

    if username:
        if username in usernames:
            if authentication_status:
                st.session_state.logged_in = True
                session_key = str(get_key(username))
                permission = []

                if session_key == 'Supervisor':
                    permission = ["Supervisor", "Production planning", "Logistics operator",
                                  'Assembly process', "Quality control", "Expedition", "Production trajectory"]

                if session_key == 'Production planning':
                    permission = ["Production planning"]

                if session_key == 'Assembly process':
                    permission = ["Assembly process"]

                if session_key == 'Logistics operator':
                    permission = ["Logistics operator"]

                if session_key == 'Quality control':
                    permission = ["Quality control"]

                if session_key == 'Expedition':
                    permission = ["Expedition"]

                if session_key == 'Production trajectory':
                    permission = ["Production trajectory"]

                with st.sidebar:
                    st.image('images/UC_logo_horizontal.png', use_column_width=True)

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
                    key = unique_key('supervisor')
                    st_autorefresh(limit=50, interval=15000, key='supervisor')
                    supervisor_page()

                if selected == "Production planning":
                    production_page(db)

                if selected == "Assembly process":
                    assembly_page()

                if selected == "Logistics operator":
                    logistics_page()

                if selected == 'Quality control':
                    key = unique_key('quality')
                    st_autorefresh(limit=50, interval=15000, key='quality')
                    quality_page()

                if selected == 'Expedition':
                    key = unique_key('expedition')
                    st_autorefresh(limit=50, interval=15000, key='expedition')
                    expedition_page()

                if selected == 'Production trajectory':
                    key = unique_key('trajectory')
                    st_autorefresh(limit=50, interval=15000, key='trajectory')
                    optimization_trajectory()

    if not authentication_status:
        st.session_state.logged_in = False

        st_autorefresh(limit=2, key='email_link')
        email = "samuel.moniz@dem.uc.pt"
        subject = "Support"
        body = "Please explain your doubt and we will answer as soon as possible. Thank you!"

        mailto_url = f"mailto:{email}?subject={subject}&body={body}"

        st.markdown(f"[Send an Email](<{mailto_url}>)", unsafe_allow_html=True)

    c = st.container()
    if authentication_status is False and username is None:
        with c:
            st.error('Invalid username or password. Please check your credentials and try again.')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    website()
