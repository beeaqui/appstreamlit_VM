import os
import streamlit as st
import pandas as pd
from datetime import datetime
from pymongo import MongoClient
import re


from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image
from reportlab.lib import colors


game_phase = ''

client = MongoClient("mongodb://localhost:27017/")
db = client['local']
collection = db['ordersCollection']
collection2 = db['selectedOrders']
collection9 = db['TimeOrderReleased']
collection10 = db['TimeProductionFinished']
collection14 = db['PreSelectedOrders']
collection16 = db['HighPriority']
collection17 = db['MediumPriority']
collection18 = db['GamePhaseConfig']
collection19 = db['LogisticsOrders']
collection23 = db['SaveOrdersLogistics']


def insert_selected_rows(selected_rows):
    for index, row in selected_rows.iterrows():
        selected_orders = collection2.insert_one(
            {'Number': row['Number'], 'Order Line': row['Order Line'],
             'Reference': row['Reference'],
             'Delivery date': row['Delivery date'], 'Time gap': row['Time gap'],
             'Description': row['Description'], 'Model': row['Model'], 'Quantity': row['Quantity'],
             'Color': row['Color'], 'Dimensions': row['Dimensions']})

        logistics_save = collection23.insert_one(
            {'Number': row['Number'], 'Order Line': row['Order Line'],
             'Reference': row['Reference'],
             'Delivery date': row['Delivery date'], 'Time gap': row['Time gap'],
             'Description': row['Description'], 'Model': row['Model'], 'Quantity': row['Quantity'],
             'Color': row['Color'], 'Dimensions': row['Dimensions']})


def insert_logistics_orders(selected_rows):
    for index, row in selected_rows.iterrows():
        if row['Model'] == "Complex cylinder":
            data = collection19.insert_one({"Order Number": row['Number'],
                                            "Order Line": row['Order Line'],
                                            "Quantity": row['Quantity'], "Model": row['Model'],
                                            "Quantity 1": row['Quantity'], "Quantity 2": row['Quantity'],
                                            "Quantity 3": 0,
                                            "Quantity 4": row['Quantity'], "Quantity 5": row['Quantity'],
                                            "Quantity 6": 0,
                                            "Quantity 7": row['Quantity'],
                                            "Quantity 8": row['Quantity'],
                                            })

        if row['Model'] == "Push-in cylinder":
            data = collection19.insert_one({"Order Number": row['Number'],
                                            "Order Line": row['Order Line'],
                                            "Quantity": row['Quantity'], "Model": row['Model'],
                                            "Quantity 1": row['Quantity'], "Quantity 2": row['Quantity'],
                                            "Quantity 3": 0,
                                            "Quantity 4": row['Quantity'], "Quantity 5": row['Quantity'],
                                            "Quantity 6": row['Quantity'] * 2,
                                            "Quantity 7": row['Quantity'],
                                            "Quantity 8": 0,
                                            })

        if row['Model'] == "L-fit cylinder":
            data = collection19.insert_one({"Order Number": row['Number'],
                                            "Order Line": row['Order Line'],
                                            "Quantity": row['Quantity'], "Model": row['Model'],
                                            "Quantity 1": row['Quantity'], "Quantity 2": row['Quantity'],
                                            "Quantity 3": row['Quantity'] * 2,
                                            "Quantity 4": row['Quantity'], "Quantity 5": row['Quantity'],
                                            "Quantity 6": 0,
                                            "Quantity 7": row['Quantity'],
                                            "Quantity 8": 0,
                                            })

        if row['Model'] == "Dual-fit cylinder":
            data = collection19.insert_one({"Order Number": row['Number'],
                                            "Order Line": row['Order Line'],
                                            "Quantity": row['Quantity'], "Model": row['Model'],
                                            "Quantity 1": row['Quantity'], "Quantity 2": row['Quantity'],
                                            "Quantity 3": row['Quantity'],
                                            "Quantity 4": row['Quantity'], "Quantity 5": row['Quantity'],
                                            "Quantity 6": row['Quantity'],
                                            "Quantity 7": row['Quantity'],
                                            "Quantity 8": 0,
                                            })


