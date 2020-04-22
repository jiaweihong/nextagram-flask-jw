from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.payment import Payment
from flask_login import current_user
import braintree
import os

payments_blueprint = Blueprint('payments',
                               __name__,
                               template_folder='templates')

gateway = braintree.BraintreeGateway(  # creates an object so that we can generate the client token
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id=os.environ.get('BT_MERCHANT_ID'),
        public_key=os.environ.get('BT_PUBLIC_KEY'),
        private_key=os.environ.get('BT_PRIVATE_KEY')
    )
)


@payments_blueprint.route("/new")
def new():
    # when this page loads, it sends a request to our server to generate a client-token and sends it back to us
    client_token = gateway.client_token.generate()
    # then sends the client token to the front end
    return render_template("payments/new.html", client_token=client_token)

# this code will receive the nonce
@payments_blueprint.route("/checkout", methods=["POST"])
def create():
    result = gateway.transaction.sale({  # this code then sends the nonce to brain tree's server
        # to check out the data you receive use: "request.form"
        "amount": request.form.get("amount"),
        "payment_method_nonce": request.form.get("paymentMethodNonce"),
        "options": {
            "submit_for_settlement": True
        }
    })
    transaction_id = result.transaction.id
    amount = result.transaction.amount
    payment = Payment(
        amount=amount, transaction_id=transaction_id, user=current_user.id)
    payment.save()
    flash('Payment Sent!')
    return "temp"
