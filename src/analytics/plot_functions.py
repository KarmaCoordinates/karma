import matplotlib.pyplot as plt
import storage.dynamodb_functions as db
import pandas as pd
import numpy as np
import streamlit as st
import streamlit_functions.state_mgmt_functions as sf
import plotly.express as px
from streamlit_plotly_events import plotly_events
import __utils
import scipy.stats as stats
import plotly.graph_objects as go
import statsmodels.api as sm

def progress_chart():    
    email=st.session_state[sf.get_session_vars()._enter_email]
    rows = db.query(partition_key_value=email, sort_key_prefix=str(__utils.unix_epoc(months_ago=6))[:2], ascending=False)
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
    rows = db.query(partition_key_value=email, sort_key_prefix=str(__utils.unix_epoc(months_ago=6))[:2], ascending=False)

    if rows is None:
        return
    df = pd.DataFrame(rows)
    df = df[[db.Columns().date, db.Columns().lives_to_moksha, db.Columns().journal_entry]]
    # df['Timeline'] = df['date'].astype(float).dt.strftime('%m/%d/%Y %H:%M')    
    df['Timeline'] = pd.to_datetime(pd.to_numeric(df['date'], errors='coerce'), unit='s', )
    df['Journal'] = df[db.Columns().journal_entry].apply(lambda x: __utils.insert_line_breaks(x))

    # Choose theme based on mode (you can set this dynamically)
    is_dark_mode = True  # Or detect from app settings
    template = "plotly_dark" if is_dark_mode else "plotly_white"

    fig = px.scatter(df, x='Timeline', y=db.Columns().lives_to_moksha, 
            hover_data=df[['Journal']], trendline='expanding', template=template)
    
    # fig.update_traces(marker=dict(size=4,
    #                           line=dict(width=4,
    #                                     color='DarkSlateGrey')),
    #               selector=dict(mode='markers'))    
    fig.update_layout({
        'paper_bgcolor':'rgba(0,0,0,0)',
        'plot_bgcolor':'rgba(0,0,0,0)',
        'hoverlabel.align':'left',
        'title':'My progress', 
        'xaxis_title':'Timeline',
        'yaxis_title':'Lives to Moksha'}
    )    
    fig.data[1].line.color = 'gold'

    selected_points = plotly_events(fig, click_event=True, hover_event=False, key="my_progress_chart")

    # if selected_points:
    #     print(f'selected: {selected_points[0]['pointIndex']}')

    # # Create figure
    # layout = go.Layout(
    #     paper_bgcolor='rgba(0,0,0,0)',
    #     plot_bgcolor='rgba(0,0,0,0)'
    # )    

    # # Convert categorical x-axis to numeric values for regression
    # # x_numeric = np.arange(len(df['Timeline']))
    # # print(df['Timeline'])
    # df = df.sort_values('Timeline', ascending=True).reset_index(drop=True)
    # df['x_numeric'] = range(len(df))

    # # df['x_numeric'] = df['Timeline'].apply(lambda x: x.timestamp())
    # # df['x_numeric'] = df['Timeline'].map(pd.Timestamp.toordinal)
    # print(df['x_numeric'])
    # valid_df = df.dropna(subset=[db.Columns().lives_to_moksha])

    # # Calculate trendline
    # # Add a constant for the OLS model (for intercept)
    # X = sm.add_constant(valid_df['x_numeric'])

    # # Fit the OLS model
    # model = sm.OLS(valid_df[db.Columns().lives_to_moksha].astype(float), X).fit()

    # # Predict y values (the trendline)
    # df['Trendline'] = model.predict(sm.add_constant(df['x_numeric']))

    # # slope, intercept = np.polyfit(valid_df['x_numeric'], valid_df[db.Columns().lives_to_moksha].astype(float), 1)
    # # df['Trendline'] = slope * df['x_numeric'] + intercept

    # # Loop df columns and plot columns to the figure
    # # for i in range(1, len(df.columns)):
    # #     col_name = 'S'+ str(i)
    # scatter_plot = go.Scatter(x=df['x_numeric'], y=df[db.Columns().lives_to_moksha],
    #                     mode='markers', # 'lines' or 'markers'
    #                     name="Lives",
    #                     marker=dict(color='gray'),
    #                     hovertext=df['Journal'])
    
    # trendline = go.Scatter(x=df['x_numeric'], y=df['Trendline'], mode='lines', name='Trendline', line=dict(color='gold', dash='dash'))
        
    # fig1 = go.Figure(data=[trendline, scatter_plot], layout=layout)
    

    # fig1.update_layout(title=f'My Progress',
    #                 xaxis_title=f'Timeline',
    #                 yaxis_title=f'Lives to Moksha')

    # selected_points = plotly_events(fig1, click_event=True, hover_event=False, key="my_progress_chart2")

    # fig1.show()   



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
    layout = go.Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )    

    # Create the figure
    fig = go.Figure(data=[histogram, bell_curve], layout=layout)

    fig.add_vline(x=mean, line_width=1, line_dash="dash", line_color="gold")


    # Update the layout
    fig.update_layout(title=f'Score of the society',
                    xaxis_title=f'Lives to Moksha',
                    yaxis_title=f'Probability Density ({len(data)} assessments)')
        

    st.plotly_chart(fig, use_container_width=True)

