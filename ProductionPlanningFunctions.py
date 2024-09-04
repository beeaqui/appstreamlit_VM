import os
import streamlit as st
import pandas as pd
from datetime import datetime
from pymongo import MongoClient

from st_aggrid import GridUpdateMode, AgGrid, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from streamlit.components.v1 import html

from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image
from reportlab.lib import colors

# Not used, code in comments
# import subprocess
# import webbrowser
# import streamlit_pdf_viewer as st_pdf

game_phase = ''


def insert_selected_rows(selected_rows):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['local']
    collection2 = db['selectedOrders']
    collection23 = db['SaveOrdersLogistics']

    for row in selected_rows:
        selected_orders = collection2.insert_one(
            {'Number': row['Customer Order'], 'Order Line': row['Order Line'],
             'Reference': row['Product Ref.'],
             'Delivery Date': row['Delivery Date'], 'Time Gap': row['Time Gap'],
             'Description': row['Description'], 'Model': row['Model'], 'Quantity': row['Quantity'],
             'Color': row['Color'], 'Dimensions': row['Dimensions']})

        logistics_save = collection23.insert_one(
            {'Number': row['Customer Order'], 'Order Line': row['Order Line'],
             'Reference': row['Product Ref.'],
             'Delivery Date': row['Delivery Date'], 'Time Gap': row['Time Gap'],
             'Description': row['Description'], 'Model': row['Model'], 'Quantity': row['Quantity'],
             'Color': row['Color'], 'Dimensions': row['Dimensions']})


def insert_logistics_orders(selected_rows):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['local']
    collection19 = db['LogisticsOrders']

    for row in selected_rows:
        if row['Model'] == "Complex cylinder":
            data = collection19.insert_one({"Order Number": row['Customer Order'],
                                            "Quantity": row['Quantity'], "Model": row['Model'],
                                            "Quantity 1": row['Quantity'], "Quantity 2": row['Quantity'],
                                            "Quantity 3": 0,
                                            "Quantity 4": row['Quantity'], "Quantity 5": row['Quantity'],
                                            "Quantity 6": 0,
                                            "Quantity 7": row['Quantity'] * 4, "Quantity 8": row['Quantity'],
                                            "Quantity 9": row['Quantity'],
                                            })

        if row['Model'] == "Push-in cylinder":
            data = collection19.insert_one({"Order Number": row['Customer Order'],
                                            "Quantity": row['Quantity'], "Model": row['Model'],
                                            "Quantity 1": row['Quantity'], "Quantity 2": row['Quantity'],
                                            "Quantity 3": 0,
                                            "Quantity 4": row['Quantity'], "Quantity 5": row['Quantity'],
                                            "Quantity 6": row['Quantity'] * 2,
                                            "Quantity 7": row['Quantity'] * 4, "Quantity 8": row['Quantity'],
                                            "Quantity 9": 0,
                                            })

        if row['Model'] == "L-fit cylinder":
            data = collection19.insert_one({"Order Number": row['Customer Order'],
                                            "Quantity": row['Quantity'], "Model": row['Model'],
                                            "Quantity 1": row['Quantity'], "Quantity 2": row['Quantity'],
                                            "Quantity 3": row['Quantity'] * 2,
                                            "Quantity 4": row['Quantity'], "Quantity 5": row['Quantity'],
                                            "Quantity 6": 0,
                                            "Quantity 7": row['Quantity'] * 4, "Quantity 8": row['Quantity'],
                                            "Quantity 9": 0,
                                            })

        if row['Model'] == "Dual-fit cylinder":
            data = collection19.insert_one({"Order Number": row['Customer Order'],
                                            "Quantity": row['Quantity'], "Model": row['Model'],
                                            "Quantity 1": row['Quantity'], "Quantity 2": row['Quantity'],
                                            "Quantity 3": row['Quantity'],
                                            "Quantity 4": row['Quantity'], "Quantity 5": row['Quantity'],
                                            "Quantity 6": row['Quantity'],
                                            "Quantity 7": row['Quantity'] * 4, "Quantity 8": row['Quantity'],
                                            "Quantity 9": 0,
                                            })


