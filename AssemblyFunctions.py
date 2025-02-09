import streamlit as st
import pandas as pd
from pymongo import MongoClient
from streamlit_autorefresh import st_autorefresh

client = MongoClient("mongodb://localhost:27017/")
db = client['local']
collection3 = db['qualityOrders']
collection18 = db['GamePhaseConfig']
collection21 = db['AssemblyOrders']
collection22 = db['AssemblyOrdersProcess']

game2_label = ""
game1_label = ""
game1_list = []
game2_list = []
numbers_to_delete = []
final = False


def basic_cylinder_operations():
    tab_data = [
        {'Operation': 'A', 'Description': 'Position the cylinder barrel in the vertical in a flat surface'},
        {'Operation': 'B', 'Description': 'Connect the back section and the cylinder barrel'},
        {'Operation': 'C', 'Description': 'Insert screw number one'},
        {'Operation': 'D', 'Description': 'Insert screw number two'},
        {'Operation': 'E', 'Description': 'Place the piston in the barrel hole and push it to connect it to the back '
                                          'section of the cylinder'},
        {'Operation': 'F', 'Description': 'Insert the top section in the piston rod and connect it to the barrel'},
        {'Operation': 'G', 'Description': 'Insert screw number three'},
        {'Operation': 'H', 'Description': 'Insert screw number four'},
        {'Operation': 'I', 'Description': 'Screw in the nut in the piston rod'},
        {'Operation': 'J', 'Description': 'Insert the swivel flange and connect it to the section.'}
    ]

    df = pd.DataFrame(tab_data)
    st.image('images/cylinder.png')
    st.dataframe(df, hide_index=True, use_container_width=True)


def push_fitting_operations():
    tab_data = [
        {'Operation': 'A', 'Description': 'Position the cylinder barrel in the vertical in a flat surface'},
        {'Operation': 'B', 'Description': 'Connect the back section and the cylinder barrel'},
        {'Operation': 'C', 'Description': 'Insert screw number one'},
        {'Operation': 'D', 'Description': 'Insert screw number two'},
        {'Operation': 'E', 'Description': 'Place the piston in the barrel hole and push it to connect it to the back '
                                          'section of the cylinder'},
        {'Operation': 'F', 'Description': 'Insert the top section in the piston rod and connect it to the barrel'},
        {'Operation': 'G', 'Description': 'Insert screw number three'},
        {'Operation': 'H', 'Description': 'Insert screw number four'},
        {'Operation': 'I', 'Description': 'Screw in the nut in the piston rod'},
        {'Operation': 'J', 'Description': 'Insert the two connectors push-in fitting'}
    ]

    df = pd.DataFrame(tab_data)
    st.image('images/op1_connectors.png')
    st.dataframe(df, hide_index=True, use_container_width=True)


def push_l_operations():
    tab_data = [
        {'Operation': 'A', 'Description': 'Position the cylinder barrel in the vertical in a flat surface'},
        {'Operation': 'B', 'Description': 'Connect the back section and the cylinder barrel'},
        {'Operation': 'C', 'Description': 'Insert screw number one'},
        {'Operation': 'D', 'Description': 'Insert screw number two'},
        {'Operation': 'E', 'Description': 'Place the piston in the barrel hole and push it to connect it to the back '
                                          'section of the cylinder'},
        {'Operation': 'F', 'Description': 'Insert the top section in the piston rod and connect it to the barrel'},
        {'Operation': 'G', 'Description': 'Insert screw number three'},
        {'Operation': 'H', 'Description': 'Insert screw number four'},
        {'Operation': 'I', 'Description': 'Screw in the nut in the piston rod'},
        {'Operation': 'J', 'Description': 'Insert the two connectors push-in L-fitting'}
    ]

    df = pd.DataFrame(tab_data)
    st.image('images/op2_connectors.png')
    st.dataframe(df, hide_index=True, use_container_width=True)


def mixed_connectors_operations():
    tab_data = [
        {'Operation': 'A', 'Description': 'Position the cylinder barrel in the vertical in a flat surface'},
        {'Operation': 'B', 'Description': 'Connect the back section and the cylinder barrel'},
        {'Operation': 'C', 'Description': 'Insert screw number one'},
        {'Operation': 'D', 'Description': 'Insert screw number two'},
        {'Operation': 'E', 'Description': 'Place the piston in the barrel hole and push it to connect it to the back '
                                          'section of the cylinder'},
        {'Operation': 'F', 'Description': 'Insert the top section in the piston rod and connect it to the barrel'},
        {'Operation': 'G', 'Description': 'Insert screw number three'},
        {'Operation': 'H', 'Description': 'Insert screw number four'},
        {'Operation': 'I', 'Description': 'Screw in the nut in the piston rod'},
        {'Operation': 'J', 'Description': 'Insert the connector push-in fitting'},
        {'Operation': 'K', 'Description': 'Insert the connector push-in L-fitting'}
    ]

    df = pd.DataFrame(tab_data)
    st.image('images/op3_connectors.png')
    st.dataframe(df, hide_index=True, use_container_width=True)


