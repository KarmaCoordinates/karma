import streamlit as st

def render_buttons(button_list, on_click_callback, button_list_name = None, style_css = None):
    if not button_list:
        return
    
    if not style_css:
        style_css = get_style_css()

    st.markdown(style_css, unsafe_allow_html=True)    

    plh = st.empty()
    for text, col in list(map(list, zip(button_list, plh.columns(len(button_list))))):
        with col:
            col.button(label=text, key=text, on_click=on_click_callback, args={text})


def get_style_css(ele_list=None):
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
            div[data-testid="column"] input * {
                margin: -0.1em;
                padding: 0;
            }
            """
    

    if ele_list:
        for ele in ele_list:
            if 'max-width' in ele:
                ele_style = f''' 
                    [aria-label="{ele['label']}"] {{
                            max-width: {ele['max-width']} !important;
                            # padding: 10px;
                            # border: 2px solid #4CAF50; /* Green border */
                            # border-radius: 5px; /* Rounded corners */
                            # font-size: 14px; /* Input text size */
                    }}  
                '''
                style_css = style_css + ele_style

    style_css = style_css + '</style>'
        

    return style_css


# Example usage:
# ele_list = [{'key':'ti_1', 'label':'ele1', 'type':'text_input', 'callback': on_click_callback, 'args': {'ele1'}, 'max-width': '280px'}, 
#             {'key':'ti_2', 'label':'Send Token', 'type':'button', 'callback': on_click_callback, 'args': {'ele2'}}, 
#             {'key':'ti_3', 'label':'ele3', 'type':'text_input', 'callback': on_click_callback, 'args': {'ele3'}, 'max-width': '70px'}, 
#             {'key':'ti_4', 'label':'Verify Token', 'type':'button', 'callback': on_click_callback, 'args': {'ele4'}}]
# render_elements(ele_list)
def render_elements(ele_list):
    st.markdown(get_style_css(ele_list), unsafe_allow_html=True)    
    plh = st.empty()
    for ele, col in list(map(list, zip(ele_list, plh.columns(len(ele_list))))):
        with col:
            if ele['type'] == 'text_input':
                col.text_input(label=ele['label'], key=ele['label'], on_change=ele['callback'], args=ele['args'])
            if ele['type'] == 'button':
                col.button(label=ele['label'], key=ele['label'], on_click=ele['callback'], args=ele['args'])

def main():
    pass

if __name__ == '__main__': main()

