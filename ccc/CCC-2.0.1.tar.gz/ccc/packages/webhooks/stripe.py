from datetime import datetime

import stripe
from cloud_tools.contrib.mail.send import send_templated_email
from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ccc.billing.models import Customer, PaymentHistory
from ccc.common.helpers import get_full_url
from ccc.packages.models import Credit, PackageType, PurchasedPackage

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeWebhookView(APIView):
    """Stripe Webhook view"""
    permission_classes = (AllowAny,)

    def __init__(self, *args, **kwargs):
        self.event = None
        super(StripeWebhookView, self).__init__(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.data.get("id", "") == self.event_test_id:
            return Response({'ok': 'Test Event'})

        self.event = stripe.Event.retrieve(request.data["id"])

        if self.event.type == self.event_type and self.event.data:
            response_data = self.handle_stripe_event(self.event)
            return Response(response_data or {'status': 'success'})
        else:
            return Response({'error': 'invalid event'}, status=400)

    def handle_stripe_event(self, event):
        raise NotImplementedError()

    def get_customer(self):
        return Customer.objects.get(customer_id=self.event.data.object.customer)


class InvoiceCreatedView(StripeWebhookView):
    """Invoice Created View webhook handler"""
    event_type = 'invoice.created'
    event_test_id = 'invoice.created_00000000000000'

    def handle_stripe_event(self, event):
        customer = self.get_customer()

        if event.data.object.status == 'draft':
            # calc remaining phone numbers included in current package
            numbers_remaining = customer.user.balance['phones']
            if numbers_remaining < 0:
                numbers_to_charge = numbers_remaining * -1

                # Append an extra charge for the additional numbers to this invoice
                stripe.InvoiceItem.create(
                    customer=event.data.object.customer,
                    amount=settings.ADDITIONAL_PHONE_NUMBER_COST * numbers_to_charge,
                    currency="usd",
                    description="Cloudcustom Solutions additional numbers (%d)" % numbers_to_charge,
                    invoice=event.data.object.id
                )
            return {'Success!'}

        else:
            return {'status': 'Cannot add invoice items: invoice is closed!'}


class PaymentSucceededView(StripeWebhookView):
    """Payment Succeded view handler"""
    event_type = 'invoice.payment_succeeded'
    event_test_id = 'invoice.payment_00000000000000'

    def handle_stripe_event(self, event):
        customer = self.get_customer()
        lines = event.data.object.lines.data
        for line in lines:
            if line.type == "subscription":
                plan = PackageType.objects.get(sku=line.plan.id)
                package = PurchasedPackage.objects.create(user=customer.user, type=plan)

                PaymentHistory.objects.create(user=customer.user,
                                              completed=True,
                                              mode=PaymentHistory.CREDIT_CARD,
                                              cost=event.data.object.total / 100.0,
                                              payment_id=event.data.object.id,
                                              package=package)

                Credit.objects.create(package=package,
                                      sms=package.type.sms,
                                      mms=package.type.mms,
                                      email=package.type.email,
                                      talktime=package.type.talktime,
                                      phones=package.type.phones)

        # If there were payment problems before, we need to clear that now,
        # because this payment succeeded, which means the user has proper
        # billing details provided.
        if customer.user.payment_failed or customer.user.next_payment_attempt:
            customer.user.next_payment_attempt = None
            customer.user.payment_failed = False
            customer.user.save()

        return {'status': 'The successful payment was recorded.'}


class PaymentFailedView(StripeWebhookView):
    event_type = 'invoice.payment_failed'
    event_test_id = 'invoice.payment_00000000000000'

    def handle_stripe_event(self, event):
        customer = self.get_customer()

        next_payment_attempt = event.data.object.next_payment_attempt
        attempt_count = event.data.object.attempt_count

        if next_payment_attempt:
            customer.user.next_payment_attempt = datetime.fromtimestamp(next_payment_attempt)
        else:
            customer.user.next_payment_attempt = None
        customer.user.payment_failed = True
        customer.user.save()

        if next_payment_attempt:
            send_templated_email(
                subject="Problem with your Cloud Custom Connections Account",
                email_template_name='templated_email/payment_failed_email.html',
                sender='hello@cloudcustomconnections.com',
                recipients=customer.user.email,
                email_context={
                    'user': customer.user,
                    'next_payment_attempt': customer.user.next_payment_attempt,
                    'attempt_count': attempt_count,
                    'payments_url': get_full_url('payments'),
                    'suspend_days': 15 - ((attempt_count - 1) * 5),
                }
            )

        return {'status': 'The failed payment attempt was recorded successfully.'}


class SubscriptionDeletedView(StripeWebhookView):
    event_type = 'customer.subscription.deleted'
    event_test_id = 'customer.subscription.deleted_00000000000000'

    def handle_stripe_event(self, event):
        success_details = 'ok'
        customer = self.get_customer()

        if event.data.object.cancel_at_period_end:
            # if cancelled at end of period (probably auto-cancel)

            if customer and customer.auto_switch_from_trial:
                # auto_switch is off, when the user explicitly cancels his plan

                cancelled_package = PackageType.objects.get(sku=event.data.object.plan.id)
                # the cancelled package has a 'package_type_after_trial' property

                stripe_customer = stripe.Customer.retrieve(event.data.object.customer)
                if stripe_customer.default_source:  # FIXME #important!  this a new bug found.
                    stripe_customer.subscriptions.create(
                        plan=cancelled_package.package_type_after_trial.sku)
                    success_details = 'Subscription switched.'
                else:
                    success_details = 'No default source.'

                customer.auto_switch_from_trial = False
                customer.save()
            else:
                success_details = 'Cancelled at the end of the period. No autoswitch.'
                customer.user.plan_cancelled()
        else:
            success_details = 'Cancelled in the middle of the period.'
            customer.user.plan_cancelled()

        return {'status': success_details}
