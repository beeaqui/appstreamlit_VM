from QualityControlFunctions import *


def quality_page():
    st.title(":grey[Quality Control]")

    with st.expander("View Detailed Explanation", expanded=True):
        st.markdown('''In order to conduct the quality control 
                         process, check all products specifications to see if it
                         is in accordance with the requirements.''')
    st.caption("")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c5:
        confirm = st.button('Refresh Data', key=f'refreshQualityBtn', type='primary')
        if confirm:
            st_autorefresh(limit=2, key=f"autoRefreshQuality")

    quality_checks()
