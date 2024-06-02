from QualityControlFunctions import *


def quality_page():
    st.title(":grey[Quality Control]", help='''In order to conduct the quality control process, check all products 
    specifications to see if it is in accordance with the requirements.''')

    st.caption("")

    st_autorefresh(limit=2, interval=20000, key=f"autoRefreshQuality")

    quality_checks()
