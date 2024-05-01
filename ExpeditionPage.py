from ExpeditionFunctions import *
import streamlit as st


def expedition_page():
    st.title(':grey[Expedition]')

    with st.expander("View Detailed Explanation", expanded=True):
        st.markdown('''In this final stage, kindly double-check your order details for accuracy. If 
                    everything is correct, simply click **Dispatched** to authorize shipment.''')
    st.caption("")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c5:
        confirm = st.button('Refresh Data', key=f'refreshExpeditionBtn', type='primary')
        if confirm:
            st_autorefresh(limit=2, key=f"autoRefreshExpedition")

    display_tables_expedition()
