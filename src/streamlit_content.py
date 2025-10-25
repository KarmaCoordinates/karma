import streamlit as st
import base64
from jinja2 import Template
        
def overview(static_files_folder):
    # logo = f'{static_files_folder}/kapil-muni-image.png'
    # logo = f'{static_files_folder}/sankhya-logo-transparent350x350.png'
    # intro = '''The app enhances clarity of thought through <span style="color:gold">reflective journaling, AI analytics and recommended activities, improving individuals' chances of success.</span> Karma Coordinates, specifically lives to Moksha, serves as an index to track progress towards mental clarity. By focusing on clarity and using Karma coordinates as a metric, individuals can improve decision-making, foster personal growth, and achieve success!'''
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
            height: 150px;
            padding-right: 15px !important;
        }
        .logo-img-wrap {
            object-fit: cover;
            width: auto;
            height: 150px;
            padding-right: 15px !important;
        }
        .app-store-logos {
        display: flex;
        align-items: center;
        }
        .app-store-badge {
        height: 42px; /* Adjust as needed */
        padding: 0 10.45px; /* Applies padding to optically match Google's badge */
        }
        .google-play-badge {
        height: 60px; /* Adjust to match the height of the Apple badge */
        }        
        </style>
        '''

    # title
    st.title('Karma Coordinates')
    # st.markdown(
    #     style,
    #     unsafe_allow_html=True
    # )

    st.markdown(
        f"""{style}""",
        unsafe_allow_html=True
    )        



def background(static_files_folder):
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
            height: 150px;
            padding-right: 15px !important;
        }
        </style>
        '''
    # st.subheader('How does it work?')
    logo = f'{static_files_folder}/logo.png'
    kapil_muni = f'{static_files_folder}/kapil-muni-image.png'
    # pdf = f'<a href="{static_files_folder}/samkhya-karika.pdf">pdf</a>'
    about_karma_coordinates = open(f'{static_files_folder}/karma_coordinates_summary.md', 'r').read()
    # st.markdown(about_karma_coordinates)

    logo_str = f'<img class="logo-img" src="data:image/png;base64,{base64.b64encode(open(logo, "rb").read()).decode()}"  alt="Karma Coordinates">'

    apple_url = 'https://apps.apple.com/us/app/karma-coordinates/id6744322484'
    apple_store_download_logo = f'{static_files_folder}/Download_on_the_App_Store_Badge_US-UK_RGB_blk_092917.svg'
    apple_store_download_logo_str = f'<img class="app-store-badge" src="data:image/svg+xml;base64,{base64.b64encode(open(apple_store_download_logo, "rb").read()).decode()}"  alt="Download app from Apple Store">'

    android_url = 'https://play.google.com/store/apps/details?id=app.sankhya'
    android_store_download_logo = f'{static_files_folder}/GetItOnGooglePlay_Badge_Web_color_English.svg'
    android_store_download_logo_str = f'<img class="google-play-badge" src="data:image/svg+xml;base64,{base64.b64encode(open(android_store_download_logo, "rb").read()).decode()}"  alt="Download app from Google Store">'

    kapil_muni_str =  f'<img class="logo-img" src="data:image/png;base64,{base64.b64encode(open(kapil_muni, "rb").read()).decode()}" alt="Kapil Muni 5561 BCE">'
    
    template = Template(about_karma_coordinates)
    md = template.render(logo = logo_str, apple_download_logo = apple_store_download_logo_str, apple_url = apple_url,
                         android_download_logo=android_store_download_logo_str, android_url = android_url,
                         kapil_muni = kapil_muni_str )

    st.markdown(
        f'''
        {md}
        <div class="container">
            <p class="logo-text"></p>
        </div>
        ''',
        unsafe_allow_html=True
    )    

def guna_details():
    text = '''
    Karma Coordinates outcome is also explained in terms of three *Guna*:  
    - ***Sattv*** is the *Prakash* (light) property in the *Prakriti*. The neural network in our brain - our intellect - has the highest *Sattv*.  
    - ***Rajas*** is the energy property in the *Prakriti*. It moves mass. It activates. Our mind and bodies are enabled by *Rajas*.  
    - ***Tamas*** is the mass property in the *Prakriti*'''

def sankhya_references(static_files_folder):
    subheader = "References"
    references = content = open(f'{static_files_folder}/karma_coordinates_summary_references.md', 'r').read()
    st.subheader(subheader)
    st.markdown(references)

def request_feedback_note():
    # subheader = "Your Feedback"
    feedback = '''Tell us what you think! Your feedback will further refine the Karma Coordinates AI classification system.'''
    # st.subheader(subheader)
    # with st.container(border=True):
    st.markdown(feedback)




