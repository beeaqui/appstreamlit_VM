from OrdersListFunctions import update_timer
from SupervisorFunctions import *


def supervisor_page():
    update_timer()

    c1, c2 = st.columns(2)

    with c1:
        plot_generated_orders()

    with c2:
        wip_plot()

    with c1:
        quality_distribution()

    with c2:
        leadtime()

    with c1:
        orders_distribution()

    with c2:
        x_coefficients = [16.0, 18.0, 16.0, 11.0, 0.0, 1.0]
        y_coefficients = [23.0, 18.0, 14.0, 16.0, 1.0, 0.0]
        signs = ["<=", "<=", "<=", "<=", ">=", ">="]
        coefficients = [900.0, 900.0, 900.0, 900.0, 0.0, 0.0]
        objective_x = 3.0
        objective_y = 4.0

        result = LinearProgrammingExample(coefficients, x_coefficients, y_coefficients, signs,
                                          [objective_x, objective_y])
