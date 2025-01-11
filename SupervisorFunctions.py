import streamlit as st
import pandas as pd
import numpy as np
import operator

from pymongo import MongoClient
from datetime import datetime
from gekko import GEKKO
from streamlit.components.v1 import html
from ortools.linear_solver import pywraplp

import plotly.graph_objects as go
import plotly.express as px

client = MongoClient("mongodb://localhost:27017/")
db = client['local']
collection = db['ordersCollection']
collection3 = db['qualityOrders']
collection4 = "qualityApproved"
collection5 = "qualityDisapproved"
collection6 = db['expeditionOrders']
collection7 = db['ordersConcluded']
collection8 = db['GenerateOrderTime']
collection9 = db['TimeOrderReleased']
collection11 = db['TimeExpeditionEnd']
collection12 = db['LeadTimeOrders']
collection13 = db['CumulativeOrdersFinished']
collection20 = db['LogisticsOrdersProcess']
collection24 = db['GameStartStop']
collection25 = db['DelayedOrders']
collection26 = db['FlowProcessKPI']


def kpis_orders():
    orders_concluded = list(collection7.find())
    time_released = list(collection9.find())
    collection9.delete_many({"Order Number": ""})
    time_finished = list(collection11.find())
    count = collection7.count_documents({})
    color: str = ''

    # Parse a time string like 17:30 h into a time object
    def parse_time(time_str):
        if time_str and isinstance(time_str, str):
            # Remove any trailing ' h' and ensure it contains only the time part
            time_str_cleaned = time_str.split(' ')[0]  # Get just the 'HH:MM' or 'HH:MM:SS' part

            # Check if the string contains seconds
            if len(time_str_cleaned.split(':')) == 3:  # Format is HH:MM:SS
                return datetime.strptime(time_str_cleaned, "%H:%M:%S").time()
            else:  # Format is HH:MM
                return datetime.strptime(time_str_cleaned, "%H:%M").time()
        return None

    def extract_time(datetime_dict):
        return datetime.strptime(datetime_dict['Time'], "%H:%M").time()

    def time_to_minutes(time_obj):
        return time_obj.hour * 60 + time_obj.minute

    # Prepare data for the DataFrame - orders released
    data = []
    if count != 0:
        for order in orders_concluded:
            order_number = str(order.get('Number', None))
            order_line = str(order.get('Order line', None))
            order_delivery_str = order.get('Delivery date', None)  # Delivery date is expected to be a dictionary

            release_entry = next((r for r in time_released
                                  if r['Order Number'] == order_number and r['Order Line'] == order_line), None)

            if release_entry:
                released_time_dict = release_entry['Released Order Time']
                release_time_str = released_time_dict.get('Time', '')  # Get the 'Time' part
                release_time = parse_time(release_time_str)  # Parse the time string
                release_time_display = release_time.strftime("%H:%M") + ' h'
            else:
                release_time = None
                release_time_display = '-'

            finish_entry = next(
                (f for f in time_finished if f['Order Number'] == str(order_number)
                 and f['Order line'] == str(order_line)), None)

            if finish_entry:
                finish_time_dict = finish_entry['End Expedition Time']
                finish_time_str = finish_time_dict.get('Time', '')  # Get the 'Time' part
                finish_time = parse_time(finish_time_str)
                finish_time_display = finish_time.strftime("%H:%M") + ' h'
            else:
                finish_time = None
                finish_time_display = 'Waiting'

            # Parse delivery time
            order_delivery_time = parse_time(order_delivery_str) if order_delivery_str else None

            # Calculate lead time (in minutes) and delay (based on the difference in minutes)
            if release_time and finish_time:
                leadtime = time_to_minutes(finish_time) - time_to_minutes(release_time)
            else:
                leadtime = None

            if finish_time and order_delivery_time:
                delay = time_to_minutes(finish_time) - time_to_minutes(order_delivery_time)
            else:
                delay = None

            document = collection26.find({})
            if document:
                flow_process_kpi = delay
                collection26.update_one({}, {'$set': {'Flow delayed orders': flow_process_kpi}}, upsert=True)
            else:
                flow_process_kpi = delay
                collection26.insert_one({'Flow delayed orders': flow_process_kpi})

            data.append({'Number': order_number if order_number else '-',
                         'Order line': order_line if order_line else '-',
                         'Delivery date': order_delivery_str if order_delivery_str else '-',
                         'Release time': release_time_display,
                         'Finishing time': finish_time_display,
                         'Leadtime': leadtime if leadtime is not None else '-',
                         'Delay': delay if delay is not None else '-'})

    else:
        data.append({'Number': '-',
                     'Order line': '-',
                     'Delivery date': '-',
                     'Release time': '-',
                     'Finishing time': '-',
                     'Leadtime': '-',
                     'Delay': '-'})

    def color_delay(delay):
        if isinstance(delay, int) and delay > 0:
            return 'background-color: rgb(207, 119, 116);'
        elif isinstance(delay, int) and delay <= 0:
            return 'background-color: rgb(153, 148, 119);'
        return 'background-color: rgb(255, 255, 255);'

    # Create DataFrame
    df = pd.DataFrame(data)
    styled_df = df.style.map(color_delay, subset=['Delay'])

    # Display with st.data_editor
    st.data_editor(styled_df, hide_index=True, disabled=True, use_container_width=True)