def find_quality_orders():
    data_quality_orders = collection22.find({}, {'_id': 0, 'Number': 1, 'Order Line': 1,
                                                 'Reference': 1, 'Delivery date': 1, 'Description': 1, 'Model': 1,
                                                 'Quantity': 1, 'Color': 1, 'Dimensions': 1})

    for row in data_quality_orders:
        quality_orders = collection3.insert_one(
            {'Number': row['Number'],
             'Order Line': row['Order Line'], 'Reference': row['Reference'], 'Delivery date': row['Delivery date'],
             'Description': row['Description'], 'Model': row['Model'],
             'Quantity': row['Quantity'], 'Color': row['Color'], 'Dimensions': row['Dimensions']})

    collection22.drop()


def fetch_order_info():
    document = collection18.find_one()
    game_phase = document.get('Game Phase')

    id_game1 = "Waiting"
    id_game2 = "Waiting"

    search = collection21.find_one()
    if search:
        id_game1 = search["Order Number"]
        id_game2 = search["Order Line"]

    count = collection21.count_documents({})
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c6:
        st.button(f"Queue: {count}", type="primary")

    with st.container(border=True):
        if game_phase == "Game 1":
            st.write(f':blue[Next order to assemble: ] {id_game1}')

        if game_phase == "Game 2":
            st.write(f':blue[Next order to assemble: ] {id_game2}')

    return game_phase, id_game1, id_game2


def handle_buttons(game_phase, id_game1, id_game2):
    global game2_label, game1_label, game1_list, game2_list, final, numbers_to_delete
    c1, c2, c3, c4 = st.columns(4)
    numbers_list = []

    if 'start_assembly' in st.session_state and st.session_state.start_assembly is True:
        st.session_state.running = True
    else:
        st.session_state.running = False

    with c1:
        start = st.button("Start", key='start_assembly', use_container_width=True, type="primary",
                          help='Click here when you start picking the materials.', disabled=st.session_state.running)
        if start:
            final = True

            if game_phase == "Game 1":
                if len(numbers_list) > 0:
                    for number in numbers_list:
                        collection22.delete_one({"Number": number})

                game1_label = id_game1
                game1_number_search = collection21.find({'Order Number': game1_label},
                                                        {'_id': 0, 'Order Number': 1})

                game1_list = list(game1_number_search)

                find_for_quality = collection21.find({'Order Number': game1_label},
                                                     {'_id': 0, 'Order Number': 1, 'Quantity': 1, 'Model': 1})

                for doc in find_for_quality:
                    collection21.delete_one(doc)

                search = collection21.find_one()

                if search:
                    id_game1 = search["Order Number"]
                    id_game2 = search["Order Number"]

                else:
                    id_game1 = "Waiting"
                    id_game2 = "Waiting"
                st_autorefresh(limit=2, key=f"{id_game1}")

                numbers_list = []

                if game1_list:
                    for order in game1_list:
                        order_number = order.get('Order Number')
                        numbers_list.append(order_number)

                for number in numbers_list:
                    find_for_quality = collection22.find({'Number': number},
                                                         {'_id': 0, 'Number': 1,
                                                          'Order Line': 1, 'Reference': 1, 'Delivery date': 1,
                                                          'Description': 1, 'Model': 1, 'Quantity': 1,
                                                          'Color': 1, 'Dimensions': 1})

                    for doc in find_for_quality:
                        collection3.insert_one(doc)

            if game_phase == "Game 2":

                if len(numbers_list) > 0:
                    for number in numbers_list:
                        collection22.delete_one({"Number": number})

                if len(numbers_to_delete) > 0:
                    for number in numbers_to_delete:
                        collection22.delete_one({"Number": number})
                        numbers_to_delete = []

                game2_label = id_game2
                game2_number_search = collection21.find_one({'Order Line': game2_label},
                                                            {'_id': 0, 'Order Line': 1})

                game2_number_search_as_list = [game2_number_search] if game2_number_search else []

                game2_list = list(game2_number_search_as_list)

                find_for_quality = collection21.find_one({'Order Line': game2_label},
                                                         {'_id': 0, 'Order Number': 1, 'Order Line': 1,
                                                          'Quantity': 1, 'Model': 1})

                if find_for_quality is not None:
                    collection21.delete_one(find_for_quality)
                st_autorefresh(limit=2)

                search = collection21.find_one()

                if search:
                    id_game1 = search["Order Number"]
                    id_game2 = search["Order Number"]

                else:
                    id_game1 = "Waiting"
                    id_game2 = "Waiting"
                st_autorefresh(limit=2, key=f"{id_game2}")

                numbers_list = []

                if game2_list:
                    for order in game2_list:
                        order_number = order.get('Order Line')
                        numbers_list.append(order_number)
                        numbers_to_delete.append(order_number)

                for number in numbers_list:
                    find_for_quality = collection22.find_one({'Order Line': number},
                                                             {'_id': 0, 'Number': 1,
                                                              'Order Line': 1, 'Reference': 1, 'Delivery date': 1,
                                                              'Description': 1, 'Model': 1, 'Quantity': 1,
                                                              'Color': 1, 'Dimensions': 1})

                    collection3.insert_one(find_for_quality)

    return id_game1


