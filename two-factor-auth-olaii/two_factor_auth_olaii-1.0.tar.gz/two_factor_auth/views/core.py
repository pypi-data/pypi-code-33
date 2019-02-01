import warnings
from base64 import b32encode
from binascii import unhexlify

import django_otp
import qrcode
import qrcode.image.svg
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from django.forms import Form
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, resolve_url
from django.urls import reverse
from django.utils.http import is_safe_url
from django.utils.module_loading import import_string
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, TemplateView
from django.views.generic.base import View
from django.utils.six import string_types
from django_otp.util import random_hex

from two_factor_auth import signals
from two_factor_auth.models import Totp
from two_factor_auth.utils import get_otpauth_url

from two_factor_auth.views.utils import totp_required

from ..forms import (
    AuthenticationTokenForm, BackupTokenForm,
    MethodForm, TOTPDeviceForm)
from .utils import IdempotentSessionWizardView, class_view_decorator


@class_view_decorator(sensitive_post_parameters())
@class_view_decorator(never_cache)
class LoginView(IdempotentSessionWizardView):
    """
    View for handling the login process, including OTP verification.

    The login process is composed like a wizard. The first step asks for the
    user's credentials. If the credentials are correct, the wizard proceeds to
    the OTP verification step. If the user has a default OTP device configured,
    that device is asked to generate a token (send sms / call phone) and the
    user is asked to provide the generated token. The backup devices are also
    listed, allowing the user to select a backup device for verification.
    """
    template_name = 'two_factor_auth/core/login.html'
    form_list = (
        ('auth', AuthenticationForm),
        ('token', AuthenticationTokenForm),
        ('backup', BackupTokenForm),
    )
    idempotent_dict = {
        'token': False,
        'backup': False,
    }

    def has_token_step(self):
        user = self.get_user()
        if not user or user.is_anonymous:
            return
        try:
            totp = Totp.objects.get(user=user)
            if totp.enabled:
                return totp
            else:
                return False
        except:
            return False

    def has_backup_step(self):
        user = self.get_user()
        if not user or user.is_anonymous:
            return
        try:
            totp = Totp.objects.get(user=user)
            if totp.has_backup_code() and totp.enabled and \
                'token' not in self.storage.validated_step_data:
                return True
            elif not totp.enabled and 'backup' in self.storage.validated_step_data:
                return True
            else:
                return False
        except:
            return False

    condition_dict = {
        'token': has_token_step,
        'backup': has_backup_step,
    }
    redirect_field_name = REDIRECT_FIELD_NAME

    def __init__(self, **kwargs):
        super(LoginView, self).__init__(**kwargs)
        self.user_cache = None
        self.device_cache = None

    def post(self, *args, **kwargs):
        """
        The user can select a particular device to challenge, being the backup
        devices added to the account.
        """
        # Generating a challenge doesn't require to validate the form.
        if 'challenge_device' in self.request.POST:
            return self.render_goto_step('token')

        return super(LoginView, self).post(*args, **kwargs)

    def done(self, form_list, **kwargs):
        """
        Login the user and redirect to the desired page.
        """
        login(self.request, self.get_user())

        redirect_to = self.request.POST.get(
            self.redirect_field_name,
            self.request.GET.get(self.redirect_field_name, '')
        )
        if not is_safe_url(url=redirect_to, host=self.request.get_host()):
            redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

        device = getattr(self.get_user(), 'otp_device', None)
        if device:
            signals.user_verified.send(sender=__name__, request=self.request,
                                       user=self.get_user(), device=device)
        return redirect(redirect_to)

    def get_form_kwargs(self, step=None):
        """
        AuthenticationTokenForm requires the user kwarg.
        """
        if step == 'auth':
            return {
                'request': self.request
            }
        if step in ('token', 'backup'):
            return {
                'user': self.get_user(),
                'initial_device': self.get_device(step),
            }
        return {}

    def get_device(self, step=None):
        """
        Returns the OTP device selected by the user, or his default device.
        """
        if not self.device_cache:
            self.device_cache = Totp.objects.get(user=self.get_user())
        return self.device_cache

    def render(self, form=None, **kwargs):
        """
        If the user selected a device, ask the device to generate a challenge;
        either making a phone call or sending a text message.
        """
        if self.steps.current == 'token':
            self.get_device().generate_challenge()
        return super(LoginView, self).render(form, **kwargs)

    def get_user(self):
        """
        Returns the user authenticated by the AuthenticationForm. Returns False
        if not a valid user; see also issue #65.
        """
        if not self.user_cache:
            form_obj = self.get_form(step='auth',
                                     data=self.storage.get_step_data('auth'))
            self.user_cache = form_obj.is_valid() and form_obj.user_cache
        return self.user_cache

    def get_context_data(self, form, **kwargs):
        """
        Adds user's default and backup OTP devices to the context.
        """
        context = super(LoginView, self).get_context_data(form, **kwargs)
        if self.steps.current == 'token':
            context['device'] = self.get_device()
            context['other_devices'] = []

            context['backup_tokens'] = 1

        if getattr(settings, 'LOGOUT_REDIRECT_URL', None):
            context['cancel_url'] = resolve_url(settings.LOGOUT_REDIRECT_URL)
        elif getattr(settings, 'LOGOUT_URL', None):
            warnings.warn(
                "LOGOUT_URL has been replaced by LOGOUT_REDIRECT_URL, please "
                "review the URL and update your settings.",
                DeprecationWarning)
            context['cancel_url'] = resolve_url(settings.LOGOUT_URL)
        return context