def insert_datetime_selected_rows(selected_rows):
    client = MongoClient("mongodb://localhost:27017/")

    db = client['local']

    collection9 = db['TimeOrderReleased']

    order_numbers = []

    current_datetime = datetime.now()
    current_date = current_datetime.strftime("%Y-%m-%d")
    current_time = current_datetime.strftime("%H:%M:%S")

    data_to_insert = {
        'Orders Number': [],
        'Total Orders': 0,
        'Released Order Time': {
            'Date': current_date,
            'Time': current_time
        }
    }

    for row in selected_rows:
        order_number = row['Customer Order']
        order_numbers.append(order_number)

        data_to_insert['Orders Number'] = order_numbers
        data_to_insert['Total Orders'] = len(order_numbers)

    collection9.insert_one(data_to_insert)


def delete_selected_rows(selected_rows):
    client = MongoClient("mongodb://localhost:27017/")

    db = client['local']

    collection = db['ordersCollection']

    for row in selected_rows:
        my_row = {'number': row['Customer Order']}
        collection.delete_one(my_row)


def find_data_order():
    client = MongoClient("mongodb://localhost:27017/")

    db = client['local']

    collection = db['ordersCollection']

    data = collection.find({}, {'_id': 0, 'number': 1, 'order_line': 1,
                                'reference': 1, 'delivery_date': 1, 'time_gap': 1, 'description': 1,
                                'model': 1, 'quantity': 1, 'color': 1, 'dimensions': 1})
    return data


def insert_pre(selected_rows):
    client = MongoClient("mongodb://localhost:27017/")

    db = client['local']

    collection14 = db['PreSelectedOrders']
    collection14.drop()

    for row in selected_rows:
        existing_document = collection14.find_one({'Number': row['Customer Order']})

        if not existing_document:
            ppselected_orders = collection14.insert_one({'Number': row['Customer Order']})


def find_pre(order_df, table_ids_selected):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['local']
    collection14 = db['PreSelectedOrders']

    pred = collection14.find({}, {'_id': 0, 'Number': 1})

    df_pre_selected = pd.DataFrame(list(pred))

    if df_pre_selected.empty:
        re_selected_orders = []
    else:
        re_selected_orders = df_pre_selected['Number']

        for number in re_selected_orders:

            if number in order_df['Customer Order'].values:
                position = order_df.index[order_df['Customer Order'] == number][0]
                table_ids_selected[str(position)] = True

    return table_ids_selected


def create_grid():
    global game_phase
    client = MongoClient("mongodb://localhost:27017/")
    db = client['local']
    collection18 = db['GamePhaseConfig']
    document = collection18.find_one()
    game_phase = document.get('Game Phase')

    data = find_data_order()

    order_df = pd.DataFrame(find_data_order(),
                            columns=['number', 'order_line', 'reference', 'delivery_date', 'time_gap', 'description',
                                     'model', 'quantity', 'color', 'dimensions'])

    data_renamed = [{'Customer Order': d['number'], 'Order Line': d['order_line'], 'Product Ref.': d['reference'],
                     'Delivery Date': d['delivery_date'], 'Time Gap': d['time_gap'],
                     'Description': d['description'], 'Model': d['model'],
                     'Quantity': d['quantity'], 'Color': d['color'], 'Dimensions': d['dimensions']} for d in data]

    order_df = pd.DataFrame(data_renamed)
    order_df = order_df.reindex(columns=['Customer Order', 'Order Line', 'Product Ref.', 'Quantity', 'Delivery Date',
                                         'Time Gap', 'Model', 'Description', 'Color', 'Dimensions'])

    gd = GridOptionsBuilder.from_dataframe(order_df)

    client = MongoClient("mongodb://localhost:27017/")
    db = client['local']
    collection16 = db['HighPriority']
    collection17 = db['MediumPriority']

    cursor1 = collection16.find()
    cursor2 = collection17.find()

    for document in cursor1:
        param1 = document['High Priority']

    for document in cursor2:
        param2 = document["Medium Priority"]

    js_code = f"""
    function cell_style(params) {{
        console.log(params.data);

        // Check if time_gap is defined before attempting to split
        var timeGapParts;
        console.log("params.data['Time Gap']", params.data['Time Gap']);
        if (params.data['Time Gap']) {{
            timeGapParts = params.data['Time Gap'].split(":");
        }} else {{
            // Handle the case where time_gap is undefined (e.g., set a default value)
            timeGapParts = [0, 0, 0];
        }}

        console.log('timeGapParts:', timeGapParts);  // Add this line to check the content of timeGapParts

        // Ensure timeGapParts has at least three elements (hours, minutes, seconds)
        while (timeGapParts.length < 3) {{
            timeGapParts.push(0);
        }}

        // Convert time_gap string to hours
        var hours = parseInt(timeGapParts[0]);
        var minutes = parseInt(timeGapParts[1]);
        var seconds = parseInt(String(timeGapParts[2]).replace('h', ''));

        console.log('hours:', hours);  // Add this line to check the value of hours
        console.log('minutes:', minutes);  // Add this line to check the value of minutes
        console.log('seconds:', seconds);  // Add this line to check the value of seconds

        var totalHours = hours + minutes / 60 + seconds / 3600;

        console.log('totalHours:', totalHours);  // Add this line to check the value of totalHours

        // Adjusted logic for background color
        var backgroundColor = totalHours < {param1} ? 'rgb(213, 96, 98)' : (totalHours < {param2} ? 'rgb(244, 211, 94)' : 'white');

        return {{
            'color': 'black',
            'backgroundColor': backgroundColor,
            'textAlign': 'center'
        }};
    }}
    """
    cell_style = JsCode(js_code)

    table_ids_selected = {}
    find_pre(order_df, table_ids_selected)

    gd.configure_default_column(columns_auto_size_mode=True, cellStyle=cell_style, editable=False, groupable=True,
                                resizable=True, width=180)

    gd.configure_selection(selection_mode="multiple", use_checkbox=True, pre_selected_rows=table_ids_selected)

    # gd.configure_side_bar(columns_panel=True)
    gd.configure_column("Time Gap", cellStyle=cell_style)

    grid_options = gd.build()

    grid_container = AgGrid(order_df, gridOptions=grid_options, theme='material',
                            update_mode=GridUpdateMode.MODEL_CHANGED, allow_unsafe_jscode=True, reload_data=False,
                            key=f"{order_df}")

    return grid_container


