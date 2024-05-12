import streamlit as st
import pandas as pd
import extra_streamlit_components as stx


def basic_cylinder_operations():
    tab_bar_data = [
        stx.TabBarItemData(id=1, title="Task 1", description=" "),
        stx.TabBarItemData(id=2, title="Task 2", description=" "),
        stx.TabBarItemData(id=3, title="Task 3", description=" "),
        stx.TabBarItemData(id=4, title="Task 4", description=" "),
        stx.TabBarItemData(id=5, title="Task 5", description=" "),
        stx.TabBarItemData(id=6, title="Task 6", description=" "),
        stx.TabBarItemData(id=7, title="Task 7", description=" "),
        stx.TabBarItemData(id=8, title="Task 8", description=" "),
        stx.TabBarItemData(id=9, title="Task 9", description=" "),
        stx.TabBarItemData(id=10, title="Task 10", description=" ")
    ]

    chosen_id = stx.tab_bar(data=tab_bar_data, default=1)

    tab_data = {
        "1": {'Operation': ['A'], 'Description': ['Position the cylinder barrel in the vertical in a flat surface']},
        "2": {'Operation': ['B'], 'Description': ['Connect the back section and the cylinder barrel']},
        "3": {'Operation': ['C'], 'Description': ['Insert screw number one']},
        "4": {'Operation': ['D'], 'Description': ['Insert screw number two']},
        "5": {'Operation': ['E'], 'Description': [
            'Place the piston in the barrel hole and push it to connect it to the back section of the cylinder']},
        "6": {'Operation': ['F'],
              'Description': ['Insert the top section in the piston rod and connect it to the barrel']},
        "7": {'Operation': ['G'], 'Description': ['Insert screw number three']},
        "8": {'Operation': ['H'], 'Description': ['Insert screw number four']},
        "9": {'Operation': ['I'], 'Description': ['Screw in the nut in the piston rod']},
        "10": {'Operation': ['J'], 'Description': ['Insert the two protections in the air ports']}
    }

    data = tab_data[chosen_id]
    df = pd.DataFrame(data)
    st.dataframe(df, hide_index=True, use_container_width=True)

    st.image('images/cylinder.png')


def push_fitting_operations():
    tab_bar_data = [
        stx.TabBarItemData(id=1, title="Task 1", description=" "),
        stx.TabBarItemData(id=2, title="Task 2", description=" "),
        stx.TabBarItemData(id=3, title="Task 3", description=" "),
        stx.TabBarItemData(id=4, title="Task 4", description=" "),
        stx.TabBarItemData(id=5, title="Task 5", description=" "),
        stx.TabBarItemData(id=6, title="Task 6", description=" "),
        stx.TabBarItemData(id=7, title="Task 7", description=" "),
        stx.TabBarItemData(id=8, title="Task 8", description=" "),
        stx.TabBarItemData(id=9, title="Task 9", description=" "),
        stx.TabBarItemData(id=10, title="Task 10", description=" ")
    ]

    chosen_id = stx.tab_bar(data=tab_bar_data, default=1)

    tab_data = {
        "1": {'Operation': ['A'], 'Description': ['Position the cylinder barrel in the vertical in a flat surface']},
        "2": {'Operation': ['B'], 'Description': ['Connect the back section and the cylinder barrel']},
        "3": {'Operation': ['C'], 'Description': ['Insert screw number one']},
        "4": {'Operation': ['D'], 'Description': ['Insert screw number two']},
        "5": {'Operation': ['E'], 'Description': [
            'Place the piston in the barrel hole and push it to connect it to the back section of the cylinder']},
        "6": {'Operation': ['F'],
              'Description': ['Insert the top section in the piston rod and connect it to the barrel']},
        "7": {'Operation': ['G'], 'Description': ['Insert screw number three']},
        "8": {'Operation': ['H'], 'Description': ['Insert screw number four']},
        "9": {'Operation': ['I'], 'Description': ['Screw in the nut in the piston rod']},
        "10": {'Operation': ['J'], 'Description': ['Insert the two connectors push-in fitting']}
    }

    data = tab_data[chosen_id]
    df = pd.DataFrame(data)
    st.dataframe(df, hide_index=True, use_container_width=True)

    st.image('images/op1_connectors.png')


