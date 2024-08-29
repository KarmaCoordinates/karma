import matplotlib.pyplot as plt
import dynamodb_functions as db
import pandas as pd
import streamlit as st
import state_mgmt_functions as sf
import statsmodels as sm
import plotly.express as px
from streamlit_plotly_events import plotly_events
import _utils

def progress_chart():    
    email=st.session_state[sf.get_session_vars()._enter_email]
    rows = db.query(partition_key_value=email)
    df = pd.DataFrame(rows)
    x = df[db.get_column_names().date].to_list()
    y = df[db.get_column_names().lives_to_moksha].to_list()
    plt.plot(x, y, marker='o')
    plt.title("My progress")
    plt.xlabel("Timeline")
    plt.ylabel("Karma-coordinates")
    plt.grid()
    st.pyplot(plt)

def clickable_progress_chart():
    email=st.session_state[sf.get_session_vars()._enter_email]
    rows = db.query(partition_key_value=email)
    df = pd.DataFrame(rows)
    df = df[[db.get_column_names().date, db.get_column_names().lives_to_moksha, db.get_column_names().journal_entry]]
    df['Timeline'] = pd.to_datetime(df['date'], unit='s')
    df['Journal'] = df[db.get_column_names().journal_entry].apply(lambda x: _utils.hard_wrap_string_vectorized(x, 15))

    fig = px.scatter(df, x='Timeline', y=db.get_column_names().lives_to_moksha, title="My progress", 
                     hover_data=df[['Journal']], trendline="ols")
    
    fig.update_layout(
        plot_bgcolor='white'
    )    
    fig.data[1].line.color = 'gold'

    selected_points = plotly_events(fig, click_event=True, hover_event=False, key="my_progress_chart")
    # if selected_points:
    #     print(f'selected: {selected_points[0]['pointIndex']}')
