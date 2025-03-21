import pandas as pd
import streamlit as st
from pymongo import MongoClient
from streamlit_autorefresh import st_autorefresh

client = MongoClient("mongodb://localhost:27017/")
db = client['local']
collection3 = db['qualityOrders']
collection4 = db['qualityApproved']
collection5 = db['qualityDisapproved']

collection6 = db['expeditionOrders']


def find_quality_rows():
    data_quality_list = collection3.find({}, {'_id': 0, 'Number': 1, 'Order Line': 1,
                                              'Reference': 1, 'Delivery date': 1, 'Description': 1, 'Model': 1,
                                              'Quantity': 1, 'Color': 1, 'Dimensions': 1})

    return data_quality_list


def delete_quality_order(db, order_number):
    collection3.delete_one({'Number': order_number})


def approved_quality_order(db, order_number):
    collection4.insert_one({'Number': order_number['Number'], 'Order Line': order_number['Order Line'],
                            'Reference': order_number['Reference'], 'Delivery date': order_number['Delivery date'],
                            'Description': order_number['Description'], 'Model': order_number['Model'],
                            'Quantity': order_number['Quantity'], 'Color': order_number['Color'],
                            'Dimensions': order_number['Dimensions']})

    collection6.insert_one({'Number': order_number['Number'], 'Order Line': order_number['Order Line'],
                            'Reference': order_number['Reference'], 'Delivery date': order_number['Delivery date'],
                            'Description': order_number['Description'], 'Model': order_number['Model'],
                            'Quantity': order_number['Quantity'], 'Color': order_number['Color'],
                            'Dimensions': order_number['Dimensions']})


def disapproved_quality_order(db, order_number):
    collection5.insert_one({'Number': order_number['Number'], 'Order Line': order_number['Order Line'],
                            'Reference': order_number['Reference'], 'Delivery date': order_number['Delivery date'],
                            'Description': order_number['Description'], 'Model': order_number['Model'],
                            'Quantity': order_number['Quantity'], 'Color': order_number['Color'],
                            'Dimensions': order_number['Dimensions']})


def quality_checks():
    quality_rows = find_quality_rows()

    rows_df = pd.DataFrame(list(quality_rows))

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
        for index, quality_order in enumerate(group):

            with ((columns[index])):
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
                    f"Details - Number {quality_order['Order Line']}</div>",
                    unsafe_allow_html=True)

                data = []

                for key, value in quality_order.items():
                    formatted_key = key.capitalize()
                    data.append({'Attribute': formatted_key, 'Value': value})

                data_frame = pd.DataFrame(data)

                st.dataframe(data_frame, hide_index=True, use_container_width=True)
                c1, c2 = st.columns(2)

                with c1:
                    if f"button_approve{quality_order['Order Line']}" in st.session_state and st.session_state[f"button_approve{quality_order['Order Line']}"] is True:

                        st.session_state.running = True
                    else:
                        st.session_state.running = False
                    approve = st.button('Approve', key=f"button_approve{quality_order['Order Line']}",
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

                        st.toast(f"Order number {quality_order['Order Line']} has been approved", icon='✔️')
                        st_autorefresh(limit=2, key=f"approve{quality_order['Number']}")

                with c2:
                    if f"button_disapprove{quality_order['Order Line']}" in st.session_state and st.session_state[f"button_disapprove{quality_order['Order Line']}"] is True:
                        st.session_state.running = True
                    else:
                        st.session_state.running = False

                    disapprove = st.button('Disapprove', key=f"button_disapprove{quality_order['Order Line']}",
                                           disabled=st.session_state.running)
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

                        st.toast(f"Order number {quality_order['Order Line']} has been disapproved", icon='✖️')
                        st_autorefresh(limit=2, key=f"disapprove{quality_order['Number']}")
