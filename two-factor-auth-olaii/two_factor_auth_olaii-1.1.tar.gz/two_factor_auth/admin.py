from __future__ import absolute_import, division, print_function, unicode_literals

from django.conf.urls import url
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.contrib.auth.views import redirect_to_login
from django.utils.html import format_html
from django.utils.http import is_safe_url
from django.shortcuts import resolve_url
from django.contrib.admin import AdminSite

from two_factor_auth.views.utils import user_has_totp
from two_factor_auth.utils import monkeypatch_method

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse

from .models import Totp


class TotpAdmin(admin.ModelAdmin):
    """
    :class:`~django.contrib.admin.ModelAdmin` for
    :class:`~two_factor_auth.models.TOTPDevice`.
    """
    list_display = ['user', 'interval', 'qrcode_link']
    readonly_fields = ['qrcode_link']

    def get_queryset(self, request):
        queryset = super(TotpAdmin, self).get_queryset(request)
        queryset = queryset.select_related('user')

        return queryset

    #
    # Columns
    #

    def qrcode_link(self, totp):
        try:
            href = reverse('admin:totp_config', kwargs={'pk': totp.pk})
            link = format_html('<a href="{}">qrcode</a>', href)
        except Exception:
            link = ''

        return link
    qrcode_link.short_description = "QR Code"

    #
    # Custom views
    #

    def get_urls(self):
        urls = [
            url(r'^(?P<pk>\d+)/config/$', self.admin_site.admin_view(self.config_view), name='totp_config'),
            url(r'^(?P<pk>\d+)/qrcode/$', self.admin_site.admin_view(self.qrcode_view), name='totp_qrcode'),
        ] + super(TotpAdmin, self).get_urls()

        return urls

    def config_view(self, request, pk):
        totp = Totp.objects.get(pk=pk)

        try:
            context = dict(
                self.admin_site.each_context(request),
                totp=totp,
            )
        except AttributeError:  # Older versions don't have each_context().
            context = {'totp': totp}

        return TemplateResponse(request, 'two_factor_auth/admin/config.html', context)

    def qrcode_view(self, request, pk):
        totp = Totp.objects.get(pk=pk)

        try:
            import qrcode
            import qrcode.image.svg

            img = qrcode.make(totp.config_url, image_factory=qrcode.image.svg.SvgImage)
            response = HttpResponse(content_type='image/svg+xml')
            img.save(response)
        except ImportError:
            response = HttpResponse('', status=503)

        return response


try:
    admin.site.register(Totp, TotpAdmin)
except AlreadyRegistered:
    # A useless exception from a double import
    pass


class AdminSiteTOTPRequiredMixin(object):
    """
    Mixin for enforcing OTP verified staff users.

    Custom admin views should either be wrapped using :meth:`admin_view` or
    use :meth:`has_permission` in order to secure those views.
    """

    def has_permission(self, request):
        """
        Returns True if the given HttpRequest has permission to view
        *at least one* page in the admin site.
        """
        if not super(AdminSiteTOTPRequiredMixin, self).has_permission(request):
            return False
        return request.user.is_verified()

    def login(self, request, extra_context=None):
        """
        Redirects to the site login page for the given HttpRequest.
        """
        if request.user.is_authenticated and not user_has_totp(request.user) and not request.user.is_verified():
            redirect_to = settings.TWO_FACTOR_SETUP_URL
        else:
            redirect_to = request.POST.get(REDIRECT_FIELD_NAME, request.GET.get(REDIRECT_FIELD_NAME))

        if not redirect_to or not is_safe_url(url=redirect_to, allowed_hosts=settings.ALLOWED_HOSTS):
            redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

        return redirect_to_login(redirect_to)


class AdminSiteTOTPRequired(AdminSiteTOTPRequiredMixin, AdminSite):
    """
    AdminSite enforcing OTP verified staff users.
    """
    pass


def patch_admin():
    @monkeypatch_method(AdminSite)
    def login(self, request, extra_context=None):
        """
        Redirects to the site login page for the given HttpRequest.
        """
        redirect_to = request.POST.get(REDIRECT_FIELD_NAME, request.GET.get(REDIRECT_FIELD_NAME))

        if not redirect_to or not is_safe_url(url=redirect_to, allowed_hosts=settings.ALLOWED_HOSTS):
            redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

        return redirect_to_login(redirect_to)


def unpatch_admin():
    setattr(AdminSite, 'login', original_login)


original_login = AdminSite.login
