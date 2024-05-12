import os
import webbrowser

import streamlit as st
import pandas as pd
import subprocess
from datetime import datetime

from pymongo import MongoClient
from st_aggrid import GridUpdateMode, AgGrid, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder

from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image
from reportlab.lib import colors
from streamlit.components.v1 import html

from streamlit_autorefresh import st_autorefresh


def insert_selected_rows(selected_rows):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['local']
    collection2 = db['selectedOrders']

    for row in selected_rows:
        selected_orders = collection2.insert_one(
            {'Number': row['Number'], 'Reference': row['Reference'], 'Delivery Date': row['Delivery Date'],
             'Time Gap': row['Time Gap'], 'Description': row['Description'], 'Model': row['Model'],
             'Quantity': row['Quantity'], 'Color': row['Color'], 'Dimensions': row['Dimensions']})


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
        order_number = row['Number']
        order_numbers.append(order_number)

        data_to_insert['Orders Number'] = order_numbers
        data_to_insert['Total Orders'] = len(order_numbers)

    collection9.insert_one(data_to_insert)


def delete_selected_rows(selected_rows):
    client = MongoClient("mongodb://localhost:27017/")

    db = client['local']

    collection = db['ordersCollection']

    for row in selected_rows:
        my_row = {'number': row['Number']}
        collection.delete_one(my_row)


def find_data_order():
    client = MongoClient("mongodb://localhost:27017/")

    db = client['local']

    collection = db['ordersCollection']

    data = collection.find({}, {'_id': 0, 'number': 1,
                                'reference': 1, 'delivery_date': 1, 'time_gap': 1, 'description': 1,
                                'model': 1, 'quantity': 1, 'color': 1, 'dimensions': 1})
    return data


def insert_pre(selected_rows):
    client = MongoClient("mongodb://localhost:27017/")

    db = client['local']

    collection14 = db['PreSelectedOrders']
    collection14.drop()

    for row in selected_rows:
        existing_document = collection14.find_one({'Number': row['Number']})

        if not existing_document:
            ppselected_orders = collection14.insert_one({'Number': row['Number']})


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

            if number in order_df['Number'].values:
                position = order_df.index[order_df['Number'] == number][0]
                table_ids_selected[str(position)] = True

    return table_ids_selected


