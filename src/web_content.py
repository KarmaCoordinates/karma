import streamlit as st
import base64


def page_config(static_files_folder):
    st.set_page_config(
        page_title='Karma Coordinates',
        page_icon=f'{static_files_folder}/favicon.ico',
        layout='wide'
    )    
    # return


def intro(static_files_folder):
    logo = f'{static_files_folder}/kapil-muni-image.png'
    intro = '''The app's primary goal is to enhance the clarity of thinking in individuals, thus giving them the best chance of succeeding in various aspects of life. The calculated Karma Coordinates, specifically the number of lives to Moksha, serves as an incentive index to track and measure progress towards achieving mental clarity. By focusing on improving clarity of thinking and using the calculated coordinates as a metric for progress, individuals can potentially enhance their decision-making abilities, achieve personal growth, and increase their chances of success in different endeavors.'''
    style = '''
        <style>
        .container {
            # display: flex;
        }
        .logo-text {
            # font-weight:700 !important;
            # font-size:50px !important;
            # color: #f9a01b !important;
            # padding-top: 75px !important;
            # padding-left: 15px !important;
        }
        .logo-img {
            object-fit: cover;
            float: left;
            width: auto;
            height: 250px;
            padding-right: 15px !important;
        }
        </style>
        '''

    # title
    st.title('Karma Coordinates Calculator')
    # st.markdown(
    #     style,
    #     unsafe_allow_html=True
    # )

    st.markdown(
        f"""
        {style}
        <div class="container">
            <img class="logo-img" src="data:image/png;base64,{base64.b64encode(open(logo, "rb").read()).decode()}" alt="Kapil Muni 5561 BCE">
            <p class="logo-text">{intro}</p>
        </div>
        """,
        unsafe_allow_html=True
    )    

def brief(static_files_folder):
    st.subheader('Background')
    pdf = f'<a href="{static_files_folder}/samkhya-karika.pdf">pdf</a>'
    about_karma_coordinates = content = open(f'{static_files_folder}/karma_coordinates_summary.md', 'r').read()
    st.markdown(about_karma_coordinates)
    

def guna_details():
    text = '''
    Karma Coordinates outcome is also explained in terms of three *Guna*:  
    - ***Sattv*** is the *Prakash* (light) property in the *Prakriti*. The neural network in our brain - our intellect - has the highest *Sattv*.  
    - ***Rajas*** is the energy property in the *Prakriti*. It moves mass. It activates. Our mind and bodies are enabled by *Rajas*.  
    - ***Tamas*** is the mass property in the *Prakriti*  
'''

def sankhya_references(static_files_folder):
    subheader = "References"
    references = content = open(f'{static_files_folder}/karma_coordinates_summary_references.md', 'r').read()
    st.subheader(subheader)
    st.markdown(references)

def request_feedback_note():
    # subheader = "Your Feedback"
    feedback = '''
Tell us what you think! Your feedback will further refine the Karma Coordinates AI classification system.
        '''
    # st.subheader(subheader)
    # with st.container(border=True):
    st.markdown(feedback)




