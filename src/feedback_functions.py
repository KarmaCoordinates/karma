import streamlit as st

# User feedback
def show_user_feedback(user_input):
    global prediction_init
    if prediction_init:    
        sattva_choice = st.selectbox('What do you believe your Sattva is?', ('Dominant', 'High', 'Moderate', 'Low'), key='sattva_feedback', on_change=update_ui_status, args=('sattva_feedback', True))
        rajas_choice = st.selectbox('What do you believe your Rajas is?', ('Low', 'Moderate', 'High', 'Dominant'), key='rajas_feedback', on_change=update_ui_status, args=('rajas_feedback', True))
        tamas_choice = st.selectbox('What do you believe your Tamas is?', ('Low', 'Moderate', 'High', 'Dominant'), key='tamas_feedback', on_change=update_ui_status, args=('tamas_feedback', True))
        stars = st_star_rating("Do you like the concept?", maxValue=5, defaultValue=3, key="rating", on_click=update_ui_status('rating', True))
        return {'rating': stars, 'sattva':sattva_choice, 'rajas': rajas_choice, 'tamas':tamas_choice}
    else: return {}

def save_user_feedback(user_input):
    if 'loading' in st.session_state and st.session_state['loading'] == 'rating':
        df = pd.DataFrame(user_input, index=[0])
        df.to_csv('.tmp/user_feedback.csv', mode='a', index=False, header=False)
        st.markdown('''Your feedback is recorded.''')
