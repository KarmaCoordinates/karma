import streamlit as st
import pandas as pd
from streamlit_star_rating import st_star_rating
import status_functions as sf

# User feedback
def show_user_feedback(user_input):
    # sattva_choice = st.selectbox('What do you believe your Sattva is?', ('Dominant', 'High', 'Moderate', 'Low'), key='sattva_feedback', on_change=update_ui_status, args=('sattva_feedback', True))
    # rajas_choice = st.selectbox('What do you believe your Rajas is?', ('Low', 'Moderate', 'High', 'Dominant'), key='rajas_feedback', on_change=update_ui_status, args=('rajas_feedback', True))
    # tamas_choice = st.selectbox('What do you believe your Tamas is?', ('Low', 'Moderate', 'High', 'Dominant'), key='tamas_feedback', on_change=update_ui_status, args=('tamas_feedback', True))    
    comments = st.text_input("Comments/suggestions:", on_change=None)
    stars = st_star_rating("Did you find it useful?", maxValue=5, defaultValue=3, key="rating", on_click=sf.update_ui_status('rating', True))
    return {'rating': stars, 'comments':comments}

def save_user_feedback(user_input):
    # print(f'save_user_feedback: {st.session_state['loading']}')
    if 'loading' in st.session_state and st.session_state['loading'] == 'rating' or 'comments':
        df = pd.DataFrame(user_input, index=[0])
        df.to_csv('.tmp/user_feedback.csv', mode='a', index=False, header=False)
        st.markdown('''Your feedback is recorded.''')
