import calendar
import datetime
import json
from decimal import Decimal

import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, FormView
from twilio.rest import Client as TwilioRestClient

from ccc.billing.models import Customer, PaymentHistory
from ccc.common.mixins import LoginRequiredMixin
from ccc.packages.forms import BillingInfoForm, ChangeCardForm
from ccc.packages.models import Credit, PackageType, PurchasedPackage
from ccc.users.models import UserProfile

ACCOUNT_SID = settings.TWILIO_SID
AUTH_TOKEN = settings.TWILIO_TOKEN

client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def stripe_pay(request):
    pack = request.session['package']
    package = PackageType.objects.get(id=int(pack))

    if request.method == "POST":
        token = request.POST['stripeToken']

        try:

            c = Customer.objects.get(user=request.user)

        except Customer.DoesNotExist:
            c = Customer.objects.create(user=request.user)
        c.billing_name = request.POST['stripeBillingName']
        c.billing_address_1 = request.POST['stripeBillingAddressLine1']
        c.billing_city = request.POST['stripeBillingAddressCity']
        try:
            c.billing_state = request.POST['stripeBillingAddressState']
        except BaseException:
            c.billing_state = 'N/A'
        c.billing_country = request.POST['stripeBillingAddressCountry']
        c.billing_zip = request.POST['stripeBillingAddressZip']
        c.email = request.POST['stripeEmail']
        try:
            customer = stripe.Customer.create(
                card=token,
                description='CCC Customer',
                email=c.email)
            c.customer_id = customer.id
            c.default_card = customer['default_card']

            mycustomer = stripe.Customer.retrieve(customer.id)
            mycard = mycustomer.cards.retrieve(customer['default_card'])

            c.card_last = mycard['last4']
            c.card_type = mycard['type']
            day = calendar.monthrange(mycard["exp_year"], mycard["exp_month"])[1]
            # c.card_expiry = '20'+str(mycard["exp_year"])+'-'+str(mycard["exp_month"])+'-'+str(day)
            c.save()  # save  customer

            # we now have a subscription save its details
            # stripe gives a unix timestamp covert to python datetime object
            # datetime.datetime.fromtimestamp(1004260000)

            # we are now ready to charge the customer
            charge = stripe.Charge.create(amount=int(Decimal(package.cost) * 100), currency="usd",
                                          customer=customer.id,
                                          description=package.title)

            package = request.session['package']
            package = PackageType.objects.get(id=int(package))
            user = PaymentHistory.objects.create(
                user=request.user,
                cost=package.cost,
                completed=True,
                payment_id=charge.id,
                current=True)

            package = PurchasedPackage.objects.create(user=request.user, type=package)

            user.package = package
            package.approved = True
            package.paid = True
            user.save()
            Credit.objects.create(
                package=package,
                sms=package.type.sms,
                mms=package.type.mms,
                email=package.type.email,
                talktime=package.type.talktime)

        except stripe.CardError as e:
            HttpResponse(e)
    return HttpResponseRedirect('/payments/')


@login_required
def stripe_store(request):
    if request.method == "POST":
        token = request.POST['stripeToken']

        try:

            c = Customer.objects.get(user=request.user)

        except Customer.DoesNotExist:
            c = Customer.objects.create(user=request.user)
        c.billing_name = request.POST['stripeBillingName']
        c.billing_address_1 = request.POST['stripeBillingAddressLine1']
        c.billing_city = request.POST['stripeBillingAddressCity']
        try:
            c.billing_state = request.POST['stripeBillingAddressState']
        except BaseException:
            c.billing_state = 'N/A'
        c.billing_country = request.POST['stripeBillingAddressCountry']
        c.billing_zip = request.POST['stripeBillingAddressZip']
        c.email = request.POST['stripeEmail']
        try:
            customer = stripe.Customer.create(
                card=token,
                description='CCC Customer',
                email=c.email)
            c.customer_id = customer.id
            c.default_card = customer['default_card']

            mycustomer = stripe.Customer.retrieve(customer.id)
            mycard = mycustomer.cards.retrieve(customer['default_card'])

            c.card_last = mycard['last4']
            c.card_type = mycard['type']
            day = calendar.monthrange(mycard["exp_year"], mycard["exp_month"])[1]
            # c.card_expiry = '20'+str(mycard["exp_month"])+'-'+str(mycard["exp_month"])+'-'+str(day)
            c.save()  # save  customer
            # stripe gives a unix timestamp covert to python datetime object
            # datetime.datetime.fromtimestamp(1004260000)

        except stripe.CardError as e:

            HttpResponse(e)
    return HttpResponseRedirect('/payments/')


