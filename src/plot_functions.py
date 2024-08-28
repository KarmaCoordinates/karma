import matplotlib.pyplot as plt
import dynamodb_functions as db
import pandas as pd
import streamlit as st
import status_functions as sf

def progress_chart():    
    email=st.session_state[sf.get_session_vars()._enter_email]
    rows = db.query(partition_key_value=email)
    df = pd.DataFrame(rows)
    x = df[db.get_columns().date].to_list()
    y = df[db.get_columns().lives_to_moksha].to_list()
    plt.plot(x, y, marker='o')
    plt.title("My progress")
    plt.xlabel("Timeline")
    plt.ylabel("Karma-coordinates")
    plt.grid()
    st.pyplot(plt)