@class_view_decorator(never_cache)
@class_view_decorator(login_required)
class SetupView(IdempotentSessionWizardView):
    """
    View for handling OTP setup using a wizard.

    The first step of the wizard shows an introduction text, explaining how OTP
    works and why it should be enabled. The user has to select the verification
    method (generator / call / sms) in the second step. Depending on the method
    selected, the third step configures the device. For the generator method, a
    QR code is shown which can be scanned using a mobile phone app and the user
    is asked to provide a generated token. For call and sms methods, the user
    provides the phone number which is then validated in the final step.
    """
    success_url = 'two_factor_auth:setup_complete'
    qrcode_url = 'two_factor_auth:qr'
    template_name = 'two_factor_auth/core/setup.html'
    session_key_name = 'django_two_factor-qr_secret_key'
    initial_dict = {}
    form_list = (
        ('welcome', Form),
        ('method', MethodForm),
        ('generator', TOTPDeviceForm),
    )
    condition_dict = {
        'generator': lambda self: self.get_method() == 'generator',
    }
    idempotent_dict = {
    }

    def get_method(self):
        method_data = self.storage.validated_step_data.get('method', {})
        return method_data.get('method', None)

    def get(self, request, *args, **kwargs):
        """
        Start the setup wizard. Redirect if already enabled.
        """
        totp = Totp.objects.devices_for_user(self.request.user)
        if totp.count() == 1:
            if totp[0].enabled:
                return redirect(self.success_url)
        return super(SetupView, self).get(request, *args, **kwargs)

    def get_form_list(self):
        """
        Check if there is only one method, then skip the MethodForm from form_list
        """
        form_list = super(SetupView, self).get_form_list()
        available_methods = [('generator', 'Token generator')]
        if len(available_methods) == 1:
            form_list.pop('method', None)
            method_key, _ = available_methods[0]
            self.storage.validated_step_data['method'] = {'method': method_key}
        return form_list

    def render_next_step(self, form, **kwargs):
        """
        In the validation step, ask the device to generate a challenge.
        """
        next_step = self.steps.next
        return super(SetupView, self).render_next_step(form, **kwargs)

    def done(self, form_list, **kwargs):
        """
        Finish the wizard. Save all forms and redirect.
        """
        # Remove secret key used for QR code generation
        try:
            del self.request.session[self.session_key_name]
        except KeyError:
            pass

        # TOTPDeviceForm
        if self.get_method() == 'generator':
            form = [form for form in form_list if isinstance(form, TOTPDeviceForm)][0]
            device = form.save()
        else:
            raise NotImplementedError("Unknown method '%s'" % self.get_method())

        django_otp.login(self.request, device)
        return redirect(self.success_url)

    def get_form_kwargs(self, step=None):
        kwargs = {}
        if step == 'generator':
            kwargs.update({
                'key': self.get_key(step),
                'user': self.request.user,
            })
        metadata = self.get_form_metadata(step)
        if metadata:
            kwargs.update({
                'metadata': metadata,
            })
        return kwargs

    def get_key(self, step):
        self.storage.extra_data.setdefault('keys', {})
        if step in self.storage.extra_data['keys']:
            return self.storage.extra_data['keys'].get(step)
        key = random_hex(20).decode('ascii')
        self.storage.extra_data['keys'][step] = key
        return key

    def get_context_data(self, form, **kwargs):
        context = super(SetupView, self).get_context_data(form, **kwargs)
        if self.steps.current == 'generator':
            key = self.get_key('generator')
            rawkey = unhexlify(key.encode('ascii'))
            b32key = b32encode(rawkey).decode('utf-8')
            self.request.session[self.session_key_name] = b32key
            context.update({
                'QR_URL': reverse(self.qrcode_url)
            })
        context['cancel_url'] = resolve_url(settings.LOGIN_REDIRECT_URL)
        return context

    def process_step(self, form):
        if hasattr(form, 'metadata'):
            self.storage.extra_data.setdefault('forms', {})
            self.storage.extra_data['forms'][self.steps.current] = form.metadata
        return super(SetupView, self).process_step(form)

    def get_form_metadata(self, step):
        self.storage.extra_data.setdefault('forms', {})
        return self.storage.extra_data['forms'].get(step, None)