def insert_datetime_selected_rows(selected_rows):
    order_numbers = []
    order_lines = []

    current_datetime = datetime.now()
    current_date = current_datetime.strftime("%Y-%m-%d")
    current_time = current_datetime.strftime("%H:%M:%S")

    for index, row in selected_rows.iterrows():
        order_number = row['Number']
        order_line = row['Order Line']

        data_to_insert = {
            'Order Number': order_number,
            'Order Line': order_line,
            'Total Orders': 1,
            'Released Order Time': {
                'Date': current_date,
                'Time': current_time
            }
        }

        collection9.insert_one(data_to_insert)


def delete_selected_rows(selected_rows):
    for index, row in selected_rows.iterrows():
        my_row = {'order_line': row['Order Line']}
        collection.delete_one(my_row)


def find_data_order():

    data = collection.find({}, {'_id': 0, 'number': 1, 'order_line': 1,
                                'reference': 1, 'delivery_date': 1, 'time_gap': 1, 'description': 1,
                                'model': 1, 'quantity': 1, 'color': 1, 'dimensions': 1})
    return data


def insert_pre(selected_rows):
    collection14.drop()

    for index, row in selected_rows.iterrows():
        existing_document = collection14.find_one({'Order Line': row['Order Line']})

        if not existing_document:
            ppselected_orders = collection14.insert_one({'Order Line': row['Order Line']})


def find_pre(order_df, table_ids_selected):
    pred = collection14.find({}, {'_id': 0, 'Order Line': 1})
    df_pre_selected = pd.DataFrame(list(pred))

    if df_pre_selected.empty:
        re_selected_orders = []
    else:
        re_selected_orders = df_pre_selected['Order Line']

        for number in re_selected_orders:

            if number in order_df['Order Line'].values:
                position = order_df.index[order_df['Order Line'] == number][0]
                table_ids_selected[str(position)] = True

    return table_ids_selected


def create_grid():
    global game_phase
    document = collection18.find_one()
    game_phase = document.get('Game Phase')

    data = find_data_order()

    order_df = pd.DataFrame(find_data_order(),
                            columns=['number', 'order_line', 'reference', 'delivery_date', 'time_gap', 'description',
                                     'model', 'quantity', 'color', 'dimensions'])

    order_df = order_df.rename(columns={
        'number': 'Number', 'order_line': 'Order Line', 'reference': 'Reference',
        'delivery_date': 'Delivery date', 'time_gap': 'Time gap', 'description': 'Description',
        'model': 'Model', 'quantity': 'Quantity', 'color': 'Color', 'dimensions': 'Dimensions'
    })

    cursor1 = collection16.find()
    cursor2 = collection17.find()

    for document in cursor1:
        param1 = document['High Priority']

    for document in cursor2:
        param2 = document["Medium Priority"]

    def get_color(time_gap):
        if pd.isna(time_gap):
            return ''

        time_gap = str(time_gap)

        time_cleaned = re.sub(r'[^0-9:]', '', time_gap)

        if not time_cleaned:
            return 'background-color: rgb(255, 255, 255);'

        time_parts = list(map(int, time_cleaned.split(":")))

        while len(time_parts) < 3:
            time_parts.append(0)

        total_hours = time_parts[0] + time_parts[1] / 60 + time_parts[2] / 3600
        if total_hours <= param1:
            return 'background-color: rgb(213, 96, 98);'  # High Priority
        elif total_hours <= param2:
            return 'background-color: rgb(244, 211, 94);'  # Medium Priority
        return 'background-color: rgb(255, 255, 255);'

    table_ids_selected = {}

    table_ids_selected = find_pre(order_df, table_ids_selected)

    if "selected_rows" not in st.session_state:
        st.session_state.selected_rows = []
    order_df['Select'] = order_df.index.isin(st.session_state.selected_rows)

    column_order = ['Select', 'Number', 'Order Line', 'Delivery date', 'Time gap',
                    'Quantity', 'Model', 'Reference', 'Description', 'Color', 'Dimensions']
    order_df = order_df[column_order]

    styled_order_df = order_df.style.applymap(get_color, subset=['Time gap'])

    grid_container = st.data_editor(
        styled_order_df,
        hide_index=True,
        column_config={"Select": st.column_config.CheckboxColumn(required=True)},
        disabled=[col for col in order_df.columns if col != 'Select'],
    )

    selected_rows = grid_container[grid_container['Select']]

    st.session_state.selected_rows = selected_rows['Order Line'].tolist()

    return grid_container


