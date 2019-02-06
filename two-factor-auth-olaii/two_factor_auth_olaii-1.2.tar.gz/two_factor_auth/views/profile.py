from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, resolve_url
from django.views.decorators.cache import never_cache
from django.views.generic import FormView, TemplateView

from two_factor_auth.models import Totp
from ..forms import DisableForm

from .utils import class_view_decorator


@class_view_decorator(never_cache)
@class_view_decorator(login_required)
class ProfileView(TemplateView):
    """
    View used by users for managing two-factor configuration.

    This view shows whether two-factor has been configured for the user's
    account. If two-factor is enabled, it also lists the primary verification
    method and backup verification methods.
    """
    template_name = 'two_factor_auth/profile/profile.html'

    def get_context_data(self, **kwargs):
        totp = Totp.objects.devices_for_user(self.request.user)
        if totp.count() == 1:
            totp = totp[0]
            if totp.enabled:
                if totp.backup_key != "":
                    backup_token = True
                else:
                    backup_token = False
            else:
                totp = False
                backup_token = False
        else:
            totp = False
            backup_token = False

        return {
            'totp': totp,
            'backup_token': backup_token
        }


@class_view_decorator(never_cache)
@class_view_decorator(login_required)
class DisableView(FormView):
    """
    View for disabling two-factor for a user's account.
    """
    template_name = 'two_factor_auth/profile/disable.html'
    success_url = None
    form_class = DisableForm

    def get(self, request, *args, **kwargs):
        totps = Totp.objects.devices_for_user(self.request.user)
        if totps.count() != 1:
            return redirect(self.success_url or resolve_url(settings.LOGIN_REDIRECT_URL))
        return super(DisableView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        totps = Totp.objects.devices_for_user(self.request.user)
        for totp in totps:
            totp.enabled = False
            totp.save()
        return redirect(self.success_url or resolve_url(settings.LOGIN_REDIRECT_URL))
