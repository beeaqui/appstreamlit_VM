import streamlit as st
from pymongo import MongoClient
from streamlit_autorefresh import st_autorefresh
import pandas as pd

quantities = [0, 0, 0, 0, 0, 0, 0, 0]
game2_label = ""
game1_label = ""
game1_list = []
game2_list = []

client = MongoClient("mongodb://localhost:27017/")
db = client['local']
collection18 = db['GamePhaseConfig']
collection19 = db['LogisticsOrders']
collection20 = db['LogisticsOrdersProcess']
collection21 = db['AssemblyOrders']
collection22 = db['AssemblyOrdersProcess']
collection23 = db['SaveOrdersLogistics']


def find_logistics_orders():
    data_logistics_orders = collection23.find({}, {'_id': 0, 'Number': 1, 'Order Line': 1,
                                                   'Reference': 1, 'Delivery date': 1, 'Time gap': 1, 'Description': 1,
                                                   'Model': 1, 'Quantity': 1, 'Color': 1, 'Dimensions': 1})

    for row in data_logistics_orders:
        if not collection20.find_one({'Number': row['Number'], 'Reference': row['Reference']}):
            collection20.insert_one(
                {'Number': row['Number'], 'Order Line': row['Order Line'], 'Reference': row['Reference'],
                 'Delivery date': row['Delivery date'],
                 'Description': row['Description'], 'Model': row['Model'],
                 'Quantity': row['Quantity'], 'Color': row['Color'], 'Dimensions': row['Dimensions']}
            )


def fetch_order_info():
    global quantities
    document = collection18.find_one()
    game_phase = document.get('Game Phase')

    id_game1 = "Waiting"
    id_game2 = "Waiting"

    search = collection19.find_one()
    if search:
        id_game1 = search["Order Number"]
        id_game2 = search["Order Line"]

    count = collection19.count_documents({})
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c6:
        st.button(f"Queue: {count}", type="primary")

    with st.container(border=True):
        if game_phase == "Game 1":
            st.write(f':blue[Next order to pick: ] {id_game1}')

        if game_phase == "Game 2":
            st.write(f':blue[Next order to pick: ] {id_game2}')

    return game_phase, id_game1, id_game2


def handle_buttons(game_phase, id_game1, id_game2):
    global quantities, game2_label, game1_label, game1_list, game2_list
    c1, c2, c3, c4 = st.columns(4)

    if 'start_picking' in st.session_state and st.session_state.start_picking is True:
        st.session_state.running = True
    else:
        st.session_state.running = False

    with c1:
        start = st.button("Start", key='start_picking', use_container_width=True, type="primary",
                          help='Click here when you start picking the materials.', disabled=st.session_state.running)

        if start:
            if game_phase == "Game 1":
                orders = collection19.find({"Order Number": id_game1})
                quantities = [0] * 8
                for order in orders:
                    for i in range(8):
                        quantity_key = f"Quantity {i + 1}"
                        quantities[i] += order.get(quantity_key, 0)

                game1_label = id_game1
                game1_number_search = collection19.find({'Order Number': game1_label},
                                                        {'_id': 0, 'Order Number': 1})

                game1_list = list(game1_number_search)

                find_for_assembly = collection19.find({'Order Number': game1_label},
                                                      {'_id': 0, 'Order Number': 1, 'Order Line': 1, 'Quantity': 1, 'Model': 1})

                for doc in find_for_assembly:
                    collection21.insert_one(doc)

                collection19.delete_one({"Order Number": id_game1})
                st_autorefresh(limit=2, key=f"{id_game1}")

            if game_phase == "Game 2":
                orders = collection19.find_one({"Order Line": id_game2})

                if orders is not None:
                    quantities = [0] * 8
                    for i in range(8):
                        quantity_key = f"Quantity {i + 1}"
                        quantities[i] += orders.get(quantity_key, 0)

                    game2_label = id_game2
                    game2_number_search = collection19.find_one({'Order Line': game2_label},
                                                                {'_id': 0, 'Order Line': 1})

                    game2_number_search_as_list = [game2_number_search] if game2_number_search else []

                    game2_list = list(game2_number_search_as_list)

                    find_for_assembly = collection19.find_one({'Order Line': game2_label},
                                                              {'_id': 0, 'Order Number': 1, 'Order Line': 1,
                                                               'Quantity': 1, 'Model': 1})

                    collection21.insert_one(find_for_assembly)

                    collection19.delete_one({"Order Line": id_game2})
                    st_autorefresh(limit=2)

    if 'stop_picking' in st.session_state and st.session_state.stop_picking is True:
        st.session_state.running = True
    else:
        st.session_state.running = False

    with c2:
        stop = st.button("Finish", key='stop_picking', use_container_width=True, type="primary",
                         help='Click here when you finish picking the materials.', disabled=st.session_state.running)

        if stop:
            if game_phase == "Game 1":
                quantities = [0, 0, 0, 0, 0, 0, 0, 0]

                search = collection19.find_one()

                if search:
                    id_game1 = search["Order Number"]
                    id_game2 = search["Order Number"]

                else:
                    id_game1 = "Waiting"
                    id_game2 = "Waiting"
                    quantities = [0, 0, 0, 0, 0, 0, 0, 0]
                st_autorefresh(limit=2, key=f"{id_game1}")

                numbers_list = []

                if game1_list:
                    for order in game1_list:
                        order_number = order.get('Order Number')
                        numbers_list.append(order_number)

                for number in numbers_list:
                    find_for_assembly = collection20.find({'Number': number},
                                                          {'_id': 0, 'Number': 1,
                                                           'Order Line': 1, 'Reference': 1, 'Delivery date': 1,
                                                           'Description': 1, 'Model': 1, 'Quantity': 1,
                                                           'Color': 1, 'Dimensions': 1})

                    for doc in find_for_assembly:
                        collection22.insert_one(doc)
                    collection20.delete_one({"Number": number})
                    collection23.delete_one({"Number": number})

            if game_phase == "Game 2":
                quantities = [0, 0, 0, 0, 0, 0, 0, 0]

                search = collection19.find_one()

                if search:
                    id_game1 = search["Order Number"]
                    id_game2 = search["Order Line"]

                else:
                    id_game1 = "Waiting"
                    id_game2 = "Waiting"
                    quantities = [0, 0, 0, 0, 0, 0, 0, 0]
                st_autorefresh(limit=2, key=f"{id_game2}")

                numbers_list = []

                if game2_list:
                    for order in game2_list:
                        order_number = order.get('Order Line')
                        numbers_list.append(order_number)

                for number in numbers_list:
                    find_for_assembly = collection20.find_one({'Order Line': number},
                                                              {'_id': 0, 'Number': 1,
                                                               'Order Line': 1, 'Reference': 1, 'Delivery date': 1,
                                                               'Description': 1, 'Model': 1, 'Quantity': 1, 'Color': 1,
                                                               'Dimensions': 1})

                    collection22.insert_one(find_for_assembly)
                    collection20.delete_one({"Order Line": number})
                    collection23.delete_one({"Order Line": number})

    return id_game1