def update_timer():
    document = collection24.find_one()
    if document:
        game_mode = document.get('Game Mode')

        start_timer_js = ""
        pause_timer_js = ""
        clear_timer_js = ""

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
            clear_timer_js = """
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
                        <span style="font-weight: bold; color: rgb(85,88,103);">TIMER: </span>
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
                            document.cookie = 'paused=true; path=/;';
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
                            document.cookie = 'myClock=' + timeString + '; path=/;';
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
                            {clear_timer_js}
                        }});
                    </script>
                </body>
            """

        st.components.v1.html(html_code, height=50)


def trajectory_plot():
    data = collection13.find()

    standard_coordinates = []
    sensor_kit_coordinates = []

    for order in data:
        standard_coordinates.append(order['Quantity Complex'])
        sensor_kit_coordinates.append(order['Quantity Sensor Kit'])

    return standard_coordinates, sensor_kit_coordinates


def find_intersections_trajectory(coefficients, x_coefficients, y_coefficients):
    intersections = []

    for i in range(len(coefficients)):
        for j in range(i + 1, len(coefficients)):

            augmented_matrix = np.column_stack((np.array([
                [x_coefficients[i], y_coefficients[i]],
                [x_coefficients[j], y_coefficients[j]]
            ]), np.array([coefficients[i], coefficients[j]])))

            try:
                _, _, rank, _ = np.linalg.lstsq(augmented_matrix[:, :-1], augmented_matrix[:, -1], rcond=None)

                if rank == augmented_matrix.shape[1] - 1:
                    pair_intersection = \
                        np.linalg.lstsq(augmented_matrix[:, :-1], augmented_matrix[:, -1], rcond=None)[
                            0]
                    # Convert -0.0 to 0.0
                    pair_intersection = [0.0 if abs(coord) < 1e-10 else coord for coord in pair_intersection]

                    # Check for duplicates
                    if pair_intersection not in intersections:
                        intersections.append(pair_intersection)

                else:
                    print(f"Pair {i + 1}-{j + 1} is inconsistent or undetermined. No unique solution.")

            except np.linalg.LinAlgError as e:
                print("LinAlgError:", e)

    rounded_intersections = [list(np.round(point, 2)) for point in intersections]
    vertices_polygon = []

    for point in rounded_intersections:
        if point not in vertices_polygon and all(coord >= 0 for coord in point):
            vertices_polygon.append(point)

    # st.write(f"**Intersection Points:** {vertices_polygon[0]}, {vertices_polygon[1]}, {vertices_polygon[2]}")

    return vertices_polygon


