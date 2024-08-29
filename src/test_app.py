import streamlit as st

import plotly.express as px
from streamlit_plotly_events import plotly_events


# # Writes a component similar to st.write()
# fig = px.line(x=[1], y=[1])
# selected_points = plotly_events(fig, key="1")

# # Can write inside of things using with!
# with st.expander('Plot'):
#     fig = px.line(x=[1,2], y=[1,2])
#     selected_points = plotly_events(fig, key="2")

# Select other Plotly events by specifying kwargs
fig = px.line(x=[1,2], y=[1,2])
selected_points = plotly_events(fig, click_event=True, hover_event=False, key="three")
if selected_points:
    print(f'selected: {selected_points}')
