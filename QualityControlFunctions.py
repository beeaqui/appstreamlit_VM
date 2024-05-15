# Imports
import pandas as pd
import streamlit as st
from pymongo import MongoClient
from streamlit_autorefresh import st_autorefresh


def connect_mongodb():
    client = MongoClient("mongodb://localhost:27017/")

    db = client['local']
    return db


def find_quality_orders(db):
    collection2 = db['selectedOrders']
    collection3 = db['qualityOrders']
    # collection3.drop()

    data_quality_orders = collection2.find({}, {'_id': 0, 'Number': 1, 'Reference': 1, 'Delivery Date': 1,
                                                'Time Gap': 1, 'Description': 1, 'Model': 1, 'Quantity': 1,
                                                'Color': 1, 'Dimensions': 1})

    for row in data_quality_orders:
        quality_orders = collection3.insert_one(
            {'Number': row['Number'], 'Reference': row['Reference'], 'Delivery Date': row['Delivery Date'],
             'Time Gap': row['Time Gap'], 'Description': row['Description'], 'Model': row['Model'],
             'Quantity': row['Quantity'], 'Color': row['Color'], 'Dimensions': row['Dimensions']})

    collection2.drop()
    st_autorefresh(limit=2)


def find_quality_rows(db):
    collection3 = db['qualityOrders']

    # Select all variables from the orders except for id
    data_quality_orders = collection3.find({}, {'_id': 0, 'Number': 1, 'Reference': 1, 'Delivery Date': 1,
                                                'Time Gap': 1, 'Description': 1, 'Model': 1, 'Quantity': 1,
                                                'Color': 1, 'Dimensions': 1})
    data_quality_list = list(data_quality_orders)

    return data_quality_list


def delete_quality_order(db, order_number):
    collection3 = db['qualityOrders']
    collection3.delete_one({'Number': order_number})


def approved_quality_order(db, order_number):
    collection4 = db['qualityApproved']
    collection4.insert_one({'Number': order_number['Number'], 'Reference': order_number['Reference'],
                            'Delivery Date': order_number['Delivery Date'], 'Time Gap': order_number['Time Gap'],
                            'Description': order_number['Description'], 'Model': order_number['Model'],
                            'Quantity': order_number['Quantity'], 'Color': order_number['Color'],
                            'Dimensions': order_number['Dimensions']})

    collection6 = db['expeditionOrders']
    collection6.insert_one({'Number': order_number['Number'], 'Reference': order_number['Reference'],
                            'Delivery Date': order_number['Delivery Date'], 'Time Gap': order_number['Time Gap'],
                            'Description': order_number['Description'], 'Model': order_number['Model'],
                            'Quantity': order_number['Quantity'], 'Color': order_number['Color'],
                            'Dimensions': order_number['Dimensions']})


def disapproved_quality_order(db, order_number):
    collection5 = db['qualityDisapproved']
    collection5.insert_one({'Number': order_number['Number'], 'Reference': order_number['Reference'],
                            'Delivery Date': order_number['Delivery Date'], 'Time Gap': order_number['Time Gap'],
                            'Description': order_number['Description'], 'Model': order_number['Model'],
                            'Quantity': order_number['Quantity'], 'Color': order_number['Color'],
                            'Dimensions': order_number['Dimensions']})


