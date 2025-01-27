import pandas as pd
import streamlit as st
from pymongo import MongoClient
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

from OptimizationFunctions import cumulative_finished_orders

client = MongoClient("mongodb://localhost:27017/")
db = client['local']
collection6 = db['expeditionOrders']
collection7 = db['ordersConcluded']
collection11 = db['TimeExpeditionEnd']


def find_expedition_orders():
    expedition_orders = collection6.find({}, {'_id': 0, 'Number': 1, 'Order Line': 1,
                                              'Reference': 1, 'Delivery date': 1, 'Description': 1, 'Model': 1,
                                              'Quantity': 1, 'Color': 1, 'Dimensions': 1})

    return expedition_orders


def delete_expedition_order(db, order_number):
    collection6.delete_one({'Number': order_number})


def concluded_orders(db, order_number):
    collection7.insert_one({'Number': order_number['Number'], 'Order Line': order_number['Order Line'],
                            'Reference': order_number['Reference'], 'Delivery date': order_number['Delivery date'],
                            'Description': order_number['Description'], 'Model': order_number['Model'],
                            'Quantity': order_number['Quantity'], 'Color': order_number['Color'],
                            'Dimensions': order_number['Dimensions']})


def display_tables_expedition():
    collection6 = db['expeditionOrders']

    expedition_orders = find_expedition_orders()

    rows_df = pd.DataFrame(list(expedition_orders))

    if 'Quantity' in rows_df.columns:
        columns = ['Number', 'Order Line', 'Reference', 'Quantity', 'Delivery date', 'Model',
                   'Description', 'Color', 'Dimensions']
        rows_df = rows_df.reindex(columns=columns)

        column_order = ['Number', 'Order Line', 'Delivery date',
                        'Quantity', 'Model', 'Reference', 'Description', 'Color', 'Dimensions']
        rows_df = rows_df[column_order]

    data_groups = [list(rows_df.iloc[i:i + 2].to_dict(orient='records')) for i in range(0, len(rows_df), 2)]

    for group in data_groups:
        columns = st.columns(2)
        for index, expedition_order in enumerate(group):

            with columns[index]:
                st.markdown(
                    f"<div style='text-align: center; "
                    f"color: rgb(49, 51, 63); "
                    f"font-size: 14px; "
                    f"font-weight: bold; "
                    f"background-color: #F0F2F6; "
                    f"padding: 10px; "
                    f"border-radius: 10px; "
                    f"margin-top: 50px; "
                    f"margin-bottom: 10px;'>"
                    f"Details - Number {expedition_order['Order Line']}</div>",
                    unsafe_allow_html=True)

                data = []

                for key, value in expedition_order.items():
                    formatted_key = key.capitalize()
                    data.append({'Attribute': formatted_key, 'Value': value})

                data_frame = pd.DataFrame(data)
                st.dataframe(data_frame, hide_index=True, use_container_width=True)

                c1, c2, c3 = st.columns(3)
                with c2:
                    if f"button_ship{expedition_order['Order Line']}" in st.session_state and st.session_state[
                        f"button_ship{expedition_order['Order Line']}"] is True:
                        st.session_state.running = True
                    else:
                        st.session_state.running = False

                    confirm = st.button('Dispatch', key=f"button_ship{expedition_order['Order Line']}",
                                        type='primary')
                    if confirm:
                        concluded_orders(db, expedition_order)
                        insert_confirmation_data(expedition_order['Number'])
                        delete_expedition_order(db, expedition_order['Number'])

                        st.toast(f"Order number {expedition_order['Order Line']} has been successfully shipped",
                                 icon='✔️')
                        st_autorefresh(limit=2, key=f"{expedition_order['Number']}")
                        cumulative_finished_orders(db)


def insert_confirmation_data(order_number):
    current_datetime = datetime.now()
    current_date = current_datetime.strftime("%Y-%m-%d")
    current_time = current_datetime.strftime("%H:%M:%S")

    order_data = collection6.find_one({'Number': order_number}, {'_id': 0, 'Order Line': 1})
    order_line = order_data.get('Order Line', 'No Order Line Provided')

    data_to_insert = {
        'Order Number': order_number,
        'Order Line': order_line,
        'Total Orders': 1,
        'End Expedition Time': {
            'Date': current_date,
            'Time': current_time
        }
    }

    collection11.insert_one(data_to_insert)