def push_l_operations():
    tab_bar_data = [
        stx.TabBarItemData(id=1, title="Task 1", description=" "),
        stx.TabBarItemData(id=2, title="Task 2", description=" "),
        stx.TabBarItemData(id=3, title="Task 3", description=" "),
        stx.TabBarItemData(id=4, title="Task 4", description=" "),
        stx.TabBarItemData(id=5, title="Task 5", description=" "),
        stx.TabBarItemData(id=6, title="Task 6", description=" "),
        stx.TabBarItemData(id=7, title="Task 7", description=" "),
        stx.TabBarItemData(id=8, title="Task 8", description=" "),
        stx.TabBarItemData(id=9, title="Task 9", description=" "),
        stx.TabBarItemData(id=10, title="Task 10", description=" ")
    ]

    chosen_id = stx.tab_bar(data=tab_bar_data, default=1)

    tab_data = {
        "1": {'Operation': ['A'], 'Description': ['Position the cylinder barrel in the vertical in a flat surface']},
        "2": {'Operation': ['B'], 'Description': ['Connect the back section and the cylinder barrel']},
        "3": {'Operation': ['C'], 'Description': ['Insert screw number one']},
        "4": {'Operation': ['D'], 'Description': ['Insert screw number two']},
        "5": {'Operation': ['E'], 'Description': [
            'Place the piston in the barrel hole and push it to connect it to the back section of the cylinder']},
        "6": {'Operation': ['F'],
              'Description': ['Insert the top section in the piston rod and connect it to the barrel']},
        "7": {'Operation': ['G'], 'Description': ['Insert screw number three']},
        "8": {'Operation': ['H'], 'Description': ['Insert screw number four']},
        "9": {'Operation': ['I'], 'Description': ['Screw in the nut in the piston rod']},
        "10": {'Operation': ['J'], 'Description': ['Insert the two connectors push-in L-fitting']}
    }

    data = tab_data[chosen_id]
    df = pd.DataFrame(data)
    st.dataframe(df, hide_index=True, use_container_width=True)

    st.image('images/op2_connectors.png')


def mixed_connectors_operations():
    tab_bar_data = [
        stx.TabBarItemData(id=1, title="Task 1", description=" "),
        stx.TabBarItemData(id=2, title="Task 2", description=" "),
        stx.TabBarItemData(id=3, title="Task 3", description=" "),
        stx.TabBarItemData(id=4, title="Task 4", description=" "),
        stx.TabBarItemData(id=5, title="Task 5", description=" "),
        stx.TabBarItemData(id=6, title="Task 6", description=" "),
        stx.TabBarItemData(id=7, title="Task 7", description=" "),
        stx.TabBarItemData(id=8, title="Task 8", description=" "),
        stx.TabBarItemData(id=9, title="Task 9", description=" "),
        stx.TabBarItemData(id=10, title="Task 10", description=" "),
        stx.TabBarItemData(id=11, title="Task 11", description=" ")

    ]

    chosen_id = stx.tab_bar(data=tab_bar_data, default=1)

    tab_data = {
        "1": {'Operation': ['A'], 'Description': ['Position the cylinder barrel in the vertical in a flat surface']},
        "2": {'Operation': ['B'], 'Description': ['Connect the back section and the cylinder barrel']},
        "3": {'Operation': ['C'], 'Description': ['Insert screw number one']},
        "4": {'Operation': ['D'], 'Description': ['Insert screw number two']},
        "5": {'Operation': ['E'], 'Description': [
            'Place the piston in the barrel hole and push it to connect it to the back section of the cylinder']},
        "6": {'Operation': ['F'],
              'Description': ['Insert the top section in the piston rod and connect it to the barrel']},
        "7": {'Operation': ['G'], 'Description': ['Insert screw number three']},
        "8": {'Operation': ['H'], 'Description': ['Insert screw number four']},
        "9": {'Operation': ['I'], 'Description': ['Screw in the nut in the piston rod']},
        "10": {'Operation': ['J'], 'Description': ['Insert the connector push-in fitting']},
        "11": {'Operation': ['K'], 'Description': ['Insert the connector push-in L-fitting']}

    }

    data = tab_data[chosen_id]
    df = pd.DataFrame(data)
    st.dataframe(df, hide_index=True, use_container_width=True)

    st.image('images/op3_connectors.png')