def linear_programming_trajectory(coefficients, x_coefficients, y_coefficients,
                                  signs, objective_coefficients, width_plot):
    solver = pywraplp.Solver.CreateSolver("GLOP")
    if not solver:
        return

    x = solver.NumVar(0, solver.infinity(), "x")
    y = solver.NumVar(0, solver.infinity(), "y")

    sign_mapping = {
        '<': operator.lt,
        '>': operator.gt,
        '<=': operator.le,
        '>=': operator.ge
    }

    constraint0 = sign_mapping[signs[0]](x_coefficients[0] * x + y_coefficients[0] * y, coefficients[0])
    constraint1 = sign_mapping[signs[1]](x_coefficients[1] * x + y_coefficients[1] * y, coefficients[1])
    constraint2 = sign_mapping[signs[2]](x_coefficients[2] * x + y_coefficients[2] * y, coefficients[2])
    constraint3 = sign_mapping[signs[3]](x_coefficients[3] * x + y_coefficients[3] * y, coefficients[3])
    constraint4 = sign_mapping[signs[4]](x_coefficients[4] * x + y_coefficients[4] * y, coefficients[4])
    constraint5 = sign_mapping[signs[5]](x_coefficients[5] * x + y_coefficients[5] * y, coefficients[5])

    solver.Add(constraint0)
    solver.Add(constraint1)
    solver.Add(constraint2)
    solver.Add(constraint3)
    solver.Add(constraint4)
    solver.Add(constraint5)

    solver.Maximize(objective_coefficients[0] * x + objective_coefficients[1] * y)

    print(f"Solving with {solver.SolverVersion()}")
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        # print("\nSolution:")
        # print(f"Objective value = {solver.Objective().Value():0.1f}")
        # print(f"x = {x.solution_value():0.1f}")
        # print(f"y = {y.solution_value():0.1f}")

        result = {"objective": solver.Objective().Value(), "x": x.solution_value(), "y": y.solution_value(),
                  "wall_time": solver.wall_time(), "iterations": solver.iterations()}

        # print("\nAdvanced usage:")
        # print(f"Problem solved in {solver.wall_time():d} milliseconds")
        # print(f"Problem solved in {solver.iterations():d} iterations")

        vertices_polygon = find_intersections_trajectory(coefficients, x_coefficients, y_coefficients)

        solution_trajectory(coefficients, x_coefficients, y_coefficients, objective_coefficients,
                            vertices_polygon, signs, width_plot)

    else:
        print("The problem does not have an optimal solution.")

    return result


def data_leadtime():
    result = []

    for order_info_9 in collection9.find():
        order_number_9 = order_info_9["Order Number"]

        for order_info_11 in collection11.find():
            order_number_11 = order_info_11["Order Number"]

            common_orders = set(order_number_9) & set(order_number_11)

            if common_orders:
                common_order = common_orders.pop()

                released_order_time = datetime.strptime(
                    order_info_9["Released Order Time"]["Date"] + " " + order_info_9["Released Order Time"]["Time"],
                    "%Y-%m-%d %H:%M:%S"
                )

                end_expedition_time = datetime.strptime(
                    order_info_11["End Expedition Time"]["Date"] + " " + order_info_11["End Expedition Time"]["Time"],
                    "%Y-%m-%d %H:%M:%S"
                )

                lead_time_seconds = ((end_expedition_time - released_order_time).total_seconds())

                result.append({
                    "Order Number": common_order,
                    "Released Order Time": {
                        "Date": order_info_9["Released Order Time"]["Date"],
                        "Time": order_info_9["Released Order Time"]["Time"]
                    },
                    "End Expedition Time": {
                        "Date": order_info_11["End Expedition Time"]["Date"],
                        "Time": order_info_11["End Expedition Time"]["Time"]
                    },
                    "Lead Time": lead_time_seconds
                })

                collection12.insert_one({
                    "Order Number": [common_order],
                    "Released Order Time": {
                        "Date": order_info_9["Released Order Time"]["Date"],
                        "Time": order_info_9["Released Order Time"]["Time"]
                    },
                    "End Expedition Time": {
                        "Date": order_info_11["End Expedition Time"]["Date"],
                        "Time": order_info_11["End Expedition Time"]["Time"]
                    },
                    "Lead Time": lead_time_seconds
                })

    return result


def find_finished_orders():
    finished_orders = collection7.find({}, {'_id': 0, 'Number': 1, 'Reference': 1, 'Delivery date': 1,
                                            'Time gap': 1, 'Description': 1, 'Model': 1, 'Quantity': 1,
                                            'Color': 1, 'Dimensions': 1})

    finished_orders_list = list(finished_orders)
    return finished_orders_list