def create_grid():
    data = find_data_order()

    order_df = pd.DataFrame(find_data_order(),
                            columns=['number', 'reference', 'delivery_date', 'time_gap', 'description', 'model',
                                     'quantity', 'color', 'dimensions'])

    data_renamed = [{'Number': d['number'], 'Reference': d['reference'], 'Delivery Date': d['delivery_date'],
                     'Time Gap': d['time_gap'], 'Description': d['description'], 'Model': d['model'],
                     'Quantity': d['quantity'], 'Color': d['color'], 'Dimensions': d['dimensions']} for d in data]

    order_df = pd.DataFrame(data_renamed)

    gd = GridOptionsBuilder.from_dataframe(order_df)

    cell_style = JsCode("""
            function(params) {
                console.log(params.data);

                // Check if time_gap is defined before attempting to split
                var timeGapParts;
                console.log("params.data['Time Gap']", params.data['Time Gap']);
                if (params.data['Time Gap']) {
                    timeGapParts = params.data['Time Gap'].split(":");
                } else {
                    // Handle the case where time_gap is undefined (e.g., set a default value)
                    timeGapParts = [0, 0, 0];
                }

                console.log('timeGapParts:', timeGapParts);  // Add this line to check the content of timeGapParts

                // Ensure timeGapParts has at least three elements (hours, minutes, seconds)
                while (timeGapParts.length < 3) {
                    timeGapParts.push(0);
                }

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
                var backgroundColor = totalHours < 0.5 ? 'rgb(213, 96, 98)' : (totalHours < 1 ? 
                'rgb(244, 211, 94)' : 'white');

                return {
                    'color': 'black',
                    'backgroundColor': backgroundColor,
                    'textAlign': 'center'
                };
            }
        """)

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
    html_code = """
    <style>
        .st-emotion-cache-wk66hx {
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
        }

        .st-emotion-cache-wk66hx:selected {
            background-color: rgb(49, 90, 146);
            color: rgb(49, 90, 146)
        }

        .st-emotion-cache-wk66hx:hover {
            border: 1px solid rgb(49, 90, 146);
            color: rgb(49, 90, 146)
        }

        .st-emotion-cache-wk66hx:active {
            background-color: rgb(49, 90, 146);
            color: rgb(255, 255, 255)
        }   
    </style>

    <body>
        <div style="font-size: 1.4rem; color: #333; font-family: 'Verdana', sans-serif;">
            <span style="font-weight: bold; color: rgb(85,88,103);">Timer: </span>
            <span id="timer" style="font-weight: bold; color: rgb(49, 90, 146);">00:00:00</span>
            <button id="startButton" class="st-emotion-cache-wk66hx">START</button>
            <button id="pauseButton" class="st-emotion-cache-wk66hx" disabled>PAUSE</button>
        </div>

         <script>
            var seconds = 0;
            var timerInterval;
            var paused = true;

            var startButton = document.getElementById("startButton");
            var pauseButton = document.getElementById("pauseButton");

            startButton.addEventListener("click", function () {
                if (paused && pauseButton.innerText != "RESUME" && startButton.innerText == "START") {
                    paused = false;
                    startButton.innerText = "RESET";
                    pauseButton.disabled = false;
                    startTimer();
                } else {
                    resetTimer();
                }
            });

            pauseButton.addEventListener("click", function () {
                if (paused) {
                    pauseButton.innerText = "PAUSE";
                    resumeTimer();
                } else {
                    pauseButton.innerText = "RESUME";
                    pauseTimer();
                }
            });

            function startTimer() {
                document.cookie = 'startButtonText=' + startButton.innerText + '; path=/; domain=localhost';
                document.cookie = 'pauseButtonText=' + pauseButton.innerText + '; path=/; domain=localhost';

                timerInterval = setInterval(function () {
                    seconds++;
                    updateTimer();
                }, 1000);

            }

            function pauseTimer() {
                clearInterval(timerInterval);
                paused = true;
                document.cookie = 'paused=' + paused + '; path=/; domain=localhost';
                document.cookie = 'startButtonText=' + startButton.innerText + '; path=/; domain=localhost';
                document.cookie = 'pauseButtonText=' + pauseButton.innerText + '; path=/; domain=localhost';
            }

            function resumeTimer() {
                startTimer();
                paused = false;
                document.cookie = 'paused=' + paused + '; path=/; domain=localhost';
                document.cookie = 'startButtonText=' + startButton.innerText + '; path=/; domain=localhost';
                document.cookie = 'pauseButtonText=' + pauseButton.innerText + '; path=/; domain=localhost';
            }

            function resetTimer() {
                clearInterval(timerInterval);
                seconds = 0;
                paused = true;
                updateTimer();
                startButton.innerText = "START";
                pauseButton.innerText = "PAUSE";
                pauseButton.disabled = true;
                document.cookie = 'startButtonText=' + startButton.innerText + '; path=/; domain=localhost';
                document.cookie = 'pauseButtonText=' + pauseButton.innerText + '; path=/; domain=localhost';
            }

            function updateTimer() {
                var hours = Math.floor(seconds / 3600).toString().padStart(2, '0');
                var minutes = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0');
                var secs = (seconds % 60).toString().padStart(2, '0');
                var timeString = hours + ':' + minutes + ':' + secs;
                document.cookie = 'myClock=' + timeString + '; path=/; domain=localhost';
                document.cookie = 'paused=' + paused + '; path=/; domain=localhost';

                document.getElementById("timer").innerHTML = timeString;
            }

            document.addEventListener("DOMContentLoaded", function () {
                var cookies = document.cookie.split(';');

                var isMyClock = false;
                var isPaused = false;
                var isStartButtonText = false;
                var isPauseButtonText = false;

                for (var i = 0; i < cookies.length; i++) {
                    var cookie = cookies[i].trim();

                    if (cookie.startsWith('myClock=')) {
                        isMyClock = true;
                        clockCurrentValue = cookie.substring('myClock='.length, cookie.length);
                        var timeParts = clockCurrentValue.split(':');
                        seconds = parseInt(timeParts[0]) * 3600 + parseInt(timeParts[1]) * 60 + parseInt(timeParts[2]);
                    } else if (cookie.startsWith('paused=')) {
                        isPaused = true;
                        paused = cookie.substring('paused='.length, cookie.length) === 'true';
                    } else if (cookie.startsWith('startButtonText=')) {
                        isStartButtonText = true;
                        startButton.innerText = cookie.substring('startButtonText='.length, cookie.length);
                        if(startButton.innerText != "START"){
                            pauseButton.disabled = false;
                        }
                    } else if (cookie.startsWith('pauseButtonText=')) {
                        isPauseButtonText = true;
                        pauseButton.innerText = cookie.substring('pauseButtonText='.length, cookie.length);
                    }
                }

                if(isMyClock && isPaused){
                    if(!paused){
                        startTimer();
                    }
                    else{
                        updateTimer();
                    }
                }
                else{
                    paused = true;
                    seconds = 0;
                    startButton.innerText = 'START';
                    pauseButton.innerText = 'PAUSE';
                    updateTimer();
                }
            });
        </script>
    </body>
    """

    st.components.v1.html(html_code, height=50)


def find_selected_rows():
    client = MongoClient("mongodb://localhost:27017/")

    db = client['local']

    collection2 = db['selectedOrders']

    data_selected_rows = collection2.find({}, {'_id': 0, 'Number': 1, 'Reference': 1, 'Delivery Date': 1,
                                               'Time Gap': 1, 'Description': 1, 'Model': 1, 'Quantity': 1,
                                               'Color': 1, 'Dimensions': 1})

    return data_selected_rows


def create_grid_selected_rows():
    selected_rows = find_selected_rows()

    rows_df = pd.DataFrame(list(selected_rows))

    data_frame_selected_rows = st.dataframe(rows_df,
                                            column_config={
                                                "Number": "Number",
                                                'Reference': "Reference",
                                                'Delivery Date': "Delivery Date",
                                                'Time Gap': "Time Gap",
                                                'Description': "Description",
                                                'Model': "Model",
                                                'Quantity': "Quantity",
                                                'Color': "Color",
                                                'Dimensions': "Dimensions"
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

    print_b = webbrowser.open(r"pdf_files/Selected_Orders_PDF.pdf")

    return print_b


def insert_production_finished_rows():
    selected_rows = find_selected_rows()

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
        order_number = row['Number']
        order_numbers.append(order_number)

        data_to_insert['Orders Number'] = order_numbers
        data_to_insert['Total Orders'] = len(order_numbers)

    collection10.insert_one(data_to_insert)
