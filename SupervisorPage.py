import extra_streamlit_components as stx
from streamlit_autorefresh import st_autorefresh

from OrderThread import *
from SupervisorFunctions import *
from ProductionPlanningFunctions import *
import datetime

width1 = 320
width2 = 320
width3 = 500

client = MongoClient("mongodb://localhost:27017/")
db = client['local']
collection1 = db['ordersCollection']
collection7 = db['ordersConcluded']
collection15 = db['ValueGenerateOrders']
collection16 = db['HighPriority']
collection17 = db['MediumPriority']
collection18 = db['GamePhaseConfig']
collection24 = db['GameStartStop']
collection25 = db['DelayedOrders']


def game_phase_config(game_option):
    count1 = collection18.count_documents({})

    if game_option:
        collection18.update_one({}, {'$set': {'Game Phase': game_option}}, upsert=True)

    else:
        collection18.update_one({}, {'$set': {'Game Phase': None}}, upsert=True)


def game_mode_config(game_mode):
    collection24.update_one({}, {'$set': {'Game Mode': game_mode}}, upsert=True)


def conf1(configuration1):
    count1 = collection15.count_documents({})

    if count1 != 0:
        collection15.drop()
        collection15.insert_one({'Time Interval Generate Order': configuration1})

    else:
        configuration_default = 30
        collection15.insert_one({'Time Interval Generate Order': configuration_default})


def conf2(configuration2):
    high_priority = configuration2

    hours = high_priority.hour + high_priority.minute / 60

    count1 = collection16.count_documents({})

    if count1 != 0:
        collection16.drop()
        collection16.insert_one({'High Priority': hours})

    else:
        configuration_default = 0.08333
        collection16.insert_one({'High Priority': configuration_default})


def conf3(configuration3):
    medium_priority = configuration3

    hours = medium_priority.hour + medium_priority.minute / 60

    count2 = collection17.count_documents({})

    if count2 != 0:
        collection17.drop()
        collection17.insert_one({'Medium Priority': hours})

    else:
        configuration_default = 0.13333
        collection17.insert_one({'Medium Priority': configuration_default})