def display_images(game_phase):
    global quantities, game2_label, game1_label, game1_list, game2_list

    if quantities == [0, 0, 0, 0, 0, 0, 0, 0]:
        st.caption(f"Waiting for the next order to pick.")

    else:
        if game_phase == "Game 1":
            st.caption(f"The order being picked is: {game1_label}")

            numbers_list = []
            df_numbers = []

            if game1_list:
                for order in game1_list:
                    order_number = order.get('Order Number')
                    numbers_list.append(order_number)

                for number in numbers_list:
                    find_number = collection20.find({'Number': number},
                                                    {'_id': 0, 'Number': 1, 'Order Line': 1,
                                                     'Reference': 1, 'Delivery date': 1, 'Description': 1, 'Model': 1,
                                                     'Quantity': 1, 'Color': 1, 'Dimensions': 1})
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
                                 'Order Line': 'Order line',
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
            st.caption(f"The order being picked is: {game2_label}")

            numbers_list = []
            df_numbers = []

            if game2_list:
                for order in game2_list:
                    order_number = order.get('Order Line')
                    numbers_list.append(order_number)

                for number in numbers_list:
                    find_number = collection20.find_one({'Order Line': number},
                                                        {'_id': 0, 'Number': 1, 'Order Line': 1,
                                                         'Reference': 1, 'Delivery date': 1, 'Description': 1,
                                                         'Model': 1,
                                                         'Quantity': 1, 'Color': 1, 'Dimensions': 1})
                    find_number_as_list = [find_number] if find_number else []
                    df_numbers.extend(find_number_as_list)

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
                                 'Order Line': 'Order line',
                                 'Reference': "Reference",
                                 'Quantity': "Quantity",
                                 'Delivery date': "Delivery date",
                                 'Model': "Model",
                                 'Description': "Description",
                                 'Color': "Color",
                                 'Dimensions': "Dimensions"
                             },
                             hide_index=True)

    images = [
        'barrel.png', 'bearing_cap.png', 'push_L_fitting.png',
        'piston.png', 'end_cap.png', 'push_in_fitting.png',
        'nut.png', 'swivel_flange.png']

    columns = st.columns(3, gap='medium')

    custom_css = """
            <style>
                .custom-caption {
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: 400;
                    padding: 0.25rem 0.75rem;
                    border-radius: 0.5rem;
                    height: 35px;
                    width: 214px;
                    margin: 0px 0px 5px 0px;
                    line-height: 1.6;
                    color: rgb(49, 51, 63);
                    user-select: none;
                    background-color: rgb(255, 255, 255);
                    border: 1px solid rgba(49, 51, 63, 0.2);
                }
                .custom-caption:hover {
                    border: 1px solid rgb(49, 90, 146);
                    color: rgb(49, 90, 146);
                }
                .custom-caption:active {
                    background-color: rgb(49, 90, 146);
                    color: rgb(255, 255, 255);
                } 
            </style>
        """

    for row in range(3):
        for col in range(3):
            with columns[col]:
                idx = row * 3 + col
                if idx < len(images):
                    st.markdown(custom_css, unsafe_allow_html=True)
                    quantity = quantities[idx] if idx < len(quantities) else 0
                    st.markdown(f"<div class='custom-caption'>Quantity: {quantity}</div>", unsafe_allow_html=True)
                    with st.container(border=True):
                        st.image(f'images/materials/{images[idx]}')
