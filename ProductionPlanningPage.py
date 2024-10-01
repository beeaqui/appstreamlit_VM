from ProductionPlanningFunctions import *
from LogisticsFunctions import *


client = MongoClient("mongodb://localhost:27017/")
db = client['local']
collection1 = db['ordersCollection']
collection2 = db['selectedOrders']
collection14 = db['PreSelectedOrders']


def production_page():
    st.title(":gray[Customer orders]",
             help='''\n This is where you can explore a detailed catalog of **Numbers**, 
            each meticulously documented with essential information, as presented in the 
            table below.
            \n At your disposal is the ability to meticulously curate the orders slated for 
            production. This task is simplified through intuitive selection mechanisms, 
            enabling you to focus on a better production workflow.''')

    st.write("")

    count1 = collection1.count_documents({})

    if count1 != 0:
        grid_container = create_grid()
        selected_rows = grid_container[grid_container['Select']]
        insert_pre(selected_rows)
        st_autorefresh(limit=50, interval=10000, key="aaaa", debounce=False)

        col1, col2, col3 = st.columns(3)

        with col1:
            submit_button = st.button('Order release', key='selected_rows_button', type='primary',
                                      help='Submit customer orders for production.',
                                      use_container_width=True)
            if submit_button:
                delete_selected_rows(selected_rows)
                insert_selected_rows(selected_rows)
                st.session_state.selected_rows = []

                insert_logistics_orders(selected_rows)

                find_logistics_orders()

                insert_production_finished_rows(selected_rows)

                collection14.drop()

                insert_datetime_selected_rows(selected_rows)

                st_autorefresh(limit=2, key=f'{selected_rows}')
        st.title("")

        # Display a message indicating where the selected orders will be produced
        st.title(":grey[Orders released]", help='''
                \n The chosen orders will be displayed below, in **Orders released** 
                section. This platform provides the tools you need to stay organized and keep your 
                production process on track.''')

        st.caption("")

        count = collection2.count_documents({})

        if count != 0:
            # Create a grid container for displaying selected rows of the orders to be printed
            data_frame_selected_rows = create_grid_selected_rows()

            # Directory of PDF file created before with the selected rows
            pdf_filename = r"pdf_files/Selected_Orders_PDF.pdf"

            # Read the PDF file as bytes
            with open(pdf_filename, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()

            create_pdf_selected_rows()

            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                # pdf_filename = r"pdf_files/Selected_Orders_PDF.pdf"
                btn = open_pdf_selected_orders()
                if btn:
                    collection2.drop()

        else:
            st.write("No orders available for production yet.")

    else:
        st.write("There are no customer orders.")

        col1, col2, col3 = st.columns(3)

        with col3:
            submit_button = st.button('Order release', key='selected_rows_button', type='primary',
                                      help='Submit customer order for production.',
                                      use_container_width=True)

        st.title("")

        # Display a message indicating where the selected orders will be produced
        st.title(":grey[Orders released]", help='''
                \n The chosen orders will be displayed below, in **Orders released** 
                section. This platform provides the tools you need to stay organized and keep your 
                production process on track.''')

        st.caption("")

        count = collection2.count_documents({})

        if count != 0:
            # Create a grid container for displaying selected rows of the orders to be printed
            data_frame_selected_rows = create_grid_selected_rows()

            # Directory of PDF file created before with the selected rows
            pdf_filename = r"pdf_files/Selected_Orders_PDF.pdf"

            # Read the PDF file as bytes
            with open(pdf_filename, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()

            create_pdf_selected_rows()

            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                # pdf_filename = r"pdf_files/Selected_Orders_PDF.pdf"
                btn = open_pdf_selected_orders()
                if btn:
                    collection2.drop()

        else:
            st.write("No orders available for production yet.")
