import streamlit_content 
import streamlit as st
import ai.openai_assistant_chat as osc
import payment.stripe_payment as sp
import assessment.questionnaire_pratyay_sargah as qps
import feedback.feedback_functions as ff
import analytics.pdf_functions as pdf
import security.auth_functions as af
import journal.journal_functions as jf
import analytics.plot_functions as pf
import streamlit_functions.state_mgmt_functions as smf
import jinja2


def page_config(static_files_folder):
    try:
        st.set_page_config(
            page_title='Karma Coordinates',
            page_icon=f'{static_files_folder}/favicon.ico',
            layout='wide'
        )    
    except:
        pass


def run_app():
    static_files_folder = '.static'
    page_config(static_files_folder)
    smf.init()
    streamlit_content.overview(static_files_folder)
    af.identity_msg()
    hide_assessment_questionnaire = True
    if st.session_state.auth:
        qps.retrieve_previous_assessment()
        if st.session_state.previous_user_answers:
            hide_assessment_questionnaire = True
        # web_content.auth_overview(static_files_folder)
        st.subheader('Make a journal entry')
        new_journal_entry=jf.journal_entry()
        # openai_assistant_chat.prompt()
    else:
        # web_content.overview(static_files_folder)
        # openai_assistant_chat.prompt()
        streamlit_content.background(static_files_folder)
        # qz.take_quiz()

    osc.prompt()

    # af.identity_msg()

    # st.subheader('Calculate my Karma Coordinates')    
    placehoder = st.empty()
    percent_completed, score_ai_analysis_query = qps.assessment(placehoder=placehoder, hide_assessment_questionnaire=hide_assessment_questionnaire)
    
    if st.session_state.auth:
        st.subheader('My progress')
        pf.clickable_progress_chart()

    # st.subheader('How does your score compare?')
    pf.bell_curve()        

    if 'karma_coordinates' in st.session_state:
        st.subheader('AI analysis')
        plh = st.container(border=True)
        query=None
        analysis=False
        with plh:
            clicked = st.button('Show and explain my score')
            if clicked:
                query = f'''Explain {score_ai_analysis_query}'''
                osc.prompt_specific(query=query, ai_query=query, plh=plh)     
                analysis = osc.get_assistant_answer_from_cache(query)

        pdf.download_assessment_pdf(st.session_state.user_answers, st.session_state.karma_coordinates, analysis)

        if st.session_state.auth:
            st.subheader('Download Journal as PDF')    
            pdf.download_journal()

    if st.session_state.auth:
        st.subheader('Your feedback')
        with st.container(border=True):
            streamlit_content.request_feedback_note()
            ff.user_feedback(st.session_state.user_answers, percent_completed)

    streamlit_content.sankhya_references(static_files_folder)
    sp.subscribe()


def main():
    # static_files_folder = '.static'
    # page_config(static_files_folder)
    run_app()

if __name__ == '__main__': 
    main()