def display_images(game_phase):
    global game2_label, game1_label, game1_list, game2_list, final

    if not final:
        st.caption(f"Waiting for the next order to assemble.")

    else:
        if game_phase == "Game 1":
            st.caption(f"The order being assembled is: {game1_label}")

            numbers_list = []
            df_numbers = []

            if game1_list:
                for order in game1_list:
                    order_number = order.get('Order Number')
                    numbers_list.append(order_number)

                for number in numbers_list:
                    find_number = collection22.find({'Number': number},
                                                    {'_id': 0, 'Number': 1, 'Order Line': 1,
                                                     'Reference': 1, 'Delivery date': 1,
                                                     'Description': 1, 'Model': 1, 'Quantity': 1,
                                                     'Color': 1, 'Dimensions': 1})
                    df_numbers.extend(list(find_number))

                rows_df = pd.DataFrame(df_numbers)

                if 'Quantity' in rows_df.columns:
                    columns = ['Number', 'Order Line', 'Reference', 'Quantity', 'Delivery date',
                               'Model', 'Description', 'Color', 'Dimensions']
                    rows_df = rows_df.reindex(columns=columns)

                rows_df = rows_df.rename(columns={
                    'Number': 'Number',
                    'Reference': 'Reference'
                })

                st.dataframe(rows_df,
                             column_config={
                                 "Number": "Number",
                                 "Order Line": "Order line",
                                 'Reference': "Reference",
                                 'Quantity': "Quantity",
                                 'Delivery date': "Delivery date",
                                 'Model': "Model",
                                 'Description': "Description",
                                 'Color': "Color",
                                 'Dimensions': "Dimensions"
                             },
                             hide_index=True)

        if game_phase == "Game 2":
            st.caption(f"The order being assembled is: {game2_label}")

            numbers_list = []
            df_numbers = []

            if game2_list:
                for order in game2_list:
                    order_number = order.get('Order Line')

                    numbers_list.append(order_number)

                for number in numbers_list:
                    find_number = collection22.find_one({'Order Line': number},
                                                        {'_id': 0, 'Number': 1, 'Order Line': 1,
                                                         'Reference': 1, 'Delivery date': 1, 'Description': 1,
                                                         'Model': 1,
                                                         'Quantity': 1, 'Color': 1, 'Dimensions': 1})

                    find_number_as_list = [find_number] if find_number else []
                    df_numbers.extend(list(find_number_as_list))

                rows_df = pd.DataFrame(df_numbers)

                if 'Quantity' in rows_df.columns:
                    columns = ['Number', 'Order Line', 'Reference', 'Quantity', 'Delivery date',
                               'Model', 'Description', 'Color', 'Dimensions']

                    rows_df = rows_df.reindex(columns=columns)

                rows_df = rows_df.rename(columns={
                    'Number': 'Number',
                    'Reference': 'Reference'
                })

                st.dataframe(rows_df,
                             column_config={
                                 "Number": "Number",
                                 "Order Line": "Order line",
                                 'Reference': "Reference",
                                 'Quantity': "Quantity",
                                 'Delivery date': "Delivery date",
                                 'Model': "Model",
                                 'Description': "Description",
                                 'Color': "Color",
                                 'Dimensions': "Dimensions"
                             },
                             hide_index=True)
