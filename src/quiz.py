import streamlit as st

def take_quiz():    
    grin_emoji = "😀"
    if not 'quiz' in st.session_state:
        st.session_state['quiz'] = None

    if not st.session_state['quiz']:
        st.subheader(f'''Sankhya pop quiz!''')
        plh = st.empty()
        plh_result = st.empty()
        with plh.container():        
            mem = '''What type of memory/knowledge is it?'''
            answer1 = st.selectbox(label=f'''I can't see the emoji clearly: {grin_emoji}.''', placeholder=mem, options=['Ignorance', 'Incapacity', 'Complacency', 'Siddhi'], key="q_cannot_see_clearly", index=None)
            answer2 = st.selectbox(label=f'''I see an unhappy face: {grin_emoji}.''', placeholder=mem, options=['Ignorance', 'Incapacity', 'Complacency', 'Siddhi'], key="q_unhappy_face", index=None)
            answer3 = st.selectbox(label=f'''I see a happy face: {grin_emoji}.''', placeholder=mem, options=['Ignorance', 'Incapacity', 'Complacency', 'Siddhi'], key="q_happy_face", index=None)
            answer4 = st.selectbox(label=f'''I am not interested in knowing.''', placeholder=mem, options=['Ignorance', 'Incapacity', 'Complacency', 'Siddhi'], key="q_donot_want_to_answer", index=None)

        # with plh.container():
        #     col1, col2 = st.columns([.5,.5])
        #     with col1:
        #         st.text(f'''I can't see the emoji clearly: {grin_emoji}''')

        #     with col2:
        #         answer1 = st.multiselect(label=f'''I can't see the emoji clearly: {grin_emoji}. What type of memory is it?''', options=['Ignorance', 'Incapacity', 'Complacency', 'Siddhi'], key="q_cannot_see_clearly")

        #     col1, col2 = st.columns(2)
        #     with col1:
        #         st.text(f'I see an unhappy face: {grin_emoji}')

        #     with col2:
        #         answer2 = st.selectbox('What type of memory is it?', ('Ignorance', 'Incapacity', 'Complacency', 'Siddhi'), key="q_unhappy_face")

        #     col1, col2 = st.columns(2)
        #     with col1:
        #         st.text(f'''I see a happy face: {grin_emoji}''')

        #     with col2:
        #         answer3 =  st.selectbox('What type of memory is it?', ('Ignorance', 'Incapacity', 'Complacency', 'Siddhi'), key="q_happy_face")

        #     col1, col2 = st.columns(2)
        #     with col1:
        #         st.text(f'''I am not interested in knowing: {grin_emoji}''')

        #     with col2:
        #         answer4 = st.selectbox('What type of memory is it?', ('Ignorance', 'Incapacity', 'Complacency', 'Siddhi'), key="q_donot_want_to_answer")
    
        # if len(st.session_state.q_cannot_see_clearly) > 0 and st.session_state.q_cannot_see_clearly[0] == 'Incapacity' and len(st.session_state.q_unhappy_face) == 1 and  st.session_state.q_unhappy_face[0] == 'Ignorance' and len(st.session_state.q_happy_face) == 1 and st.session_state.q_happy_face[0] == 'Siddhi' and len(st.session_state.q_donot_want_to_answer) == 1 and st.session_state.q_donot_want_to_answer[0] == 'Complacency':
        if st.session_state.q_cannot_see_clearly == 'Incapacity' and  st.session_state.q_unhappy_face == 'Ignorance' and st.session_state.q_happy_face == 'Siddhi' and st.session_state.q_donot_want_to_answer == 'Complacency':                    
            st.session_state['quiz'] = True
            plh.success('Perfect!')
        else:
            plh_result.error('Match questions and answers correctly!')
