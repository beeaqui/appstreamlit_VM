import streamlit as st
from pymongo import MongoClient
import pandas as pd
from datetime import datetime
import numpy as np
import operator
from gekko import GEKKO

import plotly.graph_objects as go
import plotly.express as px
from ortools.linear_solver import pywraplp


def solution(coefficients, x_coefficients, y_coefficients, objective_coefficients, vertices_polygon, signs, width6):
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

    # WS1
    y0 = (coefficients[0] / y_coefficients[0]) - (x_coefficients[0] / y_coefficients[0]) * x0
    fig.add_trace(go.Scatter(x=x0, y=y0, mode='lines', line=dict(color='#7E041C'),
                             name=f"{int(x_coefficients[0])}x + {int(y_coefficients[0])}y "
                                  f"{signs[0]} {int(coefficients[0])}"))
    # WS2
    y1 = (coefficients[1] / y_coefficients[1]) - (x_coefficients[1] / y_coefficients[1]) * x0
    fig.add_trace(go.Scatter(x=x0, y=y1, mode='lines', line=dict(color='#122F74'),
                             name=f"{int(x_coefficients[1])}x + {int(y_coefficients[1])}y "
                                  f"{signs[1]} {int(coefficients[1])}"))
    # WS3
    y2 = (coefficients[2] / y_coefficients[2]) - (x_coefficients[2] / y_coefficients[2]) * x0
    fig.add_trace(go.Scatter(x=x0, y=y2, mode='lines', line=dict(color='#076131'),
                             name=f"{int(x_coefficients[2])}x + {int(y_coefficients[2])}y "
                                  f"{signs[2]} {int(coefficients[2])}"))
    # WS4
    y3 = (coefficients[3] / y_coefficients[3]) - (x_coefficients[3] / y_coefficients[3]) * x0
    fig.add_trace(go.Scatter(x=x0, y=y3, mode='lines', line=dict(color='#CC7F37'),
                             name=f"{int(x_coefficients[3])}x + {int(y_coefficients[3])}y "
                                  f"{signs[3]} {int(coefficients[3])}"))

    y4 = 0 * x0  # x >= 0
    fig.add_trace(go.Scatter(x=x0, y=y4, mode='lines', line=dict(color='#475453'),
                             name=f"y {signs[4]} {int(coefficients[4])}"))
    y5 = x0 * 0  # y >= 0
    fig.add_trace(go.Scatter(x=y5, y=x0, mode='lines', line=dict(color='#475453'),
                             name=f"x {signs[5]} {int(coefficients[5])}"))

    # vertices for feasible area
    xv = [point[0] for point in vertices_polygon]
    yv = [point[1] for point in vertices_polygon]

    fig.add_trace(go.Scatter(x=xv, y=yv, mode='markers', line=dict(color='black'),
                             name='Intersection Points', marker=dict(size=5)))

    # trajectory of produced orders
    standard_coordinates, sensor_kit_coordinates = trajectory(connect_mongodb())
    fig.add_trace(go.Scatter(x=standard_coordinates, y=sensor_kit_coordinates, line=dict(color='black'),
                             mode='markers', marker=dict(size=4), name='Trajectory'))

    # style updates
    fig.update_layout(xaxis=dict(title='Standard Cylinder', range=[min(point[0] for point in vertices_polygon) - 2,
                                                                   max(point[0] for point in vertices_polygon) + 2],
                                 title_font=dict(color='black'),
                                 tickfont=dict(color='black')),
                      yaxis=dict(title='Sensor Kit Cylinder',
                                 range=[min(point[1] for point in vertices_polygon) - 2,
                                        max(point[1] for point in vertices_polygon) + 2],
                                 title_font=dict(color='black'),
                                 tickfont=dict(color='black')),
                      showlegend=False,
                      width=width6,
                      title='Linear Programming Problem',
                      height=420,
                      )

    st.plotly_chart(fig)


def find_intersections(coefficients, x_coefficients, y_coefficients):
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


def LinearProgrammingExample(coefficients, x_coefficients, y_coefficients, signs, objective_coefficients, width6):
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

        vertices_polygon = find_intersections(coefficients, x_coefficients, y_coefficients)

        solution(coefficients, x_coefficients, y_coefficients, objective_coefficients, vertices_polygon, signs, width6)

    else:
        print("The problem does not have an optimal solution.")

    return result


def connect_mongodb():
    client = MongoClient("mongodb://localhost:27017/")
    db = client['local']

    return db


