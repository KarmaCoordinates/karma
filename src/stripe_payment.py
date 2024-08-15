# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
import stripe

stripe.api_key = "sk_test_F58b5frd6lkgbGQ3Yupvrrbp"

stripe_button = f'''<stripe-buy-button
    buy-button-id='{{BUY_BUTTON_ID}}'
    publishable-key="pk_test_z52r8l2VyWizJcRiuteweGG1">
  </stripe-buy-button>'''

    