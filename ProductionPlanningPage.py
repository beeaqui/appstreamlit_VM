from OrdersListFunctions import *
from QualityControlFunctions import *
from ExpeditionFunctions import *


def production_page():
    c = st.container()
    with c:
        update_timer()

    st.title(":gray[Customer Orders]")
    st.write("")

    # Display a message explaining the purpose of the page
    with st.expander("View Detailed Explanation", expanded=True):
        st.markdown(
            '''
            \n This is where you can explore a detailed catalog of **Customer Orders**, 
            each meticulously documented with essential information, as presented in the 
            table below.
            \n At your disposal is the ability to meticulously curate the orders slated for 
            production. This task is simplified through intuitive selection mechanisms, 
            enabling you to focus on a better production workflow.'''
        )
    st.caption("")

    client = MongoClient("mongodb://localhost:27017/")
    db = client['local']
    collection1 = db['ordersCollection']

    count1 = collection1.count_documents({})

    if count1 != 0:

        grid_container = create_grid()
        selected_rows = grid_container["selected_rows"]
        insert_pre(selected_rows)
        st_autorefresh(limit=50, interval=10000, key="aaaa", debounce=False)

        col1, col2, col3 = st.columns(3)

        with col3:
            submit_button = st.button('Order Release', key='selected_rows_button', type='primary',
                                      help='Submit customer orders for production.',
                                      use_container_width=True)
            if submit_button:

                delete_selected_rows(selected_rows)

                insert_selected_rows(selected_rows)

                collection14 = db['PreSelectedOrders']
                collection14.drop()

                insert_datetime_selected_rows(selected_rows)

                st_autorefresh(limit=2, key=f'{selected_rows}')
        st.title("")

        # Display a message indicating where the selected orders will be produced
        st.title(":grey[Orders Released]")

        with st.expander("View Detailed Explanation", expanded=True):
            st.markdown(
                '''
                \n The chosen orders will be displayed below, in **Orders Released** 
                section. This platform provides the tools you need to stay organized and keep your 
                production process on track.'''
            )
        st.caption("")

        client = MongoClient("mongodb://localhost:27017/")
        db = client['local']
        collection2 = db['selectedOrders']
        count = collection2.count_documents({})

        if count != 0:
            # Create a grid container for displaying selected rows of the orders to be printed
            data_frame_selected_rows = create_grid_selected_rows()

            # Directory of PDF file created before with the selected rows
            pdf_filename = r"pdf_files/Selected_Orders_PDF.pdf"

            # Read the PDF file as bytes
            with open(pdf_filename, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()

            with st.expander("Show Details"):
                st.markdown(
                    '''
                    \n Here you can **open** the PDF file with the orders selected to be produced.'''
                )
            st.caption("")

            create_pdf_selected_rows()

            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                # pdf_filename = r"pdf_files/Selected_Orders_PDF.pdf"
                btn = open_pdf_selected_orders()
                if btn:
                    insert_production_finished_rows()
                    find_quality_orders(db=connect_mongodb())

        else:
            st.write("No orders available for production yet.")

    else:
        st.write("There are no customer orders.")

        col1, col2, col3 = st.columns(3)

        with col3:
            submit_button = st.button('Order Release', key='selected_rows_button', type='primary',
                                      help='Submit customer order for production.',
                                      use_container_width=True)

        st.title("")

        # Display a message indicating where the selected orders will be produced
        st.title(":grey[Orders Released]")

        with st.expander("View Detailed Explanation", expanded=True):
            st.markdown(
                '''
                \n The chosen orders will be displayed below, in **Orders Released** 
                section. This platform provides the tools you need to stay organized and keep your 
                production process on track.'''
            )
        st.caption("")

        client = MongoClient("mongodb://localhost:27017/")
        db = client['local']
        collection2 = db['selectedOrders']
        count = collection2.count_documents({})

        if count != 0:
            # Create a grid container for displaying selected rows of the orders to be printed
            data_frame_selected_rows = create_grid_selected_rows()

            # Directory of PDF file created before with the selected rows
            pdf_filename = r"pdf_files/Selected_Orders_PDF.pdf"

            # Read the PDF file as bytes
            with open(pdf_filename, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()

            with st.expander("Show Details"):
                st.markdown(
                    '''
                    \n Here you can **open** the PDF file with the orders selected to be produced.'''
                )
            st.caption("")

            create_pdf_selected_rows()

            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                # pdf_filename = r"pdf_files/Selected_Orders_PDF.pdf"
                btn = open_pdf_selected_orders()
                if btn:
                    insert_production_finished_rows()
                    find_quality_orders(db=connect_mongodb())

        else:
            st.write("No orders available for production yet.")