def supervisor_page():
    tab_bar_data = [
        stx.TabBarItemData(id=1, title="Game configurations", description=" "),
        stx.TabBarItemData(id=2, title="Game evolution", description=" "),
        stx.TabBarItemData(id=3, title="Game analysis", description=" "),
        stx.TabBarItemData(id=4, title="Order generation status", description=" "),
        stx.TabBarItemData(id=5, title="Cumulative order progress", description=" "),
        stx.TabBarItemData(id=6, title="Quality distribution", description=" "),
        stx.TabBarItemData(id=7, title="Lead time analysis", description=" "),
        stx.TabBarItemData(id=8, title="Workstation distribution", description=" "),
        stx.TabBarItemData(id=9, title="Order delivery status", description=" "),
        stx.TabBarItemData(id=10, title="Linear programming problem", description=" ")
    ]

    chosen_id = stx.tab_bar(data=tab_bar_data, default=1)

    update_timer()

    if chosen_id == "1":
        st.subheader("Game configurations", help='''\n Here you can set some configurations that will define the game. 
        Select the values for them to be accurate with the reality.''')

        def get_selected_game_phase():
            document = collection18.find_one()
            if document:
                return document.get('Game Phase')
            return None

        initial_game_option = get_selected_game_phase()
        options = ("Game 1", "Game 2")

        initial_index = options.index(initial_game_option) if initial_game_option in options else 0

        game_option = st.selectbox(label=':blue[Select the game phase in order to proceed]',
                                   options=options, key='game_options', index=initial_index,
                                   placeholder="Choose the game phase")
        game_phase_config(game_option)

        c1, c2, c3, c4 = st.columns(4)
        with c3:
            clear_game = st.button('Clear game', key='clear_game', type='secondary',
                                   help='Clear all data of the current game',
                                   use_container_width=True)
            if clear_game:
                semaphore()
                game_mode_config('Clear')
                st_autorefresh(limit=2, key='key2')

                db['ordersCollection'].drop()
                db['selectedOrders'].drop()
                db['qualityOrders'].drop()
                db['qualityApproved'].drop()
                db['qualityDisapproved'].drop()
                db['expeditionOrders'].drop()
                db['ordersConcluded'].drop()
                db['GenerateOrderTime'].drop()
                db['TimeOrderReleased'].drop()
                db['TimeProductionFinished'].drop()
                db['TimeExpeditionEnd'].drop()
                db['LeadTimeOrders'].drop()
                db['CumulativeOrdersFinished'].drop()
                db['PreSelectedOrders'].drop()
                db['ValueGenerateOrders'].drop()
                db['HighPriority'].drop()
                db['MediumPriority'].drop()
                db['LogisticsOrders'].drop()
                db['LogisticsOrdersProcess'].drop()
                db['AssemblyOrders'].drop()
                db['AssemblyOrdersProcess'].drop()
                db['SaveOrdersLogistics'].drop()
                db['GameStartStop'].drop()
                db['DelayedOrders'].drop()
                db['FlowProcessKPI'].drop()

        with c1:
            create_orders_button = st.button('Start game', key='create_orders', type='primary',
                                             help='Start generating orders',
                                             use_container_width=True)

        if create_orders_button:
            collection1.drop()
            start_thread()
            game_mode_config('Start')
            st_autorefresh(limit=2, key='key2')

        with c2:
            stop_orders_button = st.button('Stop game', key='stop_orders_button', type='primary',
                                           help='Stop generating orders',
                                           use_container_width=True)

        if stop_orders_button:
            semaphore()
            game_mode_config('Stop')
            st_autorefresh(limit=2, key='key3')

        st.caption("")
        configuration1 = st.number_input(":blue[Insert the time (in seconds) for the interval of orders generation:]",
                                         value=30, placeholder="Seconds...")
        conf1(configuration1)

        st.caption("")

        configuration2 = st.time_input(":blue[High priority orders value (HH-MM):]", value=datetime.time(0, 5))
        conf2(configuration2)

        st.caption("")

        configuration3 = st.time_input(":blue[Medium priority orders value (HH-MM):]", value=datetime.time(0, 8))
        conf3(configuration3)

    if chosen_id == "2":
        c1, c2, c3, c4 = st.columns(4)
        # Display TARGET in the first column
        with c1:
            st.markdown(
                '<div style="display: flex; flex-direction: column; justify-content: center; align-items: center;'
                'text-align: center; border: 2px solid rgb(85,88,103); padding: 10px; height: 150px;">'
                '<h1 style="font-size: 18px; line-height: 1.2; font-family: Verdana, sans-serif;'
                'font-weight: bold; color: rgb(85,88,103);">'
                'TARGET</h1>'
                '<h2 style="font-size: 30px; line-height: 30px; font-family: Verdana, sans-serif;'
                'font-weight: bold; color: rgb(85,88,103);">'
                '20</h2>'
                '</div>', unsafe_allow_html=True)

        with c2:
            total_orders = collection7.count_documents({})
            if total_orders:
                total_orders = total_orders
            else:
                total_orders = '-'
            st.markdown(
                '<div style="display: flex; flex-direction: column; justify-content: center; align-items: center;'
                'text-align: center; border: 2px solid rgb(85,88,103); padding: 10px; height: 150px;">'
                '<h1 style="font-size: 18px; line-height: 1.2; font-family: Verdana, sans-serif;'
                'font-weight: bold; color: rgb(85,88,103);">'
                'ACTUAL</h1>'
                '<h2 style="font-size: 30px; line-height: 30px; font-family: Verdana, sans-serif;'
                'font-weight: bold; color: rgb(85,88,103);">'
                f'{total_orders}</h2>'
                '</div>', unsafe_allow_html=True)

        with c3:
            delayed_orders = collection25.find_one({}, {'_id': 0, 'Total delayed orders': 1})

            if delayed_orders and 'Total delayed orders' in delayed_orders:
                delayed_orders = delayed_orders['Total delayed orders']
            else:
                delayed_orders = '-'
            st.markdown(
                '<div style="display: flex; flex-direction: column; justify-content: center; align-items: center;'
                'text-align: center; border: 2px solid rgb(85,88,103); padding: 10px; height: 150px;">'
                '<h1 style="font-size: 18px; line-height: 1.2; font-family: Verdana, sans-serif;'
                'font-weight: bold; color: rgb(85,88,103);">'
                'DELAYED ORDERS</h1>'
                '<h2 style="font-size: 30px; line-height: 20px; font-family: Verdana, sans-serif;'
                'font-weight: bold; color: rgb(85,88,103);">'
                f'{delayed_orders}</h2>'
                '</div>', unsafe_allow_html=True)

        with c4:
            flow_process = collection26.find_one({}, {'_id': 0, 'Flow delayed orders': 1})

            if flow_process and 'Flow delayed orders' in flow_process:
                flow_process = flow_process['Flow delayed orders']
            else:
                flow_process = '-'

            if flow_process == '-':
                st.markdown(
                    '<div style="display: flex; flex-direction: column; justify-content: center; align-items: center;'
                    'text-align: center; border: 2px solid rgb(85,88,103); padding: 10px; height: 150px;">'
                    '<h1 style="font-size: 18px; line-height: 1.2; font-family: Verdana, sans-serif;'
                    'font-weight: bold; color: rgb(85,88,103);">'
                    'FLOW</h1>'
                    '<h2 style="font-size: 30px; line-height: 20px; font-family: Verdana, sans-serif;'
                    'font-weight: bold; color: rgb(85,88,103);">'
                    f'{flow_process}</h2>'
                    '</div>', unsafe_allow_html=True)

            elif flow_process <= 0:
                st.markdown(
                    '<div style="display: flex; flex-direction: column; justify-content: center; align-items: center;'
                    'text-align: center; border: 2px solid rgb(85,88,103); padding: 10px; height: 150px;">'
                    '<h1 style="font-size: 18px; line-height: 1.2; font-family: Verdana, sans-serif;'
                    'font-weight: bold; color: rgb(85,88,103);">'
                    'FLOW</h1>'
                    '<h2 style="font-size: 30px; line-height: 20px; font-family: Verdana, sans-serif;'
                    'font-weight: bold; color: rgb(51, 115, 87);">'
                    f'{flow_process} min</h2>'
                    '</div>', unsafe_allow_html=True)

            elif flow_process > 0:
                st.markdown(
                    '<div style="display: flex; flex-direction: column; justify-content: center; align-items: center;'
                    'text-align: center; border: 2px solid rgb(85,88,103); padding: 10px; height: 150px;">'
                    '<h1 style="font-size: 18px; line-height: 1.2; font-family: Verdana, sans-serif;'
                    'font-weight: bold; color: rgb(85,88,103);">'
                    'FLOW</h1>'
                    '<h2 style="font-size: 30px; line-height: 20px; font-family: Verdana, sans-serif;'
                    'font-weight: bold; color: rgb(207, 119, 116);">'
                    f'{flow_process} min</h2>'
                    '</div>', unsafe_allow_html=True)

        st.caption('')
        st.caption('')
        kpis_orders()

    if chosen_id == "3":
        st.subheader("Game analysis", help='''\n This analysis provides important information related  various 
        metrics for an evolutionary analysis of the production line. \n Pay attention and discuss it with your 
        teammates.''')

        c1, c2 = st.columns(2)

        with c1:
            plot_generated_orders(width1)

        with c2:
            wip_plot(width2)

        with c1:
            quality_distribution_plot(width1)

        with c2:
            leadtime_plot(width2)

        with c1:
            orders_distribution_plot(width1)

        with c2:
            plot_delay_orders(width2)

        with c1:
            x_coefficients = [16.0, 18.0, 16.0, 11.0, 0.0, 1.0]
            y_coefficients = [23.0, 18.0, 14.0, 16.0, 1.0, 0.0]
            signs = ["<=", "<=", "<=", "<=", ">=", ">="]
            coefficients = [900.0, 900.0, 900.0, 900.0, 0.0, 0.0]
            objective_x = 3.0
            objective_y = 4.0

            result = linear_programming_trajectory(coefficients, x_coefficients, y_coefficients, signs,
                                                   [objective_x, objective_y], width1)

    if chosen_id == "4":
        plot_generated_orders(width3)

    if chosen_id == "5":
        wip_plot(width3)

    if chosen_id == "6":
        quality_distribution_plot(width3)

    if chosen_id == "7":
        leadtime_plot(width3)

    if chosen_id == "8":
        orders_distribution_plot(width3)

    if chosen_id == "9":
        plot_delay_orders(width3)

    if chosen_id == "10":
        x_coefficients = [16.0, 18.0, 16.0, 11.0, 0.0, 1.0]
        y_coefficients = [23.0, 18.0, 14.0, 16.0, 1.0, 0.0]
        signs = ["<=", "<=", "<=", "<=", ">=", ">="]
        coefficients = [900.0, 900.0, 900.0, 900.0, 0.0, 0.0]
        objective_x = 3.0
        objective_y = 4.0

        result = linear_programming_trajectory(coefficients, x_coefficients, y_coefficients, signs,
                                               [objective_x, objective_y], width3)