def cumulative_finished_orders():
    cumulative_quantities = {
        'Quantity Complex': 0,
        'Quantity Sensor Kit': 0
    }

    finished_orders_list = find_finished_orders()

    existing_orders = set(collection13.distinct("Number"))

    for order in finished_orders_list:
        if order['Model'] == 'Complex':
            cumulative_quantities['Quantity Complex'] += 1
        elif order['Model'] == 'Sensor Kit':
            cumulative_quantities['Quantity Sensor Kit'] += 1

        order_number = order["Number"]
        if order_number in existing_orders:
            # print(f"Order {order_number} already exists in collection13. Skipping...")
            continue

        coordinates_x_y = (f"{cumulative_quantities['Quantity Complex']}, "
                           f"{cumulative_quantities['Quantity Sensor Kit']}")

        document = {
            "Number": order['Number'],
            "Reference": order['Reference'],
            "Model": order['Model'],
            "Quantity Complex": cumulative_quantities['Quantity Complex'],
            "Quantity Sensor Kit": cumulative_quantities['Quantity Sensor Kit'],
            "Coordinates (x, y)": coordinates_x_y
        }

        collection13.insert_one(document)


def cumulative_wip_plot_data():
    data_order_released = list(collection9.find())
    data_order_released.sort(key=lambda x: x['Released Order Time']['Time'])

    data_production_finished = list(collection11.find())
    data_production_finished.sort(key=lambda x: x['End Expedition Time']['Time'])

    plot_data_order_released = pd.DataFrame({
        'Time': [pd.to_datetime(entry['Released Order Time']['Date'] + ' ' + entry['Released Order Time']['Time'])
                 for entry in data_order_released],
        'Cumulative Orders': [entry['Total Orders'] for entry in data_order_released]
    })
    plot_data_order_released['Cumulative Orders'] = plot_data_order_released['Cumulative Orders'].cumsum()

    plot_data_production_finished = pd.DataFrame({
        'Time': [pd.to_datetime(entry['End Expedition Time']['Date'] + ' ' + entry['End Expedition Time']['Time'])
                 for entry in data_production_finished],
        'Cumulative Orders': [entry['Total Orders'] for entry in data_production_finished]
    })
    plot_data_production_finished['Cumulative Orders'] = plot_data_production_finished['Cumulative Orders'].cumsum()

    return plot_data_order_released, plot_data_production_finished


def calculate_time_difference_wip(df, starting_point):
    if not df.empty:
        df['TimeInSeconds'] = (df['Time'] - starting_point).dt.total_seconds()
        return df[['Cumulative Orders', 'TimeInSeconds']]


def create_trace_wip(df, name, color):
    if df is not None and not df.empty:
        return go.Scatter(
            x=df['TimeInSeconds'],
            y=df['Cumulative Orders'],
            mode='lines+markers',
            name=name,
            line=dict(color=color, width=2, dash='solid'),
            marker=dict(color=color, size=5),
            hoverinfo='text',
            line_shape='hv',
            hovertext=[f'Time (sec): {time} <br>Cumulative orders: {orders}'
                       for time, orders in zip(df['TimeInSeconds'], df['Cumulative Orders'])])

    else:
        return go.Scatter(
            x=[],
            y=[],
            mode='lines+markers',
            name=name,
            line=dict(color=color, width=2, dash='solid'),
            marker=dict(color=color, size=5),
            hoverinfo='text')


