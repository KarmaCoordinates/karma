import streamlit as st
import pandas as pd
from streamlit_star_rating import st_star_rating
import status_functions as sf

def _init(user_input):
    if not user_input:
        user_input = {}

    if not 'rating' in user_input:
        user_input['rating'] = ''

    if not 'feedback' in user_input:
        user_input['feedback'] = '' 

# User feedback
def user_feedback(user_input):
    _init(user_input)
    feedback = st.text_input("Comments/suggestions:", key="feedback")
    stars = st_star_rating("Did you find it useful?", maxValue=5, defaultValue=3, key="rating", on_click=_save_user_feedback(user_input))

def _save_user_feedback(user_input):
    phl = st.empty()
    if len(st.session_state.feedback) > 20 and len(user_input) > 25 and 'auth' in st.session_state and st.session_state.auth:
        if (('rating' in st.session_state and not st.session_state.rating is None) and ('feedback' in st.session_state and not st.session_state.feedback is None)) and (not st.session_state.rating == user_input['rating'] or not st.session_state.feedback == user_input['feedback']):
            user_input.update({'email': st.session_state.email, 'rating': st.session_state.rating, 'feedback':st.session_state.feedback})
            df = pd.DataFrame(user_input, index=[0])
            df.to_csv('.tmp/user_feedback.csv', mode='a', index=False, header=False)
            phl.success('''Your feedback is recorded.''')
        else:
            phl = st.empty()
    else: 
        phl.warning('*(Note: Feedback needs to be minimum 20 character long. Atleast 50% of assessment needs to be completed. Your identity needs to be confirmed. Click number of stars to rate and save your feedback!*)')

def main():
    pass

if __name__ == '__main__': main()