def find_finished_orders(db):
    connect_mongodb()
    collection7 = db['ordersConcluded']
    finished_orders = collection7.find({}, {'_id': 0, 'Number': 1, 'Reference': 1, 'Delivery Date': 1,
                                            'Time Gap': 1, 'Description': 1, 'Model': 1, 'Quantity': 1,
                                            'Color': 1, 'Dimensions': 1})

    finished_orders_list = list(finished_orders)
    return finished_orders_list


def cumulative_finished_orders(db):
    collection13 = db['CumulativeOrdersFinished']

    cumulative_quantities = {
        'Quantity Standard': 0,
        'Quantity Sensor Kit': 0
    }

    finished_orders_list = find_finished_orders(db)

    existing_orders = set(collection13.distinct("Number"))

    for order in finished_orders_list:
        if order['Model'] == 'Standard':
            cumulative_quantities['Quantity Standard'] += 1
        elif order['Model'] == 'Sensor Kit':
            cumulative_quantities['Quantity Sensor Kit'] += 1

        order_number = order["Number"]
        if order_number in existing_orders:
            print(f"Order {order_number} already exists in collection13. Skipping...")
            continue

        coordinates_x_y = (f"{cumulative_quantities['Quantity Standard']}, "
                           f"{cumulative_quantities['Quantity Sensor Kit']}")

        document = {
            "Number": order['Number'],
            "Reference": order['Reference'],
            "Model": order['Model'],
            "Quantity Standard": cumulative_quantities['Quantity Standard'],
            "Quantity Sensor Kit": cumulative_quantities['Quantity Sensor Kit'],
            "Coordinates (x, y)": coordinates_x_y
        }

        collection13.insert_one(document)


def trajectory(db):
    collection13 = db['CumulativeOrdersFinished']
    data = collection13.find()

    standard_coordinates = []
    sensor_kit_coordinates = []

    for order in data:
        standard_coordinates.append(order['Quantity Standard'])
        sensor_kit_coordinates.append(order['Quantity Sensor Kit'])

    return standard_coordinates, sensor_kit_coordinates


def plot_generated_orders(width1):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['local']
    collection8 = db['GenerateOrderTime']

    data = list(collection8.find({}, {'Generated Cust_Order': 1}).sort('Generated Cust_Order.Time'))

    df = pd.DataFrame(data)

    df['Generated Cust_Order'] = pd.to_datetime(df['Generated Cust_Order'].apply(lambda x: f"{x['Date']} {x['Time']}"))

    interval = '10S'

    time_intervals = pd.date_range(start=df['Generated Cust_Order'].min(), end=df['Generated Cust_Order'].max(),
                                   freq=interval)

    orders_count = [df[(df['Generated Cust_Order'] >= start) & (
            df['Generated Cust_Order'] < start + pd.to_timedelta(interval))].shape[0] for start in time_intervals]

    cumulative_orders = list(pd.Series(orders_count).cumsum())

    x_labels = [int((t - time_intervals[0]).seconds) for t in time_intervals]

    plotly_df = pd.DataFrame({'Time': x_labels, 'Customer Orders': cumulative_orders})

    fig = px.line(plotly_df, x='Time', y='Customer Orders', labels={'Time': 'Time (seconds)'},
                  title='Order Generation Status',
                  line_shape='hv',
                  color_discrete_sequence=['rgb(49, 90, 146)'])

    first_entry = collection8.find_one({}, sort=[('Generated Cust_Order.Date', 1), ('Generated Cust_Order.Time', 1)])
    last_entry = collection8.find_one({}, sort=[('Generated Cust_Order.Date', -1), ('Generated Cust_Order.Time', -1)])

    first_date = first_entry['Generated Cust_Order']['Date']
    first_time = first_entry['Generated Cust_Order']['Time']

    last_date = last_entry['Generated Cust_Order']['Date']
    last_time = last_entry['Generated Cust_Order']['Time']

    # annotation_text = (f'<b>Date:</b> {first_date} to {last_date}<br>'
    #                   f'<b>Time Range:</b> from {first_time} to {last_time} hours')

    fig.update_layout(
        width=width1,
        xaxis=dict(tickfont=dict(color='black'), title=dict(text='Time (seconds)', font_color='black')),
        yaxis=dict(tickfont=dict(color='black'), title=dict(text='Customer Orders', font_color='black')),
    )

    st.plotly_chart(fig)


