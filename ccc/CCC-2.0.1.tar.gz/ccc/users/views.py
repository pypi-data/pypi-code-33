import json
import re

from django import forms
from django.conf import settings as setting
from django.contrib import messages
from django.contrib.auth import (authenticate, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.http.response import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DeleteView
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ccc.campaigns.cloud_tasks import send_email
from ccc.campaigns.models import Campaign, OEmail
from ccc.common.mixins import LoginRequiredMixin
from ccc.packages.decorators import check_user_subscription
from ccc.users.forms import SubAccountForm, UpdatePhoneForm, VerifyOtpForm
from ccc.users.models import ActivationCode, ResetCode, UserProfile
from ccc.users.utils import send_otp, set_cookie, validate_user_phone

SHA1_RE = re.compile('^[a-f0-9]{40}$')


def home(request):
    return render(request, 'home.html')


@csrf_exempt
def register(request):
    if request.method == 'POST':
        # Not a good way to deal with django forms.
        # I would have to add validation here
        # But I would never have added it here if I had time to fix issues
        # Validation should have been done in forms.py
        email = request.POST['email']
        company = request.POST['company']
        password = request.POST['password']
        fullname = request.POST['fullname']
        phone = request.POST['phone']
        try:
            code = setting.DEFAULT_COUNTRY_PHONE
            phone = "{}{}".format(code, phone)
            validate_user_phone(phone)
        except ValidationError as ex:
            message = str(".".join(ex.messages))
            data = json.dumps({'success': 'false', 'message': message})
            return HttpResponse(data)

        # Password Policy
        PASSWORD_MIN_LENGTH = 8

        if len(password) < PASSWORD_MIN_LENGTH:
            message = "Password should be at least %d character long." % PASSWORD_MIN_LENGTH
            data = json.dumps({'success': 'false', 'message': message})
            return HttpResponse(data)

        if not any(c.isdigit() for c in password):
            message = "Password should contain at least 1 digit."
            data = json.dumps({'success': 'false', 'message': message})
            return HttpResponse(data)

        if not any(c.isalpha() for c in password):
            message = "Password should contain at least 1 alphabet."
            data = json.dumps({'success': 'false', 'message': message})
            return HttpResponse(data)

        if not any(c.isupper() for c in password):
            message = "Password should contain at least 1 capital alphabet."
            data = json.dumps({'success': 'false', 'message': message})
            return HttpResponse(data)

        if UserProfile.objects.filter(email__exact=email).count():
            message = 'Email ' + email + '  already in use!'
            data = json.dumps({'success': 'false', 'message': message})
            return HttpResponse(data)

        user = UserProfile(email=email, first_name=fullname, phone=phone, company_name=company, is_active=False)
        user.set_password(password)
        user.save()

        data = json.dumps({'success': 'true',
                           'message': "Your registration is successful. Please check your mail for activation link."})

        # # Send an email to admins about new registration
        # send_email(
        #     subject="New user signup on CCC",
        #     template="ccc/templated_email/new_user_notification.html",
        #     from_=setting.DEFAULT_FROM_EMAIL,
        #     to=setting.ADMINS, context=ctx).execute()

        return HttpResponse(data)

    # If the user is already authenticated, redirect back to where they are coming from or home.
    if request.user.is_authenticated:
        referer = request.META.get('HTTP_REFERER')
        return redirect(referer if referer is not None else '/')

    return render(request, 'crm/auths/registration.html')
    # return render(request, 'ccc/pages/home.html')


def activate_account(request, activation_key):
    # Make sure the key we're trying conforms to the pattern of a
    # SHA1 hash; if it doesn't, no point trying to look it up in
    # the database.
    if SHA1_RE.search(activation_key):
        try:
            token = ActivationCode.objects.get(token=activation_key)
            user = UserProfile.objects.get(id=token.user_id)
            user.is_active = True
            user.save()

            return HttpResponseRedirect('/user/verified/')

        except ActivationCode.DoesNotExist:
            return HttpResponse('No Account Was found, Activation Code was tampered with')
    else:
        return HttpResponse('Activation Key is Wrong!')


class ActivateAccountView(View):
    template_name = 'crm/auths/validation-code-entry.html'

    @staticmethod
    def validate_activation_code(activation_code):
        if SHA1_RE.search(activation_code):
            try:
                # flag token as expired.
                token = ActivationCode.objects.get(token=activation_code, expired=False)
                token.expired = True
                token.save()

                # and finally: flag user account as active and terms accepted.
                UserProfile.objects.filter(id=token.user_id).update(is_active=True, is_accepted_term=True)

                return token.user

            except ActivationCode.DoesNotExist:
                return None
        else:
            return None

    def process_activation(self, request, activation_code):
        if activation_code:
            user = self.validate_activation_code(activation_code)
            if user:
                if user.has_usable_password():
                    return redirect('{}?activation=success'.format(reverse('srm:users:user_login')))
                else:
                    return render(request, self.template_name, {'activation_code': activation_code,
                                                                'can_set_password': True})
            else:
                return redirect('{}?activation=failure'.format(reverse('srm:users:user_login')))
        else:
            return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        activation_code = request.GET.get('activation_code', None)
        password = request.POST.get('password', None)
        confirm_password = request.POST.get('confirm_password', None)
        if not password:
            context = {'error': {'password': 'Passwords cannot be empty'},
                       'activation_code': activation_code, 'can_set_password': True}
            return render(request, self.template_name, context)
        if password != confirm_password:
            context = {'error': {'password': 'Passwords do not match'},
                       'activation_code': activation_code, 'can_set_password': True}
            return render(request, self.template_name, context)
        activation_code = get_object_or_404(ActivationCode, token=activation_code)
        user = activation_code.user
        user.set_password(password)
        user.save()
        return redirect('{}?activation=success'.format(reverse('srm:users:user_login')))

    def get(self, request, *args, **kwargs):
        activation_code = request.GET.get('activation_code', None)
        return self.process_activation(request, activation_code)


def activate_success(request):
    return render(request, 'ccc/users/activate.html')


@csrf_exempt
def login_authentication(request):
    if request.method == 'POST':
        password = request.POST['password']
        email = request.POST['email']

        # specific authentication using username.email if not we can get cannot adapt type model
        user = authenticate(request, username=email, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                # if user.phone:
                # send_otp(phone_number=user.phone.as_e164)
                # return redirect('/')
                return HttpResponse(json.dumps({'success': 'true', 'redirect': request.GET.get('next', '')}))
            else:
                return HttpResponse(json.dumps({'success': 'false',
                                                'message': 'Account Is disabled, contact us to resolve this'}))
        else:
            return HttpResponse(json.dumps({'success': 'false', 'message': 'Login Fail!'}))

    else:
        """If the user is already authenticated, redirect back to where they are coming from or home"""
        if request.user.is_authenticated:
            referer = request.META.get('HTTP_REFERER')
            return redirect(referer if referer is not None else '/')
        return render(request, 'crm/auths/login.html')


@login_required
def do_logout(request):
    logout(request)
    response = redirect('/')
    if request.COOKIES.get('opt_verified'):
        response.delete_cookie('opt_verified')
    return response


@login_required
def teams(request):
    return render(request, 'ccc/users/teams.html')


@login_required
def campaign(request):
    return render(request, 'ccc/users/campaign.html')


@login_required
def contacts(request):
    return render(request, 'ccc/users/contacts.html')


class AnalyticsDataView(GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        campaign_id = request.GET.get('campaign')
        if request.GET.get('analytics_type'):
            data = request.user.get_email_data(campaign=campaign_id, is_email_statics=True)
        else:
            data = request.user.usage_stats(campaign=campaign_id)
        return Response(data)


class DigitalBusinessCardView(LoginRequiredMixin, TemplateView):
    """Dashboard Template View
    """
    template_name = 'crm/users/digital_business_card.html'

    def get_context_data(self, **kwargs):
        context = super(DigitalBusinessCardView, self).get_context_data(**kwargs)
        context['GOOGLE_DEVELOPER_MAP_KEY'] = setting.GOOGLE_DEVELOPER_MAP_KEY
        return context


class DashboardTemplateView(LoginRequiredMixin, TemplateView):
    """Dashboard Template View
    """
    template_name = 'crm/marketing/dashboard.html'

    def get_context_data(self, **kwargs):
        user_profile = self.request.user_profile

        context = super().get_context_data(**kwargs)
        context['balance'] = user_profile.balance
        context['campaign_select'] = self.get_campaign_select()
        context['email_campaign_select'] = self.get_email_campaign_select()
        context['emailstats'] = user_profile.get_email_data(is_email_statics=True)
        context['sent_email_data'] = OEmail.objects.filter(user=self.request.user, campaign__active=True).exclude(
            campaign=None)

        return context

    def get_campaign_select(self):
        choices = forms.ModelChoiceField(queryset=Campaign.objects.filter(user=self.request.user, active=True),
                                         widget=forms.Select(attrs={"class": "form-control"}),
                                         empty_label='All campaigns'
                                         )
        return choices.widget.render('campaign', None)

    def get_email_campaign_select(self):
        choices = forms.ModelChoiceField(queryset=Campaign.objects.filter(user=self.request.user, active=True),
                                         widget=forms.Select(attrs={"class": "form-control"}),
                                         empty_label='All campaigns')
        return choices.widget.render('email_campaign', None)


def reg_success(request):
    return render(request, 'crm/auths/activation-sent.html')


class ProfileUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = UserProfile
    fields = ['first_name', 'last_name', 'email', 'country', 'company_name', 'time_zone', 'profile_image']
    success_message = "Profile updated successfully"
    template_name = "crm/users/profile.html"
    ordering = 'date_joined'
    queryset = UserProfile.objects.all()

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super(ProfileUpdate, self).get_context_data(**kwargs)
        context['profile_edit_form'] = context.get('form')
        context['form'] = PasswordChangeForm(self.request.user)
        context['users'] = self.request.user.children.all()
        return context

    def get_success_url(self):
        return reverse('srm:users:user_profile')


class ChangePassword(View):

    def post(self, request):
        # if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return JsonResponse({'status': 'success', 'url': '/user/dashboard'})

        else:
            error_message = dict([(key, [str(error) for error in value]) for key, value in form.errors.items()])
            return JsonResponse({'status': 'error', 'result': error_message})


@login_required
def social_media(request):
    return render(request, 'ccc/users/social_media.html')


@login_required
def resume(request):
    return render(request, 'ccc/users/resume.html')


@login_required
def sms_campaign(request):
    return render(request, 'ccc/users/sms_campaign.html')


def ResetSuccess(request):
    return render(request, 'crm/auths/forgot-password-email-sent.html')
    # return render(request, 'ccc/users/reset_success.html')


@login_required
def email_campaign(request):
    return render(request, 'ccc/users/email_campaign.html')


@login_required
def voice_campaign(request):
    return render(request, 'ccc/users/voice_campaign.html')


@login_required
def PurchasePlan(request):
    return HttpResponseRedirect('/user/dashboard')


@login_required
def settings(request):
    users = request.user
    if request.method == "POST":
        users.first_name = request.POST['firstname']
        users.last_name = request.POST['lastname']
        users.address = request.POST['address']
        users.company_name = request.POST['company']

        users.designation = request.POST['designation']
        users.fax = request.POST['fax']
        users.contact_no = request.POST['contactnumber']
        users.email = request.POST['email']
        users.save()

        return render(request, 'ccc/users/settings.html')

    return render(request, 'ccc/users/settings.html')


@csrf_exempt
def ResetPass(request):
    if request.method == "POST":
        user = UserProfile.objects.filter(email__exact=request.POST['email'])
        if user:
            email = request.POST['email']

            user = UserProfile.objects.get(email__exact=email)

            ResetCode.objects.create(
                user=user, token_type=2)

            json_data = json.dumps(
                {'message': "Reset email was sent! ", 'success': 'true'})
            return HttpResponse(json_data)

        else:
            data = {'message': 'Account Not Found', 'success': 'false'}

            json_data = json.dumps(data)

            return HttpResponse(json_data)

    else:
        return render(request, 'crm/auths/forgot-password.html')


def NewPass(request, activation_key):
    if request.method == 'POST':
        if request.POST.get('password', None) != request.POST.get('password1', None):
            error = 'Passwords do not match'
            return render(request, 'crm/auths/password-change.html', {'error': error})
        if not request.POST.get('password', None):
            error = 'Password is required'
            return render(request, 'crm/auths/password-change.html', {'error': error})

        if SHA1_RE.search(activation_key):
            profile = ResetCode.objects.get(token=activation_key)
            u = UserProfile.objects.get(id=profile.user.id)

            if not u.is_active:
                error = 'Your Account is disabled contact support'
                return render(request, 'crm/auths/password-change.html', {'error': error})

            u.set_password(request.POST['password'])
            u.save()
            return redirect('{}?new_password=true'.format(reverse('srm:users:user_login')))
        else:
            raise Http404
    else:
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point trying to look it up in
        # the database.
        if SHA1_RE.search(activation_key):
            get_object_or_404(ResetCode, token=activation_key, expired=False)
            return render(request, 'crm/auths/password-change.html')
        else:
            raise Http404


def admincheck(request):
    if request.user.is_staff:
        users = UserProfile.objects.all()
    return render(request, 'ccc/users/users_admin.html', locals())


class ResetPasswordView(TemplateView):
    # template_name = "ccc/pages/reset_password.html"
    template_name = "crm/auths/forgot-password.html"


class VerifyOtpFormView(LoginRequiredMixin, FormView):
    """
    Verify OTP class
    """
    form_class = VerifyOtpForm
    template_name = 'ccc/pages/verify_otp.html'
    success_url = reverse_lazy('srm:users.users.dashboard')

    def dispatch(self, *args, **kwargs):
        return super(VerifyOtpFormView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        if 'view' not in kwargs:
            kwargs['view'] = self
        if not self.request.user.is_anonymous:
            if self.request.user.phone:
                phone = str(self.request.user.phone.as_e164)
                kwargs['partial_phone_no'] = "{}".format(phone[-4:])
        return kwargs

    def get_form_kwargs(self):
        kwargs = super(VerifyOtpFormView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        self.request.session['opt_verified'] = True
        response = HttpResponseRedirect(self.get_success_url())
        set_cookie(response, key='opt_verified',
                   value="true", days_expire=None)
        return response

    def form_invalid(self, form):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        return self.render(self.request, self.get_context_data(form=form))


class ResendOtpView(LoginRequiredMixin, TemplateView):
    """Class to resend OTP
    """
    template_name = 'ccc/pages/verify_otp.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        send_otp(phone_number=self.request.user.phone.as_e164)
        return HttpResponseRedirect(reverse_lazy('srm:users:verify_otp'))


class UpdateUnverifiedPhone(LoginRequiredMixin, FormView):
    """
    Update UnverifiedPhone of user
    """
    form_class = UpdatePhoneForm
    template_name = 'ccc/pages/update_unverified_phone.html'
    success_url = reverse_lazy('srm:users:resend_otp')

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_phone_verified:
            # If phone is already verified then user can not update phone from
            # this view
            return HttpResponseRedirect(self.success_url)
        return super(UpdateUnverifiedPhone, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(UpdateUnverifiedPhone, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        self.request.user.phone = form.cleaned_data['phone']
        self.request.user.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        return self.render(self.request, self.get_context_data(form=form))


@csrf_exempt
def api_login(request):
    """Method to return token for user after validating username
    password
    """
    if request.method == "POST":
        data = json.loads(request.body) or request.POST
        email = data.get("email")
        try:
            username = UserProfile.objects.get(email__exact=email)
        except UserProfile.DoesNotExist:
            username = email
        password = data.get("password")
        user = authenticate(email=username, password=password)
        if not user:
            return HttpResponse(json.dumps({"error": "Login failed"}),
                                content_type="application/json")

        token, _ = Token.objects.get_or_create(user=user)
        return HttpResponse(json.dumps({"token": token.key}),
                            content_type="application/json")
    return HttpResponse(json.dumps({"Error": "Method not allowed"}),
                        content_type="application/json")


class SetTimeZoneView(View):
    """
    set user time zone
    """

    def get(self, request):
        timezone_name = request.GET.get('timezone')
        request.session['timezone'] = timezone_name
        request.session['django_timezone'] = timezone_name
        return HttpResponse('set-time-zone', timezone_name)


def email_support(request):
    if request.method == "POST":
        subject = request.POST.get('subject')
        message = request.POST.get('editor2')
        if message is not None and message != "":
            email = str(request.user)
            name = request.user.get_full_name()
            ctx = {'message': message, 'email': email, 'name': name}
            send_email(subject=subject,
                       email_body=message,
                       from_=setting.DEFAULT_FROM_EMAIL,
                       to='contact@cloudcustomconnections.com',
                       context=ctx).execute()
        return redirect(request.META['HTTP_REFERER'])


class SubUsersView(LoginRequiredMixin, TemplateView):
    template_name = 'crm/users/sub-users.html'

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SubUsersView, self).get_context_data(**kwargs)
        context['nav_title'] = 'Sub Users'
        context['marketing'] = True
        return context