@class_view_decorator(never_cache)
@class_view_decorator(totp_required)
class BackupTokenView(FormView):
    """
    View for listing and generating a backup token.

    A user can generate one static backup token. When the user loses
    its phone, this backup token can be used for verification. This backup
    token should be stored in a safe location.
    """
    form_class = Form
    success_url = 'two_factor_auth:backup_token'
    template_name = 'two_factor_auth/core/backup_tokens.html'

    def get_totp(self):
        return Totp.objects.get(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(BackupTokenView, self).get_context_data(**kwargs)
        context['totp'] = self.get_totp()
        return context

    def form_valid(self, form):
        """
        Delete existing backup codes and generate new ones.
        """
        totp = self.get_totp()
        totp.refresh_backup_code()

        return redirect(self.success_url)


@class_view_decorator(never_cache)
@class_view_decorator(totp_required)
class SetupCompleteView(TemplateView):
    """
    View congratulation the user when OTP setup has completed.
    """
    template_name = 'two_factor_auth/core/setup_complete.html'

    def get_context_data(self):
        return {}


@class_view_decorator(never_cache)
@class_view_decorator(login_required)
class QRGeneratorView(View):
    """
    View returns an SVG image with the OTP token information
    """
    http_method_names = ['get']
    default_qr_factory = 'qrcode.image.svg.SvgPathImage'
    session_key_name = 'django_two_factor-qr_secret_key'

    # The qrcode library only supports PNG and SVG for now
    image_content_types = {
        'PNG': 'image/png',
        'SVG': 'image/svg+xml; charset=utf-8',
    }

    def get(self, request, *args, **kwargs):
        try:
            key = self.request.session[self.session_key_name]
        except KeyError:
            raise Http404()

        # Get data for qrcode
        image_factory_string = getattr(settings, 'TWO_FACTOR_QR_FACTORY', self.default_qr_factory)
        image_factory = import_string(image_factory_string)
        content_type = self.image_content_types[image_factory.kind]

        issuer = getattr(settings, 'TOTP_ISSUER', None)
        if isinstance(issuer, string_types) and (issuer != ''):
            issuer = issuer.replace(':', '')
        else:
            issuer = get_current_site(self.request).name

        otpauth_url = get_otpauth_url(accountname=self.request.user.email,
                                      issuer=issuer,
                                      secret=key,
                                      digits=settings.TOTP_DIGITS)

        # Make and return QR code
        img = qrcode.make(otpauth_url, image_factory=image_factory)
        resp = HttpResponse(content_type=content_type)
        img.save(resp)
        return resp
