from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from ccc.packages.decorators import check_user_subscription


class HomePage(LoginRequiredMixin, TemplateView):
    template_name = 'crm/social_media/home.html'
    extra_context = {'nav_title': 'My Social'}

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class SocialAnalytics(TemplateView):
    template_name = 'crm/social_media/analytics.html'
    extra_context = {'nav_title': 'My Social Analytics'}

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