# Functions with the plots
def plot_generated_orders(width_plot):
    data = list(collection8.find({}, {'Generated Cust_Order': 1}).sort('Generated Cust_Order.Time'))

    df = pd.DataFrame(data)

    plotly_df = pd.DataFrame({'Time': [], 'Numbers': []})

    if df.empty:
        df = {'Numbers': [], 'Time (seconds)': []}

    if data:
        df['Generated Cust_Order'] = pd.to_datetime(
            df['Generated Cust_Order'].apply(lambda x: f"{x['Date']} {x['Time']}"))

        interval = '10S'

        time_intervals = pd.date_range(start=df['Generated Cust_Order'].min(), end=df['Generated Cust_Order'].max(),
                                       freq=interval)

        orders_count = [df[(df['Generated Cust_Order'] >= start) & (
                df['Generated Cust_Order'] < start + pd.to_timedelta(interval))].shape[0] for start in time_intervals]

        cumulative_orders = list(pd.Series(orders_count).cumsum())

        x_labels = [int((t - time_intervals[0]).seconds) for t in time_intervals]

        plotly_df = pd.DataFrame({'Time': x_labels, 'Numbers': cumulative_orders})

        first_entry = collection8.find_one({},
                                           sort=[('Generated Cust_Order.Date', 1), ('Generated Cust_Order.Time', 1)])
        last_entry = collection8.find_one({},
                                          sort=[('Generated Cust_Order.Date', -1), ('Generated Cust_Order.Time', -1)])

        first_date = first_entry['Generated Cust_Order']['Date']
        first_time = first_entry['Generated Cust_Order']['Time']

        last_date = last_entry['Generated Cust_Order']['Date']
        last_time = last_entry['Generated Cust_Order']['Time']

    fig = px.line(plotly_df, x='Time', y='Numbers', labels={'Time': 'Time (sec)'},
                  line_shape='hv',
                  color_discrete_sequence=['rgb(49, 90, 146)'])

    fig.update_layout(
        width=width_plot,
        title=dict(
            text='Order generation status',
            x=0.5,  # Center the title
            xanchor='center'  # Anchor the title to the center
        ),
        xaxis=dict(
            tickfont=dict(color='black'), title=dict(text='Time (sec)', font_color='black'),
            showline=False,
            showgrid=False,
            showticklabels=True),
        yaxis=dict(
            tickfont=dict(color='black'), title=dict(text='Numbers', font_color='black'),
            showline=False,
            showgrid=True,
            showticklabels=True),

        showlegend=False,
        dragmode=False,
        hovermode="x unified",
        modebar=dict(
            orientation='v',  # Vertical modebar position
            bgcolor='rgba(0,0,0,0)',  # Transparent modebar
            activecolor='rgb(0,0,0,0)',  # Transparent active color
            color='rgba(0,0,0,0)',  # Transparent inactive color
        ))

    st.plotly_chart(fig, use_container_width=True)


def wip_plot(width_plot):
    plot_data_order_released, plot_data_production_finished = cumulative_wip_plot_data()

    if plot_data_order_released.empty or plot_data_production_finished.empty:
        plot_data_order_released = pd.DataFrame({'Time': [], 'Cumulative Orders': []})
        plot_data_production_finished = pd.DataFrame({'Time': [], 'Cumulative Orders': []})

    starting_point = min(plot_data_order_released['Time'].min(), plot_data_production_finished['Time'].min())

    new_plot_data_order_released = calculate_time_difference_wip(plot_data_order_released, starting_point)
    new_plot_data_production_finished = calculate_time_difference_wip(plot_data_production_finished, starting_point)

    trace1 = create_trace_wip(new_plot_data_order_released, 'Input orders', 'rgb(166, 58, 80)')
    trace2 = create_trace_wip(new_plot_data_production_finished, 'Output orders', 'rgb(21, 96, 100)')

    fig = go.Figure(data=[trace1, trace2])

    fig.update_layout(
        xaxis=dict(
            tickfont=dict(color='black'),
            title=dict(text='Time (seconds)', font_color='black'),
            showline=False,
            showgrid=False,
            showticklabels=True
        ),
        yaxis=dict(
            tickfont=dict(color='black'),
            title=dict(text='Cumulative orders', font_color='black'),
            showline=False,
            showgrid=True,
            showticklabels=True
        ),
        title=dict(
            text='Cumulative order progress',
            x=0.5,  # Center the title
            xanchor='center'  # Anchor the title to the center
        ),
        hovermode='x unified',
        width=width_plot,
        showlegend=True,
        legend=dict(
            x=0.7,  # Center horizontally
            y=1.15,  # Position legend below the graph (negative value moves it inside)
            traceorder='normal',
            orientation='v',  # Horizontal orientation
        ),
        dragmode=False,
        modebar=dict(
            orientation='v',
            bgcolor='rgba(0,0,0,0)',
            activecolor='rgba(0,0,0,0)',
            color='rgba(0,0,0,0)', )
    )
    st.plotly_chart(fig, use_container_width=True)