def find_selected_rows():

    data_selected_rows = collection2.find({}, {'_id': 0, 'Number': 1, 'Order Line': 1,
                                               'Reference': 1,
                                               'Delivery date': 1, 'Time gap': 1, 'Description': 1, 'Model': 1,
                                               'Quantity': 1, 'Color': 1, 'Dimensions': 1})

    return data_selected_rows


def create_grid_selected_rows():
    selected_rows = find_selected_rows()

    rows_df = pd.DataFrame(list(selected_rows))
    if 'Time gap' in rows_df.columns:
        rows_df = rows_df.drop(columns=['Time gap'])
    if 'Color' in rows_df.columns:
        rows_df = rows_df.drop(columns=['Color'])
    if 'Dimensions' in rows_df.columns:
        rows_df = rows_df.drop(columns=['Dimensions'])

    if 'Quantity' in rows_df.columns:
        columns = ['Number', 'Order Line', 'Reference', 'Quantity', 'Delivery date', 'Model',
                   'Description']
        rows_df = rows_df.reindex(columns=columns)

    rows_df = rows_df.rename(columns={
        'Number': 'Number',
        'Reference': 'Reference'
    })

    column_order = ['Number', 'Order Line', 'Delivery date',
                    'Quantity', 'Model', 'Reference', 'Description']
    rows_df = rows_df[column_order]

    data_frame_selected_rows = st.dataframe(rows_df,
                                            column_config={
                                                "Number": "Number",
                                                "Order Line": "Order Line",
                                                'Reference': "Reference",
                                                'Quantity': "Quantity",
                                                'Delivery date': "Delivery date",
                                                'Model': "Model",
                                                'Description': "Description"

                                            },
                                            hide_index=True)

    return data_frame_selected_rows


def create_pdf_selected_rows():
    selected_rows = find_selected_rows()

    rows_df = pd.DataFrame(list(selected_rows))

    script_dir = os.path.dirname(os.path.realpath(__file__))

    image = r"images/PDF_planning_orders1.png"

    pdf_filename = os.path.join(script_dir, "pdf_files/Selected_Orders_PDF.pdf")
    pdf = SimpleDocTemplate(pdf_filename, pagesize=landscape(letter))

    story = []

    img_width = 792
    img_height = 218

    img = Image(image, width=img_width, height=img_height)

    data = [rows_df.columns.tolist()] + rows_df.values.tolist()

    table = Table(data)

    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])

    table.setStyle(style)

    story.append(img)
    story.append(table)

    pdf.build(story)

    return pdf_filename


def open_pdf_selected_orders():
    pdf_filename = "pdf_files/Selected_Orders_PDF.pdf"

    with open("pdf_files/Selected_Orders_PDF.pdf", "rb") as file:
        btn = st.download_button(
            label="Download",
            data=file,
            file_name="Production_Order.pdf"
        )
    return btn


def insert_production_finished_rows(selected_rows):
    order_numbers = []
    order_lines = []

    current_datetime = datetime.now()
    current_date = current_datetime.strftime("%Y-%m-%d")
    current_time = current_datetime.strftime("%H:%M:%S")

    data_to_insert = {
        'Order Number': [],
        'Order Line': [],
        'Total Orders': 0,
        'Production Finished Time': {
            'Date': current_date,
            'Time': current_time
        }
    }

    for index, row in selected_rows.iterrows():
        order_number = row['Number']
        order_numbers.append(order_number)
        order_line = row['Order Line']
        order_lines.append(order_line)

        data_to_insert['Order Number'] = order_numbers
        data_to_insert['Order Line'] = order_lines
        data_to_insert['Total Orders'] = len(order_numbers)

    collection10.insert_one(data_to_insert)
