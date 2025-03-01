import streamlit as st
import pandas as pd
from streamlit_star_rating import st_star_rating
import streamlit_functions.state_mgmt_functions as sf
import storage.dynamodb_functions as db
import time
import streamlit_functions.state_mgmt_functions as smf
import _configs

def _init(user_answers):

    if not 'rating' in user_answers:
        user_answers.update({'rating' : None})

    if not 'feedback' in user_answers:
        user_answers.update({'feedback' : None})

    if  'minimum_required_completion_percent' not in st.session_state:
        st.session_state['minimum_required_completion_percent'] = _configs.get_config().minimum_assessment_completion_percent


# # IMP: Reading the data back that is saved by this method
# df_read = pd.read_csv('output.csv', quoting=pd.io.common.csv.QUOTE_ALL)
# # Optionally, you may want to revert the escaping back (if needed)
# df_read['key_value_pairs'] = df_read['key_value_pairs'].str.replace("\\;", ";")
def _save_user_feedback(user_answers, percent_completed):
    phl = st.empty()
    # st.write(f'st.session_state.feedback: {st.session_state.user_answers}')
    if len(st.session_state.feedback) > 20:
        if (('rating' in st.session_state and not st.session_state.rating is None) and ('feedback' in st.session_state and not st.session_state.feedback is None)) and (not st.session_state.rating == user_answers['rating'] or not st.session_state.feedback == user_answers['feedback']):
            user_answers.update({'rating': st.session_state.rating, 'feedback':st.session_state.feedback})
            smf.save(phl, 'feedback')
            # try:
            #     db.insert(user_activity_data=user_answers)
            #     # st.session_state.feedback = None
            #     # Create a single string holding key-value pairs
            #     # key_value_pairs = "; ".join(f"{key}={str(value).replace(';', '{0}')}" for key, value in user_answers.items())
            #     # formatted_key_value_pairs = key_value_pairs.format('\\;')
            #     # df = pd.DataFrame({"key_value_pairs": [formatted_key_value_pairs]}, index=[0])            
            #     # df.to_csv('.tmp/user_feedback.csv', mode='a', index=False, header=False)            
            #     phl.success('''Your feedback is recorded.''')
            # except Exception as e:
            #     phl.error(f'''Feedback not recorded. Error{e}''')
            
        else:
            phl = st.empty()
    else: 
        phl.warning(f'*(Note: Feedback needs to be minimum 20 character long. Click number of stars to rate and save your feedback!*)')


# User feedback
def user_feedback(user_answers, percent_completed):
    _init(user_answers)
    feedback = st.text_input("Comments/suggestions:", key="feedback")
    stars = st_star_rating("Did you find it useful?", maxValue=5, defaultValue=3, key="rating", on_click=_save_user_feedback(user_answers, percent_completed))




def main():
    pass

if __name__ == '__main__': main()
