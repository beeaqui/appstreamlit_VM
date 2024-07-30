from AssemblyFunctions import *
import extra_streamlit_components as stx


def assembly_page():
    st.title('Assembly process', help='''
        \n **Note:** Ensure that each step is completed with precision for proper assembly.
        \n If you encounter any issues or have questions, talk with your teammates or call the instructor. ''')

    st.caption("")

    game_phase, id_game1, id_game2 = fetch_order_info()
    handle_buttons(game_phase, id_game1, id_game2)
    display_images(game_phase)

    tab_bar_data = [
        stx.TabBarItemData(id=1, title="Standard cylinder", description=" "),
        stx.TabBarItemData(id=2, title="Push-in cylinder", description=" "),
        stx.TabBarItemData(id=3, title="L-fit cylinder", description=" "),
        stx.TabBarItemData(id=4, title="Dual-fit cylinder", description=" ")]

    chosen_id = stx.tab_bar(data=tab_bar_data, default=1)

    st.title("")

    if chosen_id == "1":
        basic_cylinder_operations()

    elif chosen_id == "2":
        push_fitting_operations()

    elif chosen_id == "3":
        push_l_operations()

    elif chosen_id == "4":
        mixed_connectors_operations()
