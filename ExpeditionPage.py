from ExpeditionFunctions import *
from SupervisorFunctions import *
import streamlit as st


def expedition_page():
    st.title(':grey[Expedition]', help='''In this final stage, kindly double-check your order details for accuracy. If 
                    everything is correct, simply click **Dispatched** to authorize shipment.''')

    st.caption("")

    display_tables_expedition()
    total_delay_orders, without_delay = calculate_delay_orders()