def update_timer():
    client = MongoClient("mongodb://localhost:27017/")
    db = client['local']
    collection24 = db['GameStartStop']

    document = collection24.find_one()
    if document:
        game_mode = document.get('Game Mode')

        start_timer_js = ""
        pause_timer_js = ""

        # If game_mode is "Start", reset and then start the timer
        if game_mode == "Start":
            start_timer_js = """
                    startTimer();
                """

        # If game_mode is "Stop", pause the timer
        elif game_mode == "Stop":
            pause_timer_js = """
                    pauseTimer();
                """

        elif game_mode == "Clear":
            start_timer_js = """
                    resetTimer();
                """

        html_code = f"""
                <style>
                    .st-emotion-cache-wk66hx {{
                        display: inline-flex;
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
                        color: rgb(49, 51, 63);
                        width: auto;
                        user-select: none;
                        background-color: rgb(255, 255, 255);
                        border: 1px solid rgb(49, 51, 63, 0.2);
                    }}
                </style>
    
                <body>
                    <div style="font-size: 1.4rem; color: #333; font-family: 'Verdana', sans-serif;">
                        <span style="font-weight: bold; color: rgb(85,88,103);">Timer: </span>
                        <span id="timer" style="font-weight: bold; color: rgb(49, 90, 146);">00:00:00</span>
                    </div>
    
                    <script>
                        var seconds = 0;
                        var timerInterval;
                        var paused = true;
    
                        function startTimer() {{
                            if (!paused) return; // If already running, do nothing
                            paused = false;
                            timerInterval = setInterval(function () {{
                                seconds++;
                                updateTimer();
                            }}, 1000);
                        }}
    
                        function pauseTimer() {{
                            clearInterval(timerInterval);
                            paused = true;
                            document.cookie = 'paused=true; path=/; domain=localhost';
                        }}
    
                        function resetTimer() {{
                            clearInterval(timerInterval);
                            seconds = 0;
                            paused = true;
                            updateTimer();
                        }}
    
                        function updateTimer() {{
                            var hours = Math.floor(seconds / 3600).toString().padStart(2, '0');
                            var minutes = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0');
                            var secs = (seconds % 60).toString().padStart(2, '0');
                            var timeString = hours + ':' + minutes + ':' + secs;
                            document.cookie = 'myClock=' + timeString + '; path=/; domain=localhost';
                            document.getElementById("timer").innerHTML = timeString;
                        }}
    
                        document.addEventListener("DOMContentLoaded", function () {{
                            var cookies = document.cookie.split(';');
                            var isPaused = false;
    
                            for (var i = 0; i < cookies.length; i++) {{
                                var cookie = cookies[i].trim();
                                if (cookie.startsWith('paused=')) {{
                                    isPaused = cookie.substring('paused='.length, cookie.length) === 'true';
                                }}
                                if (cookie.startsWith('myClock=')) {{
                                    var clockCurrentValue = cookie.substring('myClock='.length, cookie.length);
                                    var timeParts = clockCurrentValue.split(':');
                                    seconds = parseInt(timeParts[0]) * 3600 + parseInt(timeParts[1]) * 60 + parseInt(timeParts[2]);
                                }}
                            }}
    
                            updateTimer(); // Update the timer display with the current time
    
                            if (!isPaused) {{
                                startTimer(); // Continue the timer if it wasn't paused
                            }}
    
                            {start_timer_js}
                            {pause_timer_js}
                        }});
                    </script>
                </body>
            """

        st.components.v1.html(html_code, height=50)


