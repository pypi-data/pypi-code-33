import logging
import re

import paypal
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, FormView, View
from django.views.generic import ListView
from twilio.request_validator import RequestValidator
from twilio.rest import Client as TwilioRestClient
from twilio.twiml.voice_response import VoiceResponse

from ccc.billing.models import Customer
from ccc.billing.models import PaymentHistory
from ccc.campaigns.models import RedirectNumber
from ccc.common.mixins import (AjaxableResponseMixin, LoginRequiredAjaxMixin,
                               LoginRequiredMixin)
from ccc.packages.forms import (CreditCardAndBillingInfoForm, PackageForm,
                                PasswordForm, RedirectNumberCreateForm)
from ccc.packages.models import PackageType, PurchasedPackage, TwilioNumber

ACCOUNT_SID = settings.TWILIO_SID
AUTH_TOKEN = settings.TWILIO_TOKEN

logger = logging.getLogger(__name__)
SHA1_RE = re.compile('^[a-f0-9]{40}$')

client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)


# TODO: this into User model
def onetime_charge_for_additional_numbers(user, numbers_to_charge):
    """ This creates a one-time charge for the user when buying additional
    numbers. """

    if numbers_to_charge > 0:
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        customer = user.customer
        stripe_customer = stripe.Customer.retrieve(customer.customer_id)
        charge = stripe.Charge.create(amount=settings.ADDITIONAL_PHONE_NUMBER_COST * numbers_to_charge, currency='usd',
                                      description='Cloudcustom Solutions additional numbers (%d)' % numbers_to_charge,
                                      customer=stripe_customer)
        PaymentHistory.objects.create(
            user=user,
            cost=charge.amount / 100.0,
            completed=True,
            payment_id=charge.id,
            current=True
        )


@csrf_exempt
@login_required
def check_avalaible_phone_numbers(request):
    """Check avalaible phone numbers, via twilio API."""
    number = request.POST['number']
    num_type = request.POST['num_type']

    data = {}
    try:
        country = request.POST.get('country', "US")  # by default find US numbers
        if num_type == 'int':

            if number != '':
                import re
                number = re.sub(r'\W+', '', number)

                # numbers = client.phone_numbers.search(mms_enabled="true",country="CA")

                # 5x API
                #                 numbers = client.phone_numbers.search(country=country,contains=number,voice_enabled='true')

                # Upgrading to 6x API
                client.api.available_phone_numbers(country).local.list(contains=number, voice_enabled='true')

            else:
                #                 numbers = client.phone_numbers.search(country=country,voice_enabled="true")
                numbers = client.api.available_phone_numbers(country).local.list(voice_enabled='true')

        elif num_type == 'local':
            area_code = request.POST['area_code']
            country = "US"
            if number != '':
                import re
                number = re.sub(r'\W+', '', number)
                #                 numbers = client.phone_numbers.search(contains=number,area_code=area_code)
                numbers = client.api.available_phone_numbers(country).local.list(contains=number, area_code=area_code)
            else:
                #                 numbers = client.phone_numbers.search(contains=number,area_code=area_code,voice_enabled='true')
                numbers = client.api.available_phone_numbers(country).local.list(
                    contains=area_code, area_code=area_code, voice_enabled='true')

        # numbers = client.api.available_phone_numbers(country).local.list(contains=area_code,voice_enabled='true')
        elif num_type == 'tf':
            if number != '':
                import re
                number = re.sub(r'\W+', '', number)
                #                 numbers = client.phone_numbers.search(type="tollfree",contains=number)
                numbers = client.api.available_phone_numbers(country).toll_free.list(contains=number)
            else:
                #                 numbers = client.phone_numbers.search(type="tollfree")
                area_code = request.POST.get('area_code') or ''
                if area_code:
                    numbers = client.api.available_phone_numbers(country).toll_free.list(area_code=area_code)
                else:
                    numbers = client.api.available_phone_numbers(country).toll_free.list()
        else:
            numbers = client.api.available_phone_numbers("US").local.list()

        if numbers:
            data = {}
            for i in numbers:
                data[i.phone_number] = i.friendly_name

            return render(request, 'ccc/users/number.html', {'phones': data})

            # numbers[0].purchase()
        else:

            return render(request, 'ccc/users/number.html')
    except BaseException:
        # Getting avaliable "Phone Numbers...."
        avalaible_phone_numbers = client.api.available_phone_numbers(country).local.list(contains=number + '*',
                                                                                         sms_enabled='true',
                                                                                         voice_enabled='true')
        if avalaible_phone_numbers:
            data = {}
            for i in avalaible_phone_numbers:
                data[i.phone_number] = i.friendly_name

            return render(request, 'ccc/users/number.html', {'phones': data})

        return render(request, 'ccc/users/number.html', {'phones': data})

    return render(request, 'ccc/packages/payment.html')


