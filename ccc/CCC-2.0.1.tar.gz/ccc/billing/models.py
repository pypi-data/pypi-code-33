import logging
from datetime import datetime

from django.conf import settings
from django.db import models
from django.urls import reverse
from stripe import error

from ccc.packages.models import PurchasedPackage

logger = logging.getLogger(__name__)


class CurrentBalance(models.Model):
    user = models.OneToOneField(settings.ACCOUNT_USER_PROXY_MODEL, on_delete=models.CASCADE)
    total_sms = models.IntegerField(blank=True, null=True, default=0)
    total_mms = models.IntegerField(blank=True, null=True, default=0)
    total_talktime = models.IntegerField(blank=True, null=True, default=0)
    total_email = models.IntegerField(blank=True, null=True, default=0)
    total_attachment = models.IntegerField(blank=True, null=True, default=0)

    def get_total_sms(self):
        return self.total_sms

    def get_total_talktime(self):
        total_sec = self.total_talktime
        total_minute = total_sec / 60
        sec = total_sec % 60
        if sec == 0:
            rt = total_minute
        else:
            rt = str(total_minute) + "." + str(sec)
        return rt

    def get_total_mms(self):
        return self.total_mms

    def get_total_email(self):
        return self.total_email

    def __str__(self):
        return "%s have %d sms %d sec" % (self.member.email, self.total_sms, self.total_talktime)

    def available_tw_number_to_purchase(self):
        return self.purchased_twilio_number - self.total_added_tw_number

    def save(self, *args, **kwargs):
        try:
            self.available_tw_number_to_purchase = self.purchased_twilio_number - self.total_added_tw_number
        except BaseException:
            self.available_tw_number_to_purchase = 0
        super(CurrentBalance, self).save(*args, **kwargs)


class PaymentHistory(models.Model):
    """Payment History"""
    PAYPAL = '1'
    CREDIT_CARD = '2'

    PAYMENT_SOURCE = ((PAYPAL, 'PAYPAL'), (CREDIT_CARD, 'Credit Card'))

    user = models.ForeignKey(settings.ACCOUNT_USER_PROXY_MODEL, on_delete=models.CASCADE)
    package = models.ForeignKey(PurchasedPackage, blank=True, null=True, on_delete=models.SET_NULL)

    mode = models.CharField(max_length=255, default=2, choices=PAYMENT_SOURCE, verbose_name='Payment Source')
    recharge = models.BooleanField(default=False, verbose_name='Auto Recharged?')
    cost = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, default=0.0)
    datetime = models.DateTimeField(auto_now_add=True)
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    payer_id = models.CharField(max_length=255, blank=True, null=True)
    completed = models.BooleanField(default=False)
    current = models.BooleanField(default=False)

    def __str__(self):
        if self.payment_id:
            return self.user.email + " / " + self.payment_id
        else:
            return self.user.email

    class Meta:
        db_table = 'h_payments'
        verbose_name_plural = 'Payment History'

    def get_absolute_url(self):
        return reverse("payment_detail_url", args=([self.id]))