def find_selected_rows():
    client = MongoClient("mongodb://localhost:27017/")
    db = client['local']
    collection2 = db['selectedOrders']

    data_selected_rows = collection2.find({}, {'_id': 0, 'Number': 1, 'Order Line': 1,
                                               'Reference': 1,
                                               'Delivery Date': 1, 'Time Gap': 1, 'Description': 1, 'Model': 1,
                                               'Quantity': 1, 'Color': 1, 'Dimensions': 1})

    return data_selected_rows


def create_grid_selected_rows():
    selected_rows = find_selected_rows()

    rows_df = pd.DataFrame(list(selected_rows))
    if 'Time Gap' in rows_df.columns:
        rows_df = rows_df.drop(columns=['Time Gap'])
    if 'Color' in rows_df.columns:
        rows_df = rows_df.drop(columns=['Color'])
    if 'Dimensions' in rows_df.columns:
        rows_df = rows_df.drop(columns=['Dimensions'])

    if 'Quantity' in rows_df.columns:
        columns = ['Number', 'Order Line', 'Reference', 'Quantity', 'Delivery Date', 'Model',
                   'Description']
        rows_df = rows_df.reindex(columns=columns)

    rows_df = rows_df.rename(columns={
        'Number': 'Customer Order',
        'Reference': 'Product Ref.'
    })

    data_frame_selected_rows = st.dataframe(rows_df,
                                            column_config={
                                                "Customer Order": "Customer Order",
                                                "Order Line": "Order Line",
                                                'Product Ref.': "Product Ref.",
                                                'Quantity': "Quantity",
                                                'Delivery Date': "Delivery Date",
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

    # Windows
    # print_b = subprocess.Popen(['C:\\Program Files\\Adobe\\Acrobat DC\\Acrobat\\Acrobat.exe', '', pdf_filename])
    # Linux
    # print_b = subprocess.Popen(["/usr/bin/evince", pdf_filename])

    # Uncomment if necessary to open directly the PDF file
    # st_pdf.pdf_viewer(input="pdf_files/Selected_Orders_PDF.pdf", width=15000)
    # webbrowser.open(r"pdf_files/Selected_Orders_PDF.pdf")

    with open("pdf_files/Selected_Orders_PDF.pdf", "rb") as file:
        btn = st.download_button(
            label="Download",
            data=file,
            file_name="Production_Order.pdf"
        )
    return btn


def insert_production_finished_rows(selected_rows):
    client = MongoClient("mongodb://localhost:27017/")

    db = client['local']

    collection10 = db['TimeProductionFinished']

    order_numbers = []

    current_datetime = datetime.now()
    current_date = current_datetime.strftime("%Y-%m-%d")
    current_time = current_datetime.strftime("%H:%M:%S")

    data_to_insert = {
        'Orders Number': [],
        'Total Orders': 0,
        'Production Finished Time': {
            'Date': current_date,
            'Time': current_time
        }
    }

    for row in selected_rows:
        order_number = row['Customer Order']
        order_numbers.append(order_number)

        data_to_insert['Orders Number'] = order_numbers
        data_to_insert['Total Orders'] = len(order_numbers)

    collection10.insert_one(data_to_insert)
