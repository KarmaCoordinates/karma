import streamlit as st
import pandas as pd
from streamlit_star_rating import st_star_rating
import streamlit_functions.state_mgmt_functions as sf
import storage.dynamodb_functions as db
import time
import streamlit_functions.state_mgmt_functions as smf
import __configs

def _init(user_answers):

    if not 'rating' in user_answers:
        user_answers.update({'rating' : None})

    if not 'feedback' in user_answers:
        user_answers.update({'feedback' : None})

    if  'minimum_required_completion_percent' not in st.session_state:
        st.session_state['minimum_required_completion_percent'] = __configs.get_config().minimum_assessment_completion_percent


# # IMP: Reading the data back that is saved by this method
# df_read = pd.read_csv('output.csv', quoting=pd.io.common.csv.QUOTE_ALL)
# # Optionally, you may want to revert the escaping back (if needed)
# df_read['key_value_pairs'] = df_read['key_value_pairs'].str.replace("\\;", ";")
def _save_user_appsupport_request(feedback):
    phl = st.empty()
    # phl.warning(f'*(Note: Feedback needs to be minimum 20 character long. Click number of stars to rate and save your feedback!*)')


# User feedback
def user_feedback():
    # email = st.text_input("Email", key="appsupport_request_email")
    st.markdown("Need help with the app? Send an email to support@ohioedge.com")
    # feedback = st.text_input("Need help with the app? Send an email to support@ohioedge.com", key="appsupport_request")
    # st.button('Clear Chat History', on_click=_save_user_appsupport_request(feedback))




def main():
    pass

if __name__ == '__main__': main()
