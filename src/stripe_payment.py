# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
import stripe
import streamlit as st
from streamlit.components.v1 import html


# stripe.api_key = "sk_test_F58b5frd6lkgbGQ3Yupvrrbp"

# stripe_button = f'''<stripe-buy-button
#     buy-button-id='{{BUY_BUTTON_ID}}'
#     publishable-key="sk_test_F58b5frd6lkgbGQ3Yupvrrbp">
#   </stripe-buy-button>'''

stripe_button = f'''
<script async
  src="https://js.stripe.com/v3/buy-button.js">
</script>
<stripe-buy-button
  buy-button-id="buy_btn_1Po85eJTeVnJtPF3D0HBocpa"
  publishable-key="pk_test_z52r8l2VyWizJcRiuteweGG1">
</stripe-buy-button>
'''

stripe.api_key = 'sk_test_4eC39HqLyjWDarjtT1zdp7dc'
payment_link = 'test_bIY9D4dZ94oc2mk288'

def subscribe():
    col1, col2 = st.columns([1,1])
    with col1:
        st.markdown('[Subscribe](https://buy.stripe.com/14keWy5LffpzeKkaEE) for unlimited AI (ChatGPT) queries into Indian epics and spiritual content such as Sankhya, Yoga, Vedas, Upanishad, Ramayan, Mahabharat, etc.')
    with col2:
        st.image('.static/qr_14keWy5LffpzeKkaEE.png', width=100)
    # st.write("1")
    # st.markdown(stripe_button, unsafe_allow_html=True)
    # st.write("2")
    # html(stripe_button)
    # st.write("3")
    # st.html(stripe_button)
