from AssemblyFunctions import *


def assembly_page():
    st.title('Assembly Process')

    with st.expander("View Additional Information", expanded=True):
        st.markdown(
            '''
            \n *Note: Ensure that each step is completed with precision for proper assembly.*
            \n If you encounter any issues or have questions, talk with your teammates or call the instructor.
            '''
        )
    st.caption("")

    option = st.selectbox(
        ":blue[**Choose the variant of the cylinder to see the assembly operations**]",
        ("Basic Cylinder", "Connectors Push-in Fitting", "Connectors Push-in L-Fitting", "Mixed Connectors"))

    st.title("")

    if option == "Basic Cylinder":
        basic_cylinder_operations()

    elif option == "Connectors Push-in Fitting":
        push_fitting_operations()

    elif option == "Connectors Push-in L-Fitting":
        push_l_operations()

    elif option == "Mixed Connectors":
        mixed_connectors_operations()
