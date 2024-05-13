from OrdersListFunctions import update_timer
from SupervisorFunctions import *
import extra_streamlit_components as stx


def conf1(configuration1):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['local']
    collection15 = db['ValueGenerateOrders']

    count1 = collection15.count_documents({})

    if count1 != 0:
        collection15.drop()
        collection15.insert_one({'Time Interval Generate Order': configuration1})

        cursor = collection15.find()
        # Print data
        for document in cursor:
            print("Conf count nao 0 ", document)

    else:
        configuration_default = 30
        collection15.insert_one({'Time Interval Generate Order': configuration_default})
        cursor = collection15.find()
        # Print data
        for document in cursor:
            print("Conf count=0 ", document)


def supervisor_page():
    # update_timer()

    tab_bar_data = [
        stx.TabBarItemData(id=1, title="Game Configurations", description=" "),
        stx.TabBarItemData(id=2, title="Evolutionary Analysis", description=" "),
        stx.TabBarItemData(id=3, title="Order Generation Status", description=" "),
        stx.TabBarItemData(id=4, title="Cumulative Order Progress", description=" "),
        stx.TabBarItemData(id=5, title="Quality Distribution", description=" "),
        stx.TabBarItemData(id=6, title="Lead Time Analysis", description=" "),
        stx.TabBarItemData(id=7, title="Workstation Distribution", description=" "),
        stx.TabBarItemData(id=8, title="Linear Programming Problem", description=" ")
    ]

    chosen_id = stx.tab_bar(data=tab_bar_data, default=1)

    if chosen_id == "1":
        st.subheader("Game Configurations")
        with st.expander("Quick note:", expanded=True):
            st.markdown(
                '''\n Here you can set some configurations that will define the game. Select the values for them to 
                be accurate with the reality.'''
            )

        configuration1 = st.number_input(":blue[Insert how much time (in seconds) between orders generation]",
                                        value=30, placeholder="Seconds...")

        st.write("The current number is ", configuration1)

        print("\n mudado", configuration1)

        conf1(configuration1)

    if chosen_id == "2":
        st.subheader("Evolutionary Analysis of the Game")
        with st.expander("Quick note:", expanded=True):
            st.markdown(
                '''\n This analysis provides important information related  various metrics for an evolutionary 
                analysis of the production line. \n Pay attention and discuss it with your teammates.'''
            )
        c1, c2 = st.columns(2)
        with c1:
            width1 = 320
            plot_generated_orders(width1)

        with c2:
            width2 = 350
            wip_plot(width2)

        with c1:
            width3 = 320
            quality_distribution(width3)

        with c2:
            width4 = 350
            leadtime(width4)

        with c1:
            width5 = 320
            orders_distribution(width5)

        with c2:
            x_coefficients = [16.0, 18.0, 16.0, 11.0, 0.0, 1.0]
            y_coefficients = [23.0, 18.0, 14.0, 16.0, 1.0, 0.0]
            signs = ["<=", "<=", "<=", "<=", ">=", ">="]
            coefficients = [900.0, 900.0, 900.0, 900.0, 0.0, 0.0]
            objective_x = 3.0
            objective_y = 4.0

            width6 = 350
            result = LinearProgrammingExample(coefficients, x_coefficients, y_coefficients, signs,
                                              [objective_x, objective_y], width6)

    if chosen_id == "3":
        width1 = 500
        plot_generated_orders(width1)

    if chosen_id == "4":
        width2 = 500
        wip_plot(width2)

    if chosen_id == "5":
        width3 = 500
        quality_distribution(width3)

    if chosen_id == "6":
        width4 = 500
        leadtime(width4)

    if chosen_id == "7":
        width5 = 500
        orders_distribution(width5)

    if chosen_id == "8":
        width6 = 500
        x_coefficients = [16.0, 18.0, 16.0, 11.0, 0.0, 1.0]
        y_coefficients = [23.0, 18.0, 14.0, 16.0, 1.0, 0.0]
        signs = ["<=", "<=", "<=", "<=", ">=", ">="]
        coefficients = [900.0, 900.0, 900.0, 900.0, 0.0, 0.0]
        objective_x = 3.0
        objective_y = 4.0

        result = LinearProgrammingExample(coefficients, x_coefficients, y_coefficients, signs,
                                          [objective_x, objective_y], width6)
