from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from ccc.common.mixins import LoginRequiredMixin
from ccc.packages.decorators import check_user_subscription


class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = 'crm/marketing/reports.html'

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ReportsView, self).get_context_data(**kwargs)
        context['nav_title'] = 'Reports'
        context['marketing'] = True
        return context


class CampaignNumbersView(LoginRequiredMixin, TemplateView):
    template_name = 'crm/marketing/campaigns/numbers.html'

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CampaignNumbersView, self).get_context_data(**kwargs)
        context['nav_title'] = 'Campaign Numbers'
        context['marketing'] = True
        return context


class CampaignRedirectNumbersView(LoginRequiredMixin, TemplateView):
    template_name = 'crm/marketing/campaigns/redirect-numbers.html'

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CampaignRedirectNumbersView, self).get_context_data(**kwargs)
        context['nav_title'] = 'Redirect Numbers'
        context['marketing'] = True
        return context