def quality_distribution_plot(width_plot):
    count_approved = db[collection4].count_documents({})
    count_disapproved = db[collection5].count_documents({})

    df = {'Quantity': [count_approved, count_disapproved],
          'Quality': ['Approved', 'Disapproved']}

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df['Quantity'],
        x=df['Quality'],
        orientation='v',
        marker=dict(color=['rgb(21, 96, 100)', 'rgb(219, 173, 106)'])
    ))

    fig.update_layout(
        width=width_plot,
        title=dict(
            text='Quality distribution',
            x=0.5,  # Center the title
            xanchor='center'  # Anchor the title to the center
        ),
        xaxis=dict(
            tickfont=dict(color='black'), title=dict(text='Quality status', font_color='black'),
            showline=False,
            showgrid=False,
            showticklabels=True),
        yaxis=dict(
            tickfont=dict(color='black'), title=dict(text='Quantity', font_color='black'),
            showline=False,
            showgrid=True,
            showticklabels=True),

        showlegend=False,
        dragmode=False,
        hovermode="x unified",
        modebar=dict(
            orientation='v',  # Vertical modebar position
            bgcolor='rgba(0,0,0,0)',  # Transparent modebar
            activecolor='rgb(0,0,0,0)',  # Transparent active color
            color='rgba(0,0,0,0)',  # Transparent inactive color
        )
    )

    st.plotly_chart(fig, use_container_width=True)


def leadtime_plot(width_plot):
    collection12.drop()

    result = data_leadtime()
    lead_time_data = [doc["Lead Time"] for doc in collection12.find()]

    df = pd.DataFrame(result)

    if df.empty:
        df = {'Order Number': [],
              'Lead Time': []}

    # Create a bar chart using Plotly Express

    fig = px.bar(df, x='Order Number', y='Lead Time', orientation='v',
                 title='Orders lead time analysis',
                 labels={'Lead Time': 'Lead time (sec)', 'Order Number': 'Order number'})

    # Customize the layout
    fig.update_traces(marker_color='rgb(49, 90, 146)', marker_line_color='rgb(49, 90, 146)',
                      marker_line_width=1.5, opacity=1)

    fig.update_layout(
        width=width_plot,
        title=dict(
            text='Orders lead time analysis',
            x=0.5,  # Center the title
            xanchor='center'  # Anchor the title to the center
        ),
        xaxis=dict(
            tickfont=dict(color='black'), title=dict(text='Order number', font_color='black'),
            showline=False,
            showgrid=False,
            showticklabels=True),
        yaxis=dict(
            tickfont=dict(color='black'), title=dict(text='Lead time (sec)', font_color='black'),
            showline=False,
            showgrid=True,
            showticklabels=True),
        showlegend=False,
        dragmode=False, hovermode="x unified",
        modebar=dict(
            orientation='v',  # Vertical modebar position
            bgcolor='rgba(0,0,0,0)',  # Transparent modebar
            activecolor='rgb(0,0,0,0)',  # Transparent active color
            color='rgba(0,0,0,0)',  # Transparent inactive color
        )
    )

    # Display the chart using Streamlit
    st.plotly_chart(fig, use_container_width=True)


def orders_distribution_plot(width_plot):
    production_orders = collection.count_documents({})
    logistics_orders = collection20.count_documents({})
    quality_orders = collection3.count_documents({})
    expedition_orders = collection6.count_documents({})

    df = {
        'Workstation': ['Production', 'Logistics', 'Quality', 'Expedition'],
        'Quantity': [production_orders, logistics_orders, quality_orders, expedition_orders]
    }

    fig = px.bar(df, x='Workstation', y='Quantity',
                 orientation='v',
                 title='Workstations order distribution',
                 color='Workstation',
                 color_discrete_sequence=['rgb(166, 58, 80)', 'rgb(49, 90, 146)',
                                          'rgb(219, 173, 106)', 'rgb(21, 96, 100)'])

    fig.update_layout(
        width=width_plot,
        title=dict(
            text='Workstations order distribution',
            x=0.5,  # Center the title
            xanchor='center'  # Anchor the title to the center
        ),
        xaxis=dict(
            tickfont=dict(color='black'), title=dict(text='Workstation', font_color='black'),
            showline=False,
            showgrid=False,
            showticklabels=True),
        yaxis=dict(
            tickfont=dict(color='black'), title=dict(text='Quantity', font_color='black'),
            showline=False,
            showgrid=True,
            showticklabels=True),
        hovermode="x",
        showlegend=False,
        dragmode=False,
        modebar=dict(
            orientation='v',  # Vertical modebar position
            bgcolor='rgba(0,0,0,0)',  # Transparent modebar
            activecolor='rgb(0,0,0,0)',  # Transparent active color
            color='rgba(0,0,0,0)',  # Transparent inactive color
        )
    )
    st.plotly_chart(fig, use_container_width=True)


