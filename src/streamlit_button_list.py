import streamlit as st

def render_buttons(button_list, on_click_callback, button_list_name, style_css = None):
    if not button_list:
        return
    
    if not style_css:
        style_css = """
        <style>
            div[data-testid="column"] {
                flex: 0 3 max-content !important;  
                min-width: min-content;                   
                justify-content: start !important;
                margin: -0.3em !important;        
                padding: 0;          
                # background-color: gray;
            }
            div[data-testid="column"] * {
                width: fit-content !important;
                padding: 0.015em;
                margin: -0.035em;
                border-radius: 16px;
                # background-color: red;     
            }
            div[data-testid="column"] button {
                height: 1.9em;
                align-items: center;
                justify-content: center;
                padding: 0 0.3em 0 0.3em;
            }
            div[data-testid="column"] button * {
                margin: -0.1em;
                padding: 0;
            }
                
        </style>
        """

    st.markdown(style_css, unsafe_allow_html=True)    

    plh = plh = st.empty()
    for text, col in list(map(list, zip(button_list, plh.columns(len(button_list))))):
        with col:
            col.button(label=text, key=text, on_click=on_click_callback, args={text})
