import logging

import paypalrestsdk
from django.conf import settings
from django.contrib.sites.models import Site

logging.basicConfig(level=logging.INFO)


if settings.DEBUG:

    paypalrestsdk.configure({
        "mode": "sandbox",  # sandbox or live
        "client_id": "Ab-KcRCdef_dvavos3A7WHuCrPFQru3-XUL25K3bvbbUoSMJM2bqPtJ7Fych",
        "client_secret": "EMQYRRBuCFZhb3aNGo1MDd5XbSf6m_-PfZefqqqjaa5S0ZsT_hSmLYVP8Kto"})
else:
    paypalrestsdk.configure({
        "mode": "live",
        "client_id": "AaN7rRDtvuZ5VFHGSrxF8z1L2msxmDs4KG77z7JxbD7rgGQg4bj5kgBXoHVk",
        "client_secret": "EPq1vhDAvdhNUx9OXLe3ROjg6IfL_IH5jLG57BuOIzuyH_Z8hxuYUjL7sAaI"})


def paynow(amount, description):

        # #CreatePayment using credit card Sample
    # This sample code demonstrate how you can process
    # a payment with a credit card.
    # API used: /v1/payments/payment

    # ###Payment
    # A Payment Resource; create one using
    # the above types and intent as 'sale'
    payment = paypalrestsdk.Payment({
        "intent": "sale",

        # ###Payer
        # A resource representing a Payer that funds a payment
        # Use the List of `FundingInstrument` and the Payment Method
        # as 'credit_card'
        "payer": {
            "payment_method": "credit_card",

            # ###FundingInstrument
            # A resource representing a Payeer's funding instrument.
            # Use a Payer ID (A unique identifier of the payer generated
            # and provided by the facilitator. This is required when
            # creating or using a tokenized funding instrument)
            # and the `CreditCardDetails`
            "funding_instruments": [{

                # ###CreditCard
                # A resource representing a credit card that can be
                # used to fund a payment.
                "credit_card": {
                    "type": "visa",
                    "number": "4417119669820331",
                    "expire_month": "11",
                    "expire_year": "2018",
                    "cvv2": "874",
                    "first_name": "Joe",
                    "last_name": "Shopper",

                    # ###Address
                    # Base Address used as shipping or billing
                    # address in a payment. [Optional]
                    "billing_address": {
                        "line1": "52 N Main ST",
                        "city": "Johnstown",
                        "state": "OH",
                        "postal_code": "43210",
                        "country_code": "US"}}}]},
        # ###Transaction
        # A transaction defines the contract of a
        # payment - what is the payment for and who
        # is fulfilling it.
        "transactions": [{

            # ### ItemList
            "item_list": {
                "items": [{
                    "name": description,
                    "sku": "ccc",
                    "price": amount,
                    "currency": "USD",
                    "quantity": 1}]},

            # ###Amount
            # Let's you specify a payment amount.
            "amount": {
                "total": amount,
                "currency": "USD"},
            "description": 'Cloud Custom Connections plan purchase'}]})

    # Create Payment and return status( True or False )
    if payment.create():
        print("Payment[%s] created successfully" % (payment.id))
        return payment

    else:
      # Display Error message
        print("Error while creating payment:")
        print(payment.error)


def paywithpp(user, amount, description):
    payment = paypalrestsdk.Payment({
        "intent": "sale",

        # ###Payer
        # A resource representing a Payer that funds a payment
        # Payment Method as 'paypal'
        "payer": {
            "payment_method": "paypal"},

        # ###Redirect URLs
        "redirect_urls": {
            "return_url": "http://" + Site.objects.get_current().domain + "/" + 'payment/execute/' + str(user),
            "cancel_url": "http://" + Site.objects.get_current().domain + "/"},

        # ###Transaction
        # A transaction defines the contract of a
        # payment - what is the payment for and who
        # is fulfilling it.
        "transactions": [{

            # ### ItemList
            "item_list": {
                "items": [{
                    "name": "Cloud Custom Connections Payment ",
                    "sku": "ccc",
                    "price": amount,
                    "currency": "USD",
                    "quantity": 1}]},

            # ###Amount
            # Let's you specify a payment amount.
            "amount": {
                "total": amount,
                "currency": "USD"},
            "description": description}]})

    # Create Payment and return status
    if payment.create():
        print("Payment[%s] created successfully" % (payment.id))
        # Redirect the user to given approval url

        return payment
    else:
        print("Error while creating payment:")

        print(payment.error)
        return False


def excecutepay(payer_id, payment_ref):

    payment = paypalrestsdk.Payment.find(payment_ref)

    # PayerID is required to approve the payment.
    if payment.execute({"payer_id": payer_id}):  # return True or False
        print("Payment[%s] execute successfully" % (payment.id))
        return payment
    else:
        print(payment.error)
        return False
