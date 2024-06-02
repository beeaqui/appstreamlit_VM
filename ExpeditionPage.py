from ExpeditionFunctions import *
import streamlit as st


def expedition_page():
    st.title(':grey[Expedition]', help='''In this final stage, kindly double-check your order details for accuracy. If 
                    everything is correct, simply click **Dispatched** to authorize shipment.''')

    st.caption("")

    st_autorefresh(limit=2, interval=20000, key=f"autoRefreshExpedition")

    display_tables_expedition()
