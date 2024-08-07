import extra_streamlit_components as stx
from OrderThread import *
from SupervisorFunctions import *
from ProductionPlanningFunctions import reset_release_id
import datetime


def game_conf(game_option):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['local']
    collection18 = db['GamePhaseConfig']

    count1 = collection18.count_documents({})

    if game_option:
        collection18.update_one({}, {'$set': {'Game Phase': game_option}}, upsert=True)

    else:
        collection18.update_one({}, {'$set': {'Game Phase': None}}, upsert=True)


def conf1(configuration1):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['local']
    collection15 = db['ValueGenerateOrders']

    count1 = collection15.count_documents({})

    if count1 != 0:
        collection15.drop()
        collection15.insert_one({'Time Interval Generate Order': configuration1})

    else:
        configuration_default = 30
        collection15.insert_one({'Time Interval Generate Order': configuration_default})


def conf2(configuration2):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['local']
    collection16 = db['HighPriority']

    high_priority = configuration2

    hours = high_priority.hour + high_priority.minute / 60

    count1 = collection16.count_documents({})

    if count1 != 0:
        collection16.drop()
        collection16.insert_one({'High Priority': hours})

    else:
        configuration_default = 0.085
        collection16.insert_one({'High Priority': configuration_default})


def conf3(configuration3):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['local']
    collection17 = db['MediumPriority']

    medium_priority = configuration3

    hours = medium_priority.hour + medium_priority.minute / 60

    count2 = collection17.count_documents({})

    if count2 != 0:
        collection17.drop()
        collection17.insert_one({'Medium Priority': hours})

    else:
        configuration_default = 0.17
        collection17.insert_one({'Medium Priority': configuration_default})


def supervisor_page():
    # update_timer()

    tab_bar_data = [
        stx.TabBarItemData(id=1, title="Game configurations", description=" "),
        stx.TabBarItemData(id=2, title="Game analysis", description=" "),
        stx.TabBarItemData(id=3, title="Order generation status", description=" "),
        stx.TabBarItemData(id=4, title="Cumulative order progress", description=" "),
        stx.TabBarItemData(id=5, title="Quality distribution", description=" "),
        stx.TabBarItemData(id=6, title="Lead time analysis", description=" "),
        stx.TabBarItemData(id=7, title="Workstation distribution", description=" "),
        stx.TabBarItemData(id=8, title="Linear programming problem", description=" ")
    ]

    chosen_id = stx.tab_bar(data=tab_bar_data, default=1)

    if chosen_id == "1":
        st.subheader("Game configurations", help='''\n Here you can set some configurations that will define the game. 
        Select the values for them to be accurate with the reality.''')

        client = MongoClient("mongodb://localhost:27017/")
        db = client['local']

        def get_selected_game_phase():
            collection18 = db['GamePhaseConfig']

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
        game_conf(game_option)

        c1, c2, c3, c4 = st.columns(4)
        with c3:
            clear_game = st.button('Clear game', key='clear_game', type='secondary',
                                   help='Clear all data of the current game',
                                   use_container_width=True)
            if clear_game:
                semaphore()
                reset_release_id()
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

        with c1:
            create_orders_button = st.button('Start game', key='create_orders', type='primary',
                                             help='Start Generating Orders',
                                             use_container_width=True)

        with c2:
            stop_orders_button = st.button('Stop game', key='stop_orders_button', type='primary',
                                           help='Stop Generating Orders',
                                           use_container_width=True)

        collection1 = db['ordersCollection']

        if create_orders_button:
            reset_release_id()
            collection1.drop()
            start_thread()

        if stop_orders_button:
            semaphore()

        st.caption("")
        configuration1 = st.number_input(":blue[Insert the time (in seconds) for the interval of orders generation:]",
                                         value=30, placeholder="Seconds...")
        conf1(configuration1)

        st.caption("")

        configuration2 = st.time_input(":blue[High priority orders value (HH-MM):]", value=datetime.time(0, 5))
        conf2(configuration2)

        st.caption("")

        configuration3 = st.time_input(":blue[Medium priority orders value (HH-MM):]", value=datetime.time(0, 10))
        conf3(configuration3)

    if chosen_id == "2":
        st.subheader("Game Analysis", help='''\n This analysis provides important information related  various 
        metrics for an evolutionary analysis of the production line. \n Pay attention and discuss it with your 
        teammates.''')

        calculate_delay_orders()

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