def quality_checks():
    db = connect_mongodb()
    collection3 = db['qualityOrders']

    quality_rows = find_quality_rows(db)

    data_groups = [quality_rows[i:i + 2] for i in range(0, len(quality_rows), 2)]

    for group in data_groups:
        columns = st.columns(2)
        for index, quality_order in enumerate(group):

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
                    f"Details - Order {quality_order['Number']}</div>",
                    unsafe_allow_html=True)

                data = []

                for key, value in quality_order.items():
                    formatted_key = key.capitalize()
                    data.append({'Attribute': formatted_key, 'Value': value})

                data_frame = pd.DataFrame(data)
                st.dataframe(data_frame, hide_index=True, use_container_width=True)

                c1, c2 = st.columns(2)
                with c1:

                    approve = st.button('Approve', key=f"button_approve{quality_order['Number']}",
                                        use_container_width=True)
                    st.markdown(
                        """
                        <style>
                            .st-emotion-cache-1jwswwm.ef3psqc12 {
                                display: flex;
                                -webkit-box-align: center;
                                align-items: center;
                                -webkit-box-pack: center;
                                justify-content: center;
                                font-weight: 400;
                                padding: 0.25rem 0.75rem;
                                border-radius: 0.5rem;
                                min-height: 38.4px;
                                margin: 0px;
                                line-height: 1.6;
                                color: rgb(255, 255, 255);
                                width: 164px;
                                user-select: none;
                                background-color: rgb(51, 115, 87);
                                border: 1px solid rgb(51, 115, 87);
                                color: rgb(255, 255, 255)
                            }

                            .st-emotion-cache-1jwswwm.ef3psqc12:hover {
                                border: 1px solid rgb(51, 115, 87);
                                background-color: rgb(255, 255, 255);
                                color: rgb(51, 115, 87)
                            }

                            .st-emotion-cache-1jwswwm.ef3psqc12:focus {
                                border: 1px solid rgb(51, 115, 87);
                                background-color: rgb(255, 255, 255);
                                color: rgb(51, 115, 87)
                            }

                            .st-emotion-cache-1jwswwm.ef3psqc12:selected {
                                border: 1px solid rgb(51, 115, 87);
                                background-color: rgb(255, 255, 255);
                                color: rgb(51, 115, 87)
                            }

                            .st-emotion-cache-1jwswwm.ef3psqc12:active {
                                border: 1px solid rgb(51, 115, 87);
                                background-color: rgb(51, 115, 87);
                                color: rgb(255, 255, 255)
                            }   


                        </style>
                    """,
                        unsafe_allow_html=True)

                    if approve:
                        approved_quality_order(db, quality_order)
                        delete_quality_order(db, quality_order['Number'])

                        st.toast(f"Order number {quality_order['Number']} has been approved", icon='✔️')
                        st_autorefresh(limit=2, key=f"approve{quality_order['Number']}")

                with c2:
                    disapprove = st.button('Disapprove', key=f"button_disapprove{quality_order['Number']}")
                    st.markdown(
                        """
                        <style>
                            .st-emotion-cache-wk66hx.ef3psqc12 {
                                display: flex;
                                -webkit-box-align: center;
                                align-items: center;
                                -webkit-box-pack: center;
                                justify-content: center;
                                font-weight: 400;
                                padding: 0.25rem 0.75rem;
                                border-radius: 0.5rem;
                                min-height: 38.4px;
                                margin: 0px;
                                line-height: 1.6;
                                color: rgb(255, 255, 255);
                                width: 164px;
                                user-select: none;
                                background-color: rgb(135, 61, 72);
                                border: 1px solid rgb(135, 61, 72);
                                color: rgb(255, 255, 255)
                            }

                            .st-emotion-cache-wk66hx.ef3psqc12:hover {
                                border: 1px solid rgb(135, 61, 72);
                                background-color: rgb(255, 255, 255);
                                color: rgb(135, 61, 72)
                            }

                            .st-emotion-cache-wk66hx.ef3psqc12:focus {
                                border: 1px solid rgb(135, 61, 72);
                                background-color: rgb(255, 255, 255);
                                color: rgb(135, 61, 72)
                            }

                            .st-emotion-cache-wk66hx.ef3psqc12:selected {
                                border: 1px solid rgb(135, 61, 72);
                                background-color: rgb(255, 255, 255);
                                color: rgb(135, 61, 72)
                            }

                            .st-emotion-cache-wk66hx.ef3psqc12:active {
                                border: 1px solid rgb(135, 61, 72);
                                background-color: rgb(135, 61, 72);
                                color: rgb(255, 255, 255)
                            }   


                        </style>
                    """,
                        unsafe_allow_html=True)

                    if disapprove:
                        disapproved_quality_order(db, quality_order)
                        delete_quality_order(db, quality_order['Number'])

                        st.toast(f"Order number {quality_order['Number']} has been disapproved", icon='✖️')
                        st_autorefresh(limit=2, key=f"disapprove{quality_order['Number']}")
