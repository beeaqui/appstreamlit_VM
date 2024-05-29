from LogisticsFunctions import *


def logistics_page():
    st.title('Logistics', help='''\n Please pick the listed materials and quantities for the order and deliver them 
    to the designated workstations. Ensure accuracy and timeliness in your task. ''')

    game_phase, id_game1, id_game2 = fetch_order_info()
    handle_buttons(game_phase, id_game1, id_game2)
    display_images(game_phase)