@login_required
def payments(request):
    customer = Customer.objects.filter(user=request.user).order_by('-date_created').first()
    package = PurchasedPackage.objects.filter(user=request.user).order_by('-created_at').first()

    ctx = {
        'package': package,
    }

    if customer:
        default_source = customer.fetch_default_source()
        kwargs = {
            'package': package,
            'customer': customer,
            'card_name': default_source.get('name'),
            'card_last4': default_source.get('last4'),
            'card_type': default_source.get('type') or default_source.get('brand'),
            'exp_month': default_source.get('exp_month'),
            'exp_year': default_source.get('exp_year'),
            'billing_name': '',
            'billing_address_line1': default_source.get('address_line1'),
            'billing_address_line2': default_source.get('address_line2'),
            'billing_address_city': default_source.get('address_city'),
            'billing_address_state': default_source.get('address_state'),
            'billing_address_zip': default_source.get('address_zip'),
            'billing_address_country': default_source.get('address_country'),
        }
        if default_source:
            kwargs['billing_name'] = customer.billing_name

        ctx.update(**kwargs)
    return render(request, 'crm/billing/payments.html', ctx)


@login_required
def payment_history(request):
    payments = PaymentHistory.objects.filter(user=request.user)
    ctx = {
        'payments': payments,
    }
    return render(request, 'crm/billing/payment-history.html', ctx)


def payment_history_search(request):
    pay_num = request.GET.get('payment_number')
    plan = request.GET.get('payment_plan')
    date = request.GET.get('date')
    if date != '':
        new_date = date.split()
        y = int(new_date[0])
        m = int(new_date[1])
        d = int(new_date[2])
        dd = datetime.datetime(y, m, d)
        end_date = dd + datetime.timedelta(1)
        payments = PaymentHistory.objects.filter(
            Q(user=request.user) & Q(payment_id=pay_num) | Q(package__type__title=plan) | Q(
                datetime__range=[dd, end_date]))
    else:
        payments = PaymentHistory.objects.filter(
            Q(user=request.user) & Q(payment_id=pay_num) | Q(package__type__title=plan))
    ctx = {
        'payments': payments,
    }
    return render(request, 'crm/billing/payment-history.html', ctx)


@login_required
def delete_card(request):
    if request.POST:
        customer = Customer.objects.filter(user=request.user).order_by('-date_created')
        if customer:
            customer.delete()
    return HttpResponseRedirect('/payments/')


@login_required
def dash(request):
    return render(request, 'ccc/billing/admin_dash.html', locals())


@csrf_exempt
def all_users(request):
    users = UserProfile.objects.exclude(id=request.user.id)
    data = []
    return HttpResponse(json.dumps(data))


class PaymentDetailView(LoginRequiredMixin, DetailView):
    """Show Details. Payment detail view."""

    model = PaymentHistory
    template_name = "ccc/billing/invoice.html"

    def get_context_data(self, **kwargs):
        context = super(PaymentDetailView, self).get_context_data(**kwargs)
        context['host'] = "http://127.0.0.1:8001/static/"
        context['package'] = context['object'].package
        context['package_type'] = context['package'].type
        return context


class ChangeCardView(LoginRequiredMixin, FormView):
    form_class = ChangeCardForm
    success_url = reverse_lazy('srm:billings:payments')

    def get_context_data(self, **kwargs):
        ctx = super(ChangeCardView, self).get_context_data(**kwargs)
        ctx['STRIPE_PUBLISHABLE_KEY'] = settings.STRIPE_PUBLIC_KEY
        return ctx

    def form_valid(self, form):
        customer = self.request.user_profile.customer
        stripe_customer = customer.get_stripe_customer()
        if stripe_customer is not None:
            current_card = customer.list_stripe_cards().data[0]

            card = stripe_customer.sources.retrieve(current_card.id)

            # update card and save
            card.name = form.cleaned_data['fullname']
            card.exp_month = form.cleaned_data['exp_month']
            card.exp_year = form.cleaned_data['exp_year']
            card.save()

        return super(ChangeCardView, self).form_valid(form)


class ChangeBillingInfoView(LoginRequiredMixin, FormView):
    """Allows to update the billing information"""
    form_class = BillingInfoForm
    success_url = reverse_lazy('srm:billings:payments')

    def get_initial(self):
        initial_data = super(ChangeBillingInfoView, self).get_initial()

        # retrieve stripe customer
        customer = Customer.objects.filter(user=self.request.user) \
            .order_by('-date_created').first()
        stripe_customer = stripe.Customer.retrieve(customer.customer_id)

        existing_billing_info = {key: stripe_customer.sources.data[0].get(key)
                                 for key in Customer.BILLING_KEYS}

        initial_data.update(existing_billing_info)
        initial_data['billing_name'] = customer.billing_name
        return initial_data

    def form_valid(self, form):
        # retrieve stripe customer
        customer = self.request.user_profile.customer
        stripe_customer = customer.get_stripe_customer()

        if stripe_customer is not None:
            # update billing info for card then save again
            for key in Customer.BILLING_KEYS:
                setattr(stripe_customer.sources.data[0],
                        key,
                        form.cleaned_data.get(key) or None)
            stripe_customer.sources.data[0].save()

            customer.billing_name = form.cleaned_data.get('billing_name')
            customer.save()

        return super(ChangeBillingInfoView, self).form_valid(form)
