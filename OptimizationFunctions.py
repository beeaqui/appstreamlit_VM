import streamlit as st
from pymongo import MongoClient
import numpy as np
import operator

from ortools.linear_solver import pywraplp
import plotly.graph_objects as go
from gekko import GEKKO


def solution(coefficients, x_coefficients, y_coefficients, objective_coefficients, vertices_polygon, signs):
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
                  name=f"{int(x_coefficients[0])}x + {int(y_coefficients[0])}y {signs[0]} {int(coefficients[0])}"))
    # WS2
    y1 = (coefficients[1] / y_coefficients[1]) - (x_coefficients[1] / y_coefficients[1]) * x0
    fig.add_trace(go.Scatter(x=x0, y=y1, mode='lines', line=dict(color='#122F74'),
                  name=f"{int(x_coefficients[1])}x + {int(y_coefficients[1])}y {signs[1]} {int(coefficients[1])}"))
    # WS3
    y2 = (coefficients[2] / y_coefficients[2]) - (x_coefficients[2] / y_coefficients[2]) * x0
    fig.add_trace(go.Scatter(x=x0, y=y2, mode='lines', line=dict(color='#076131'),
                  name=f"{int(x_coefficients[2])}x + {int(y_coefficients[2])}y {signs[2]} {int(coefficients[2])}"))
    # WS4
    y3 = (coefficients[3] / y_coefficients[3]) - (x_coefficients[3] / y_coefficients[3]) * x0
    fig.add_trace(go.Scatter(x=x0, y=y3, mode='lines', line=dict(color='#CC7F37'),
                  name=f"{int(x_coefficients[3])}x + {int(y_coefficients[3])}y {signs[3]} {int(coefficients[3])}"))

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
                             name='Intersection Points', marker=dict(size=6)))

    # trajectory of produced orders
    standard_coordinates, sensor_kit_coordinates = trajectory(connect_mongodb())
    fig.add_trace(go.Scatter(x=standard_coordinates, y=sensor_kit_coordinates, line=dict(color='black'),
                             mode='markers', marker=dict(size=5), name='Trajectory'))

    # style updates
    fig.update_layout(xaxis=dict(title='Complex cylinder', range=[min(point[0] for point in vertices_polygon) - 2,
                                 max(point[0] for point in vertices_polygon) + 2], title_font=dict(color='black'),
                                 tickfont=dict(color='black')),
                      yaxis=dict(title='Sensor Kit Cylinder', range=[min(point[1] for point in vertices_polygon) - 2,
                                 max(point[1] for point in vertices_polygon) + 2], title_font=dict(color='black'),
                                 tickfont=dict(color='black')),
                      title='Linear programming problem',
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
                    pair_intersection = np.linalg.lstsq(augmented_matrix[:, :-1], augmented_matrix[:, -1], rcond=None)[
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

    st.write(f"**Intersection Points:** {vertices_polygon[0]}, {vertices_polygon[1]}, {vertices_polygon[2]}")

    return vertices_polygon


def LinearProgrammingExample(coefficients, x_coefficients, y_coefficients, signs, objective_coefficients):
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
        solution(coefficients, x_coefficients, y_coefficients, objective_coefficients, vertices_polygon, signs)

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
        'Quantity Complex': 0,
        'Quantity Sensor Kit': 0
    }

    finished_orders_list = find_finished_orders(db)

    existing_orders = set(collection13.distinct("Number"))

    for order in finished_orders_list:
        if order['Model'] == 'Complex':
            cumulative_quantities['Quantity Complex'] += 1
        elif order['Model'] == 'Sensor Kit':
            cumulative_quantities['Quantity Sensor Kit'] += 1

        order_number = order["Number"]
        if order_number in existing_orders:
            print(f"Order {order_number} already exists in collection13. Skipping...")
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


def trajectory(db):
    collection13 = db['CumulativeOrdersFinished']
    data = collection13.find()

    standard_coordinates = []
    sensor_kit_coordinates = []

    for order in data:
        standard_coordinates.append(order['Quantity Complex'])
        sensor_kit_coordinates.append(order['Quantity Sensor Kit'])

    return standard_coordinates, sensor_kit_coordinates