def wip_plot(width2):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['local']
    collection9 = db['TimeOrderReleased']
    collection11 = db['TimeExpeditionEnd']

    data_order_released = list(collection9.find())
    data_order_released.sort(key=lambda x: x['Released Order Time']['Time'])

    data_production_finished = list(collection11.find())
    data_production_finished.sort(key=lambda x: x['End Expedition Time']['Time'])

    plot_data_order_released = pd.DataFrame({
        'Time': [pd.to_datetime(entry['Released Order Time']['Date'] + ' ' + entry['Released Order Time']['Time']) for
                 entry in data_order_released],
        'Cumulative Orders': [entry['Total Orders'] for entry in data_order_released]
    })

    plot_data_order_released['Cumulative Orders'] = plot_data_order_released['Cumulative Orders'].cumsum()

    plot_data_production_finished = pd.DataFrame({
        'Time': [pd.to_datetime(entry['End Expedition Time']['Date'] + ' ' + entry['End Expedition Time']['Time']) for
                 entry in data_production_finished],
        'Cumulative Orders': [entry['Total Orders'] for entry in data_production_finished]
    })

    plot_data_production_finished['Cumulative Orders'] = plot_data_production_finished['Cumulative Orders'].cumsum()

    '''fig = go.Figure()

    fig.add_trace(go.Scatter(x=plot_data_order_released['Time'],
                             y=plot_data_order_released['Cumulative Orders'],
                             mode='lines+markers',
                             name='Input Orders',
                             line=dict(color='rgb(166, 58, 80)', width=2, dash='solid'),
                             marker=dict(color='rgb(166, 58, 80)', size=5),
                             hoverinfo='text',
                             line_shape='hv',
                             hovertext=[f'Time: {time}<br>Cumulative Orders: {orders}' for time, orders in
                                        zip(plot_data_order_released['Time'],
                                            plot_data_order_released['Cumulative Orders'])]))

    fig.add_trace(go.Scatter(x=plot_data_production_finished['Time'],
                             y=plot_data_production_finished['Cumulative Orders'],
                             mode='lines+markers',
                             name='Output Orders',
                             line=dict(color='rgb(21, 96, 100)', width=2, dash='solid'),
                             marker=dict(color='rgb(21, 96, 100)', size=5),
                             hoverinfo='text',
                             line_shape='hv',
                             hovertext=[f'Time: {time}<br>Cumulative Orders: {orders}' for time, orders in
                                        zip(plot_data_production_finished['Time'],
                                            plot_data_production_finished['Cumulative Orders'])]))

    fig.update_layout(
        xaxis=dict(
            tickfont=dict(color='black'),
            title=dict(text='Time', font_color='black'),
        ),

        yaxis=dict(
            tickfont=dict(color='black'),
            title=dict(text='Work', font_color='black'),
        ),
        title='Cumulative Order Progress',
        hovermode='closest',
        width=350,
        legend=dict(x=0.5, y=1.2, traceorder='normal', orientation='v'),
    )

    st.plotly_chart(fig)'''

    # Assuming starting point is the minimum datetime value from both dataframes
    starting_point = min(
        min(plot_data_order_released['Time']),
        min(plot_data_production_finished['Time'])
    )

    # Function to calculate time differences in seconds and add Cumulative Orders
    # noinspection PyShadowingNames
    def calculate_time_difference_in_seconds(df, starting_point):
        df['TimeInSeconds'] = (df['Time'] - starting_point).dt.total_seconds()
        return df[['Cumulative Orders', 'TimeInSeconds']]

    # Apply the function to create new dataframes
    new_plot_data_order_released = calculate_time_difference_in_seconds(
        plot_data_order_released.copy(), starting_point
    )

    new_plot_data_production_finished = calculate_time_difference_in_seconds(
        plot_data_production_finished.copy(), starting_point
    )

    # Create traces
    trace1 = go.Scatter(
        x=new_plot_data_order_released['TimeInSeconds'],
        y=new_plot_data_order_released['Cumulative Orders'],
        mode='lines+markers',
        name='Input Orders',
        line=dict(color='rgb(166, 58, 80)', width=2, dash='solid'),
        marker=dict(color='rgb(166, 58, 80)', size=5),
        hoverinfo='text',
        line_shape='hv',
        hovertext=[
            f'Time: {time}<br>Cumulative Orders: {orders}'
            for time, orders in zip(new_plot_data_order_released['TimeInSeconds'],
                                    new_plot_data_order_released['Cumulative Orders'])
        ]
    )

    trace2 = go.Scatter(
        x=new_plot_data_production_finished['TimeInSeconds'],
        y=new_plot_data_production_finished['Cumulative Orders'],
        mode='lines+markers',
        name='Output Orders',
        line=dict(color='rgb(21, 96, 100)', width=2, dash='solid'),
        marker=dict(color='rgb(21, 96, 100)', size=5),
        hoverinfo='text',
        line_shape='hv',
        hovertext=[
            f'Time: {time}<br>Cumulative Orders: {orders}'
            for time, orders in zip(new_plot_data_production_finished['TimeInSeconds'],
                                    new_plot_data_production_finished['Cumulative Orders'])
        ]
    )

    # Create layout
    layout = go.Layout(
        xaxis=dict(
            tickfont=dict(color='black'),
            title=dict(text='Time (seconds)', font_color='black'),
        ),
        yaxis=dict(
            tickfont=dict(color='black'),
            title=dict(text='Cumulative Orders', font_color='black'),
        ),
        title='Cumulative Order Progress',
        hovermode='closest',
        width=width2,
        legend=dict(x=0.5, y=1.2, traceorder='normal', orientation='v'),
    )

    # Create figure
    fig = go.Figure(data=[trace1, trace2], layout=layout)

    # Show plot
    st.plotly_chart(fig)