class Customer(models.Model):
    """ base class for storing customer order information.
    Also this represent a customer in the stripe. A CRM user can to have different associated accounts
    """
    BILLING_KEYS = 'address_line1', 'address_line2', 'address_city', \
                   'address_state', 'address_zip', 'address_country'

    user = models.OneToOneField(settings.ACCOUNT_USER_PROXY_MODEL, on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    customer_id = models.CharField(max_length=255, blank=True, null=True, help_text='Stripe customer ID')

    # billing information
    billing_name = models.CharField(max_length=255, blank=True, null=True)
    billing_address_1 = models.CharField(max_length=255, blank=True, null=True)
    billing_address_2 = models.CharField(max_length=255, blank=True, null=True)
    billing_city = models.CharField(max_length=255, blank=True, null=True)
    billing_state = models.CharField(max_length=255, blank=True, null=True)
    billing_country = models.CharField(max_length=255, blank=True, null=True)
    billing_zip = models.CharField(max_length=10, blank=True, null=True)

    default_card = models.CharField(max_length=255, blank=True, null=True, verbose_name='default card')
    card_last = models.CharField(max_length=255, blank=True, null=True)
    card_type = models.CharField(max_length=255, blank=True, null=True)
    min_bal = models.IntegerField(default=0)
    recharge_to = models.IntegerField(default=10)
    auto_recharge = models.BooleanField(default=False)
    sus_reason = models.CharField(max_length=255, blank=True, null=True)
    card_expiry = models.DateField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    # Trial flag, actions.
    trial_end = models.DateTimeField(null=True, blank=True)
    auto_switch_from_trial = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return "Customer {}".format(self.id)

    class Meta:
        db_table = 'customers'

    @staticmethod
    def api_stripe():
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        return stripe

    def purchase_twilio_numbers(self, numbers):
        """Wrapper function..."""
        return self.user.purchase_twilio_numbers(numbers=numbers)

    def fetch_default_source(self):
        """ Fetches default source (card) from stripe """
        stripe_customer = self.get_stripe_customer()
        default_source = {}
        if stripe_customer is not None:
            sources = stripe_customer.get('sources', {}).get('data', [])
            default_source_id = stripe_customer.get('default_source', None)
            if default_source_id is not None:
                default_source = list(filter(lambda x: x.get('id') == default_source_id, sources) or [{}])[0]

        return default_source

    def add_invoice_extra_phone_numbers(self, quantity):
        """
        This generated a new invoice to the Customer,
        caused by extra phone numbers purchased that are not included in the package.
        """
        amount = settings.ADDITIONAL_PHONE_NUMBER_COST * quantity
        description = settings.ADDITIONAL_PHONE_NUMBER_INVOICE_DESCRIPTION.format(quantity)
        data = {'amount': amount, 'description': description}
        new_invoice = self.add_stripe_invoice(**data)
        return new_invoice

    def add_invoice_recharge_plan(self, chosen_plan):
        """This generate a new invoice to the customer caused by the purchase of  recharge plan"""
        description = settings.ADDITIONAL_PACKAGES_INVOICE_DESCRIPTION
        data = {
            'amount': chosen_plan.stripe_cost,
            'description': description
        }
        new_invoice = self.add_stripe_invoice(**data)
        return new_invoice

    def clear_payment_reminders(self):
        """Clear payment reminders."""
        if self.user.payment_failed or self.user.next_payment_attempt:
            self.user.next_payment_attempt = None
            self.user.payment_failed = False
            self.user.save()

    def get_or_create_stripe_customer(self, token):
        """Get or create a Stripe customer for this instance. Required token.
        This updated automatically self.customer_id (stripe customer_id)"""
        stripe_customer = self.get_stripe_customer()
        if stripe_customer is not None:
            stripe_customer.source = token
            stripe_customer.save()
            return stripe_customer

        else:
            return self.create_stripe_customer(token)

    def create_stripe_customer(self, token):
        """Register/create a new customer in Stripe. Required token transaction."""
        stripe = self.api_stripe()
        new_stripe_customer = stripe.Customer.create(
            source=token,
            email=self.user.email,
            description=self.user.get_full_name()
        )
        self.customer_id = new_stripe_customer.id
        self.save()

        return new_stripe_customer

    def get_stripe_customer(self):
        """Returns the Stripe customer info based in the self.customer_id."""
        stripe = self.api_stripe()
        if self.customer_id:
            return stripe.Customer.retrieve(self.customer_id)
        return None

    def get_stripe_subscriptions(self):
        """API Stripe Wrapper. Returns a list with the subscription/s of this customer"""
        stripe_customer = self.get_stripe_customer()
        if stripe_customer is not None:
            return stripe_customer.subscriptions

        return []

    def add_stripe_invoice(self, **kwargs):
        """Allow to add and charges an additional invoice to the Customer"""
        stripe = self.api_stripe()

        kwargs['customer'] = self.customer_id
        kwargs['currency'] = "usd"
        new_invoice = stripe.InvoiceItem.create(**kwargs)
        return new_invoice

    def subscribe_to_stripe_plan(self, chosen_plan):
        """
        Subscribe the customer to the chosen_plan in Stripe. (This creates an invoice, and charges the user)
        + Cancel subscription at the end of the month if trial.
        + Clear payment reminders (subscription was successful).
        """
        stripe = self.api_stripe()
        kwargs = {
            'customer': self.customer_id,
            'plan': chosen_plan.sku,
        }

        # subscribe customer to stripe plan
        subscription = stripe.Subscription.create(**kwargs)

        #  clear payment reminders (subscription was successful).
        self.clear_payment_reminders()

        # Cancel subscription at the end of the month if trial.
        if chosen_plan.package_type_after_trial:
            subscription.cancel_at_period_end = True
            subscription.save()

            self.auto_switch_from_trial = True
            self.trial_end = datetime.fromtimestamp(subscription.current_period_end)
            self.save()

        return subscription

    def cancel_stripe_subscription(self):
        """Cancel the active subscription/s of the user at stripe"""
        for subs in self.get_stripe_subscriptions():
            try:
                subs.delete()
            except error.InvalidRequestError as e:
                # Swallow "No active subscriptions for customer:" (404) error,
                # all others must be re-raised
                if not e.http_status == 404:
                    logger.error("Error canceling subscription for Customer{} ".format(self.customer_id))
                    raise e

    def list_stripe_cards(self):
        """Returns the list of cards associated to this customer"""
        stripe = self.api_stripe()
        return stripe.Customer.retrieve(self.customer_id).sources.list(limit=100, object='card')

    def delete_stripe_card(self):
        """Delete all cards associated to this customer in Stripe"""

        for cards in self.list_stripe_cards():
            cards.delete()