def calculate_delay_orders():
    document = collection25.find()

    delivery_times = list(collection7.find({}))
    expedition_times = list(collection11.find({}))

    total_delay_orders = 0
    without_delay = 0

    for expedition_time in expedition_times:
        for delivery_time in delivery_times:
            if expedition_time['Order Number'] == delivery_time['Number']:
                dateformat = '%H:%M:%S'
                start = delivery_time['Delivery date'].replace(' h', ':00')

                expedition_time_date = datetime.strptime(expedition_time['End Expedition Time']['Time'],
                                                         dateformat).replace(second=0)
                delivery_time_date = datetime.strptime(start, dateformat).replace(second=0)

                if expedition_time_date > delivery_time_date:
                    total_delay_orders += 1
                    if document:
                        collection25.update_one({}, {'$set': {'Total delayed orders': total_delay_orders}}, upsert=True)
                    else:
                        collection25.insert_one({'Total delayed orders': total_delay_orders})

                else:
                    without_delay += 1
    return total_delay_orders, without_delay


def plot_delay_orders(width_plot):
    total_delay_orders, without_delay = calculate_delay_orders()

    # Create data for the bar chart
    data = {'Status': ['Orders on time', 'Delayed orders'],
            'Count': [without_delay, total_delay_orders]}
    df = pd.DataFrame(data)

    color_map = {'Orders on time': 'rgb(21, 96, 100)', 'Delayed orders': 'rgb(219, 173, 106)'}
    fig = px.bar(df, x='Status', y='Count', color='Status',
                 color_discrete_map=color_map,
                 labels={'Count': 'Quantity'},
                 title='Order delivery status')

    # Update layout to disable interaction
    fig.update_layout(
        width=width_plot,
        title=dict(
            text='Order delivery status',
            x=0.5,  # Center the title
            xanchor='center'  # Anchor the title to the center
        ),
        xaxis=dict(
            tickfont=dict(color='black'), title=dict(text='Order status', font_color='black'),
            showline=False,
            showgrid=False,
            showticklabels=True),
        yaxis=dict(
            tickfont=dict(color='black'), title=dict(text='Number of orders', font_color='black'),
            showline=False,
            showgrid=True,
            showticklabels=True),
        showlegend=False,
        dragmode=False,
        hovermode="x unified",
        modebar=dict(
            orientation='v',  # Vertical modebar position
            bgcolor='rgba(0,0,0,0)',  # Transparent modebar
            activecolor='rgb(0,0,0,0)',  # Transparent active color
            color='rgba(0,0,0,0)',  # Transparent inactive color
        )
    )

    # Display the bar chart using Streamlit
    st.plotly_chart(fig, use_container_width=True)

    return total_delay_orders, without_delay


