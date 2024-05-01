from OptimizationFunctions import *


def other_page():
    st.title("Linear Programming Model")

    st.write("**Constraints:** ax + bx = c")

    c1, c2, c3, c4, c5 = st.columns(5)
    inputs = [
        ("a", ["16.0", "18.0", "16.0", "11.0", "0.0", "1.0"]),
        ("b", ["23.0", "18.0", "14.0", "16.0", "1.0", "0.0"]),
        ("Operator", ["<=", "<=", "<=", "<=", ">=", ">="]),
        ("c", ["900.0", "900.0", "900.0", "900.0", "0.0", "0.0"]),
    ]

    with c1:
        x_coefficients = [
            st.text_input("Workstation 1", value="16.0"),
            st.text_input("Workstation 2", value="18.0"),
            st.text_input("Workstation 3", value="16.0"),
            st.text_input("Workstation 4", value="11.0"),
            st.text_input("y >= 0", value="0.0"),
            st.text_input("x >= 0", value="1.0"),

        ]

    with c2:
        y_coefficients = [
            st.text_input(" ", value="23.0"),
            st.text_input("  ", value="18.0"),
            st.text_input("   ", value="14.0"),
            st.text_input("    ", value="16.0"),
            st.text_input("     ", value="1.0"),
            st.text_input("      ", value="0.0"),
        ]

    with c3:
        signs = [
            st.text_input(f" ", value="<="),
            st.text_input(f"  ", value="<="),
            st.text_input(f"   ", value="<="),
            st.text_input(f"    ", value="<="),
            st.text_input(f"     ", value=">="),
            st.text_input(f"      ", value=">="),

        ]

    with c4:
        coefficients = [
            st.text_input(" ", value="900.0"),
            st.text_input("  ", value="900.0"),
            st.text_input("   ", value="900.0"),
            st.text_input("    ", value="900.0"),
            st.text_input("    ", value="0.0"),
            st.text_input("     ", value="0.0"),

        ]

    with c5:
        st.subheader("")
        st.write("")
        for i in range(len(coefficients)):

            st.write(
                f"<span style='font-size: 14px;'"
                f">{x_coefficients[i]}x {y_coefficients[i]}y {signs[i]} {coefficients[i]}</span>",
                unsafe_allow_html=True)
            st.subheader("")
            st.write("")

    h1, h2, h3 = st.columns(3)
    with h1:
        st.caption("")
        st.caption("")
        st.write("**Objective function:** ax + bx")

    l1, l2, l3 = st.columns(3)
    with l1:
        objective_x = st.number_input("x value", value=3.0)

    with l2:
        objective_y = st.number_input("y value", value=4.0)

    with l3:
        st.caption("")
        st.caption("")
        # Objective function: ax + by, where a and b are user inputs
        objective_function = f"{objective_x}x + {objective_y}y"
        st.write(f"**Maximize Z** = {objective_function}")

    st.caption("")
    coefficients = [float(value) for value in coefficients]
    x_coefficients = [float(value) for value in x_coefficients]
    y_coefficients = [float(value) for value in y_coefficients]
    signs = [str(value) for value in signs]

    result = LinearProgrammingExample(coefficients, x_coefficients, y_coefficients, signs, [objective_x, objective_y])

    # print("x_coefficients", x_coefficients)
    # print("y_coefficients", y_coefficients)
    # print("coefficients", coefficients)

    st.write(f"**Solution:**")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.write(f"Objective = {result['objective']:0.1f}")
    with c2:
        st.write(f"X Value = {result['x']:0.1f}")
    with c3:
        st.write(f"Y Value = {result['y']:0.1f}")
    with c4:
        st.write(f"Wall Time = {result['wall_time']:0.1f}")
    with c5:
        st.write(f"Iterations = {result['iterations']:0.1f}")

    optimal_solution = f"{objective_x:0.1f} x + {objective_y:0.1f} y = {result['objective']:0.1f}"
    st.caption('')
    st.write(f"**Optimal Function:** {optimal_solution}")