def leadtime_calculate():
    result = []
    client = MongoClient("mongodb://localhost:27017/")
    db = client['local']
    collection9 = db['TimeOrderReleased']
    collection11 = db['TimeExpeditionEnd']
    collection12 = db['LeadTimeOrders']

    for order_info_9 in collection9.find():
        order_number_9 = order_info_9["Orders Number"]

        for order_info_11 in collection11.find():
            order_number_11 = order_info_11["Orders Number"]

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
                    "Orders Number": [common_order],
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


def leadtime(width4):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["local"]
    collection12 = db["LeadTimeOrders"]
    collection12.drop()

    result = leadtime_calculate()
    lead_time_data = [doc["Lead Time"] for doc in collection12.find()]

    df = pd.DataFrame(result)

    # Create a bar chart using Plotly Express
    fig = px.bar(df, x='Lead Time', y='Order Number', orientation='h',
                 title='Order Lead Time Visualization', labels={'Lead Time': 'Lead Time (seconds) '}, )

    # Customize the layout
    fig.update_traces(marker_color='rgb(49, 90, 146)', marker_line_color='rgb(49, 90, 146)',
                      marker_line_width=1.5, opacity=1)

    fig.update_layout(
        xaxis=dict(title='Lead Time (seconds)', title_font=dict(color='black'), tickfont=dict(color='black'), ),
        yaxis=dict(title='Order Number', title_font=dict(color='black'), tickfont=dict(color='black'), ),
        bargap=0.15,
        width=width4)

    # Display the chart using Streamlit
    st.plotly_chart(fig, use_container_width=True)


def quality_distribution(width3):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["local"]
    collection4 = "qualityApproved"
    collection5 = "qualityDisapproved"

    count_approved = db[collection4].count_documents({})
    count_disapproved = db[collection5].count_documents({})

    df = {
        'Quality': ['Approved', 'Disapproved'],
        'Quantity': [count_approved, count_disapproved]
    }

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df['Quality'],
        x=df['Quantity'],
        orientation='h',
        marker=dict(color=['rgb(21, 96, 100)', 'rgb(219, 173, 106)'])
    ))

    # Update layout
    fig.update_layout(
        title='Quality Distribution',
        xaxis=dict(title='Quantity', title_font=dict(color='black'), tickfont=dict(color='black')),
        yaxis=dict(title='Quality', title_font=dict(color='black'), tickfont=dict(color='black')),
        width=width3,
        showlegend=False
    )

    st.plotly_chart(fig)


def orders_distribution(width5):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["local"]

    # Define your collections
    collection = db['ordersCollection']
    collection3 = db['qualityOrders']
    collection6 = db['expeditionOrders']

    production_orders = collection.count_documents({})
    quality_orders = collection3.count_documents({})
    expedition_orders = collection6.count_documents({})

    df = {
        'Workstation': ['Production Planning', 'Quality Control', 'Expedition Orders'],
        'Quantity': [production_orders, quality_orders, expedition_orders]
    }

    fig = px.bar(df, x='Quantity', y='Workstation',
                 orientation='h',
                 title='Workstations Order Distribution',
                 color='Workstation',
                 color_discrete_sequence=['rgb(166, 58, 80)', 'rgb(49, 90, 146)', 'rgb(219, 173, 106)'])

    fig.update_layout(
        xaxis=dict(title_font=dict(color='black'), tickfont=dict(color='black'), ),
        yaxis=dict(title_font=dict(color='black'), tickfont=dict(color='black'), ),
        width=width5,
        showlegend=False)

    st.plotly_chart(fig)