class SelectPlanView(LoginRequiredAjaxMixin, AjaxableResponseMixin, FormView):
    template_name = 'crm/packages/subscription-plans.html'
    form_class = PackageForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if PurchasedPackage.objects.filter(user=self.request.user):
            return HttpResponseRedirect(reverse('srm:users:users.dashboard'))
        return super(SelectPlanView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(SelectPlanView, self).get_context_data(**kwargs)
        ctx['plans'] = PackageType.subscription_objects.all()
        return ctx

    def form_valid(self, form):
        package_type = form.cleaned_data.get('package')
        self.request.session['numbers'] = form.cleaned_data.get('numbers')

        return self.render_to_json_response(
            {'status': 'success', 'redirect_to': reverse('srm:packages:buy_plan', kwargs={'plan_id': package_type.pk})}
        )


class RechargePlanListView(ListView):
    """Recharges Plan List view"""
    template_name = 'crm/packages/recharge-plans.html'
    context_object_name = 'plans'
    queryset = PackageType.recharge_objects.all()


class BuyFormView(FormView):
    """Class base for differents 'BuyFormViews' """
    template_name = 'crm/packages/payment.html'
    form_class = CreditCardAndBillingInfoForm
    success_url = reverse_lazy('srm:users:users.dashboard')

    def get_initial(self):
        initial_data = super(BuyFormView, self).get_initial()
        exists_customer = hasattr(self.request.user_profile, 'customer')

        if exists_customer:
            customer = self.request.user_profile.customer
            stripe_customer = customer.get_stripe_customer()

            # If customer (billing account) is also in stripe...
            if stripe_customer is not None:
                # todo encapsulated this logic. #DRF
                sources_data = stripe_customer.sources.data or None
                if sources_data is not None:
                    existing_billing_info = {key: stripe_customer.sources.data[0].get(key)
                                             for key in Customer.BILLING_KEYS}

                    initial_data.update(existing_billing_info)
                    initial_data['billing_name'] = customer.billing_name

        return initial_data

    def create_customer(self):
        """Get or create a new billing customer"""
        form = self.get_form()
        if form.is_valid():
            # Get or create local Customer (billing account) instance.
            customer = form.save_customer(self.request)

            return customer

    def get_or_create_stripe_customer(self):
        """
        Get or create the customer in Stripe, this is associated to our local model Customer,
        using the field customer_id"""
        from stripe.error import CardError
        token = self.get_stripe_token()
        form = self.get_form()

        if token:
            customer = self.request.user_profile.customer
            try:
                stripe_customer = customer.get_or_create_stripe_customer(token=token)
                return stripe_customer, None
            except CardError as e:
                body = e.json_body
                err = body.get('error', {})
                form.add_error('card_number', err.get('message', 'Error. Please, contact to the support.'))
                return None, self.form_invalid(form)
            except Exception as e:
                logger.error(str(e))
                raise Exception(e)

        raise Exception('You need provided a valid token.')

    def get_context_data(self, **kwargs):
        context_data = super(BuyFormView, self).get_context_data(**kwargs)
        context_data['amount'] = self.calculate_amount()
        context_data['STRIPE_PUBLISHABLE_KEY'] = settings.STRIPE_PUBLIC_KEY
        return context_data

    def buy_now(self):
        """you need to implemented this method."""
        raise NotImplemented

    def form_valid(self, form):
        """Executed when form is valid."""
        if self.get_stripe_token():
            return self.buy_now()

        return super(BuyFormView, self).form_valid(form)

    def get_stripe_token(self):
        """Returns the token/session received via stripe in front end."""
        if 'stripeToken' in self.request.POST:
            return self.request.POST['stripeToken']

        return None

    def get_chosen_numbers_from_session(self):
        """Returns selected phone numbers. Via request.session"""
        return self.request.session.get('numbers', []) or []

    def get_chosen_package(self):
        return get_object_or_404(PackageType, pk=self.kwargs['plan_id'])

    def calculate_amount(self):
        """Calculate amount based on extra numbers and plan-cost"""
        chosen_numbers = self.get_chosen_numbers_from_session()
        chosen_plan = self.get_chosen_package()
        if len(chosen_numbers) > chosen_plan.phones:
            numbers_to_charge = len(chosen_numbers) - chosen_plan.phones
        else:
            numbers_to_charge = 0

        amount = float(chosen_plan.cost) + settings.ADDITIONAL_PHONE_NUMBER_COST / 100.0 * numbers_to_charge
        return amount


class BuySubscriptionFormView(BuyFormView):
    """Allow to buy a new plan."""
    template_name = 'crm/packages/payment.html'
    form_class = CreditCardAndBillingInfoForm
    success_url = reverse_lazy('srm:marketing:campaigns:create_campaign')

    def buy_now(self):
        """Processing the payment"""
        chosen_plan = self.get_chosen_package()
        customer = self.create_customer()
        stripe_customer, err = self.get_or_create_stripe_customer()
        if err:
            return err

        # Try to purchase numbers at twilio
        purchased_numbers = customer.purchase_twilio_numbers(self.get_chosen_numbers_from_session())

        # Add Invoice item for the additional numbers if necessary.
        if len(purchased_numbers) > chosen_plan.phones:
            numbers_to_charge = len(purchased_numbers) - chosen_plan.phones
            customer.add_invoice_extra_phone_numbers(quantity=numbers_to_charge)

        # Subscribe customer to the plan/package.
        customer.subscribe_to_stripe_plan(chosen_plan)

        messages.info(self.request, 'Thank you for your payment. Start making new campaigns.')

        return HttpResponseRedirect(self.get_success_url())


class BuyRechargeFormView(BuyFormView):
    """Allow to buy additional packages"""
    template_name = 'crm/packages/payment.html'
    form_class = CreditCardAndBillingInfoForm
    success_url = reverse_lazy('srm:marketing:campaigns:create_campaign')

    def buy_now(self):
        customer = self.create_customer()
        chosen_plan = self.get_chosen_package()
        stripe_customer, err = self.get_or_create_stripe_customer()
        if err:
            return err
        stripe_customer.subscriptions.create(plan=chosen_plan.sku)
        customer.add_invoice_recharge_plan(chosen_plan)

        return HttpResponseRedirect(self.get_success_url())


def Pay(request):
    package = request.session['package']

    package = PackageType.objects.get(id=int(package))

    payment = paypal.paywithpp(request.user.id, int(package.cost), package.title)
    if payment:

        packages = PurchasedPackage.objects.create(user=request.user, type=package)
        user = PaymentHistory.objects.create(
            user=request.user,
            completed=False,
            payment_id=payment.id,
            mode=1,
            cost=package.cost,
            package=packages)

        user.save()
        for link in payment.links:

            if link.method == "REDIRECT":
                redirect_url = link.href
                return HttpResponseRedirect(redirect_url)
    else:
        pass


@login_required
def campaign_numbers(request):
    """Get campaign numbers"""
    context = {}
    context['twilio_numbers'] = TwilioNumber.objects.filter(user=request.user).order_by('-date_created')

    # Get userprofile information, via proxy model.
    context['balance'] = request.user_profile.balance

    return render(request, 'ccc/campaigns/campaign_no.html', context)


class BuyNumbers(LoginRequiredAjaxMixin, AjaxableResponseMixin, View):
    def post(self, request, *args, **kwargs):
        numbers = request.POST.getlist('numbers', [])
        if not numbers:
            return self.render_to_json_response({'error': 'Choose at least one number'}, status=400)
        else:
            # get generic UserProfile instance. Proxy model for compatibility between ccs ecosystem apps.
            # calc remaining phone numbers included in current package
            numbers_remaining = request.user_profile.balance['phones']
            if numbers_remaining < 0:
                numbers_remaining = 0

            # purchase the numbers at twilio
            purchased_numbers = request.user_profile.purchase_twilio_numbers(numbers=numbers)

            # charge the user for the new numbers
            numbers_to_charge = len(purchased_numbers) - numbers_remaining
            onetime_charge_for_additional_numbers(request.user_profile, numbers_to_charge)

            return self.render_to_json_response({'status': 'success', 'redirect_to': reverse('campaign_no')})


class RedirectNumberView(CreateView):
    model = RedirectNumber
    form_class = RedirectNumberCreateForm
    template_name = 'ccc/campaigns/red_no.html'
    success_url = reverse_lazy('redirect_numbers')

    def get_form_kwargs(self):
        kwargs = super(RedirectNumberView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super(RedirectNumberView, self).get_context_data(**kwargs)
        ctx['numbers'] = RedirectNumber.objects.filter(user=self.request.user)
        ctx['tw_phones'] = TwilioNumber.objects.filter(user=self.request.user,
                                                       is_redirected=False)
        return ctx

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()

        twilio_number = form.cleaned_data.get('from_no')
        twilio_number.is_redirected = True
        twilio_number.save()

        return super(RedirectNumberView, self).form_valid(form)


def remove_redirect(request, red_id):
    red_no = RedirectNumber.objects.filter(id=red_id)
    if red_no:
        red_no = red_no[0]
        twilio = red_no.from_no
        twilio.is_redirected = False
        twilio.save()

        red_no.delete()

    return HttpResponseRedirect('/redirect-numbers/')


class CancelPackageView(FormView):
    form_class = PasswordForm
    template_name = 'crm/packages/cancel.html'
    success_url = reverse_lazy('srm:packages:select_plan')

    def get_form_kwargs(self):
        kwargs = super(CancelPackageView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super(CancelPackageView, self).get_context_data(**kwargs)
        ctx['package'] = PurchasedPackage.objects.filter(
            user=self.request.user).order_by('-created_at').first()
        return ctx

    def form_valid(self, form):
        self.request.user_profile.cancel_plan()
        return super(CancelPackageView, self).form_valid(form)


class TwilioIncomingGenericHandler(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        # Validating incoming request:
        # https://www.twilio.com/docs/api/security#validating-requests
        validator = RequestValidator(settings.TWILIO_TOKEN)
        if not validator.validate(
            uri=request.build_absolute_uri(),
            params=request.POST.dict(),
            signature=request.META.get('X-Twilio-Signature', request.META.get('HTTP_X_TWILIO_SIGNATURE', ''))
        ):
            return HttpResponse('Unauthorized', status=401)

        return super(TwilioIncomingGenericHandler, self).dispatch(request, *args,
                                                                  **kwargs)

    def get_twilio_number(self):
        to = self.request.POST.get("To", '')
        return get_object_or_404(TwilioNumber, twilio_number=to)

    def post(self, request):
        self.twilio_number = self.get_twilio_number()
        return HttpResponse(self.get_response(), content_type='application/xml')

    def get_response(self):
        raise NotImplementedError()


class TwilioIncomingVoiceHandler(TwilioIncomingGenericHandler):
    def post(self, request):
        self.twilio_number = self.get_twilio_number()

        redirect_no = RedirectNumber.objects.filter(from_no=self.twilio_number).first()
        if self.twilio_number.is_redirected and redirect_no:
            response = self.get_redirected_response(redirect_no)
        else:
            response = self.get_response()

        return HttpResponse(response, content_type='application/xml')

    def get_redirected_response(self, redirect_no):
        resp = VoiceResponse()
        resp.dial(redirect_no.to_no)
        return HttpResponse(resp, content_type='application/xml')

    def response(self, resp):
        raise NotImplementedError()


class DefaultVoiceHandler(TwilioIncomingVoiceHandler):
    def get_response(self):
        resp = VoiceResponse()
        resp.say("Sorry, this number is not in use at the moment.")
        return HttpResponse(resp, content_type='application/xml')


class DefaultSMSHandler(TwilioIncomingGenericHandler):
    def get_response(self):
        resp = VoiceResponse()
        resp.message('Sorry, this number is not in use at the moment.')
        return HttpResponse(resp, content_type='application/xml')


class ReleaseNumberView(LoginRequiredMixin, AjaxableResponseMixin, DeleteView):
    model = TwilioNumber

    def get_queryset(self):
        qs = super(ReleaseNumberView, self).get_queryset()
        return qs.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        number = self.get_object()
        if number.get_campaign() or number.surveys.all():
            return self.render_to_json_response(
                {
                    'error': "Couldn't release this number, because it is still in use. Please archive connected campaign or survey and try again."},
                status=400)
        else:
            # call async task
            number.task_release_twilio_number()
            return self.render_to_json_response({'status': "released"}, status=204)