def solution_trajectory(coefficients, x_coefficients, y_coefficients, objective_coefficients,
                        vertices_polygon, signs, width_plot):
    m = GEKKO(remote=False)
    x, y = m.Array(m.Var, 2, lb=0)

    m.Equations([x_coefficients[0] * x + y_coefficients[0] * y <= coefficients[0],  # ws1
                 x_coefficients[1] * x + y_coefficients[1] * y <= coefficients[1],  # ws2
                 x_coefficients[2] * x + y_coefficients[2] * y <= coefficients[2],  # ws3
                 x_coefficients[3] * x + y_coefficients[3] * y <= coefficients[3]])  # ws4

    m.Maximize(objective_coefficients[0] * x + objective_coefficients[1] * y)  # objective function
    m.solve(disp=False)

    x_opt = x.value[0]
    y_opt = y.value[0]

    # visualize solution
    g = np.linspace(0, 100, 200)
    x, y = np.meshgrid(g, g)
    obj = x + y

    fig = go.Figure()

    fig.add_trace(go.Contour(z=((x_coefficients[0] * x + y_coefficients[0] * y <= coefficients[0]) &  # ws1
                                (x_coefficients[1] * x + y_coefficients[1] * y <= coefficients[1]) &  # ws2
                                (x_coefficients[2] * x + y_coefficients[2] * y <= coefficients[2]) &  # ws3
                                (x_coefficients[3] * x + y_coefficients[3] * y <= coefficients[3]) &  # ws4
                                (x >= 0) & (y >= 0)).astype(int), x=g, y=g,
                             colorscale='Greys', opacity=0.2, showscale=False))

    x0 = np.linspace(0, 100, 2000)

    # Workstations
    for i in range(4):
        y = (coefficients[i] / y_coefficients[i]) - (x_coefficients[i] / y_coefficients[i]) * x0
        fig.add_trace(go.Scatter(
            x=x0, y=y,
            mode='lines', line=dict(color=['#7E041C', '#122F74', '#076131', '#CC7F37'][i]),
            name=f"{int(x_coefficients[i])}x + {int(y_coefficients[i])}y {signs[i]} {int(coefficients[i])}",
            hovertemplate=(
                    f"{int(x_coefficients[i])}x + {int(y_coefficients[i])}y {signs[i]} {int(coefficients[i])}<br>" +
                    f"x: %{{x:.2f}}<br>" +
                    f"y: %{{y:.2f}}<br>"
            )
        ))

    y4 = 0 * x0  # x >= 0
    fig.add_trace(go.Scatter(x=x0, y=y4, mode='lines',
                             line=dict(color='#475453'), name=f"y {signs[4]} {int(coefficients[4])}",
                             hovertemplate=f"y {signs[4]} {int(coefficients[4])}<br>" +
                                           f"x: %{{x:.2f}}<br>" +
                                           f"y: %{{y:.2f}}<br>"
                             ))
    y5 = x0 * 0  # y >= 0
    fig.add_trace(go.Scatter(x=y5, y=x0, mode='lines', line=dict(color='#475453'),
                             name=f"x {signs[5]} {int(coefficients[5])}",
                             hovertemplate=f"x {signs[5]} {int(coefficients[5])}<br>" +
                                           f"x: %{{x:.2f}}<br>" +
                                           f"y: %{{y:.2f}}<br>"
                             ))

    # vertices for feasible area
    xv = [point[0] for point in vertices_polygon]
    yv = [point[1] for point in vertices_polygon]

    fig.add_trace(go.Scatter(x=xv, y=yv, mode='markers', line=dict(color='black'),
                             name='Intersection Points', marker=dict(size=5),
                             hovertemplate='Intersection Point<br>x: %{{x:.2f}}<br>y: %{{y:.2f}}<br>'))

    # trajectory of produced orders
    standard_coordinates, sensor_kit_coordinates = trajectory_plot()
    fig.add_trace(go.Scatter(x=standard_coordinates, y=sensor_kit_coordinates, line=dict(color='black'),
                             mode='markers', marker=dict(size=4), name='Trajectory',
                             hovertemplate='Trajectory Point<br>x: %{{x:.2f}}<br>y: %{{y:.2f}}<br>'))

    # style updates
    fig.update_layout(title=dict(
        text='Linear programming problem',
        x=0.5,  # Center the title
        xanchor='center'  # Anchor the title to the center
    ),
        xaxis=dict(title='Complex cylinder', range=[min(point[0] for point in vertices_polygon) - 2,
                                                    max(point[0] for point in vertices_polygon) + 2],
                   title_font=dict(color='black'),
                   tickfont=dict(color='black'),
                   showline=False,
                   showgrid=True,
                   showticklabels=True),
        yaxis=dict(title='Sensor kit cylinder',
                   range=[min(point[1] for point in vertices_polygon) - 2,
                          max(point[1] for point in vertices_polygon) + 2],
                   title_font=dict(color='black'),
                   tickfont=dict(color='black'),
                   showline=False,
                   showgrid=True,
                   showticklabels=True),
        showlegend=False,
        dragmode=False,
        hovermode="closest",
        width=width_plot,
        height=420,
        modebar=dict(
            orientation='v',  # Vertical modebar position
            bgcolor='rgba(0,0,0,0)',  # Transparent modebar
            activecolor='rgb(0,0,0,0)',  # Transparent active color
            color='rgba(0,0,0,0)',  # Transparent inactive color
        ))

    st.plotly_chart(fig, use_container_width=True)
