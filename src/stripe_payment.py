# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
import stripe

# stripe.api_key = "sk_test_F58b5frd6lkgbGQ3Yupvrrbp"

# stripe_button = f'''<stripe-buy-button
#     buy-button-id='{{BUY_BUTTON_ID}}'
#     publishable-key="sk_test_F58b5frd6lkgbGQ3Yupvrrbp">
#   </stripe-buy-button>'''

stripe.api_key = 'sk_test_4eC39HqLyjWDarjtT1zdp7dc'
payment_link = 'test_bIY9D4dZ94oc2mk288'

def subscribe():
    # payment_link = stripe.PaymentLink.create(
    # line_items=[
    #     {
    #     "price": "price_1HKiSf2eZvKYlo2CxjF9qwbr",
    #     "quantity": 1,
    #     },
    # ],
    # )
    return