import matplotlib.pyplot as plt
import dynamodb_functions as db
import pandas as pd
import numpy as np
import streamlit as st
import state_mgmt_functions as sf
import statsmodels as sm
import plotly.express as px
from streamlit_plotly_events import plotly_events
import _utils
import scipy.stats as stats
import plotly.graph_objects as go

def progress_chart():    
    email=st.session_state[sf.get_session_vars()._enter_email]
    rows = db.query(partition_key_value=email)
    if rows is None:
        return
    df = pd.DataFrame(rows)
    x = df[db.Columns().date].to_list()
    if not db.Columns().lives_to_moksha in df:
        df[db.Columns().lives_to_moksha] = ''
    y = df[db.Columns().lives_to_moksha].to_list()
    plt.plot(x, y, marker='o')
    plt.title("My progress")
    plt.xlabel("Timeline")
    plt.ylabel("Karma-coordinates")
    plt.grid()
    st.pyplot(plt)

def clickable_progress_chart():
    email=st.session_state[sf.get_session_vars()._enter_email]
    rows = db.query(partition_key_value=email)
    if rows is None:
        return
    df = pd.DataFrame(rows)
    df = df[[db.Columns().date, db.Columns().lives_to_moksha, db.Columns().journal_entry]]
    # df['Timeline'] = df['date'].astype(float).dt.strftime('%m/%d/%Y %H:%M')    
    df['Timeline'] = pd.to_datetime(pd.to_numeric(df['date'], errors='coerce'), unit='s', )
    df['Journal'] = df[db.Columns().journal_entry].apply(lambda x: _utils.insert_line_breaks(x))

    fig = px.scatter(df, x='Timeline', y=db.Columns().lives_to_moksha, 
            labels={
                "lives_to_moksha": "Lives to Moksha"},
            title="My progress", 
            hover_data=df[['Journal']], trendline="ols")
    
    fig.update_layout({
        'plot_bgcolor':'white',
        'hoverlabel.align':'left',
        'xaxis_title':'Timeline',
        'yaxis_title':'Lives to Moksha'}
    )    
    fig.data[1].line.color = 'gold'

    selected_points = plotly_events(fig, click_event=True, hover_event=False, key="my_progress_chart")
    # if selected_points:
    #     print(f'selected: {selected_points[0]['pointIndex']}')


def bell_curve():
    response_df = db.query_columns()
    if response_df is None or response_df.empty:
        return
    data = pd.to_numeric(response_df['lives_to_moksha'].dropna()).to_list()

    # Create the histogram
    histogram = go.Histogram(
        x=data,
        histnorm='probability density',
        name='Score histogram',
        nbinsx=15,
        opacity=0.75
    )

    mean = np.mean(data)
    std_dev = np.std(data)
    # Create a range for the x values
    x_values = np.linspace(mean - 4*std_dev, mean + 4*std_dev, 100)
    # Calculate the corresponding y values for the normal distribution
    y_values = stats.norm.pdf(x_values, mean, std_dev)

    # Create a line for the bell curve
    bell_curve = go.Scatter(
        x=x_values,
        y=y_values,
        mode='lines',
        name='Bell Curve',
        line=dict(color='gold')
    )


    # vline = go.scatter.Line([mean], width=3, dash="dash", color="green")

    # Create the figure
    fig = go.Figure(data=[histogram, bell_curve])

    fig.add_vline(x=mean, line_width=1, line_dash="dash", line_color="gold")


    # Update the layout
    fig.update_layout(title=f'How does your score compare (based on {len(data)} assessments)? ',
                    xaxis_title=f'Lives to Moksha',
                    yaxis_title='Probability Density')
        

    st.plotly_chart(fig, use_container_width=True)

