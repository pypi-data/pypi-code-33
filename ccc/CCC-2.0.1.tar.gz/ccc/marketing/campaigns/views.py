from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from ccc.campaigns.models import Campaign
from ccc.packages.decorators import check_user_subscription


class CampaignsView(LoginRequiredMixin, TemplateView):
    template_name = 'crm/marketing/campaigns/create_campaign.html'

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CampaignsView, self).get_context_data(**kwargs)
        context['nav_title'] = 'Campaigns'
        context['marketing'] = True
        context['action_url'] = reverse('srm:api_marketing:campaigns:campaign-list')
        return context


class CampaignsKeywordsView(LoginRequiredMixin, TemplateView):
    template_name = 'crm/marketing/campaigns/keywords.html'

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CampaignsKeywordsView, self).get_context_data(**kwargs)
        context['nav_title'] = 'Campaign Keywords'
        context['marketing'] = True
        return context


class FollowUPCampaignsView(CampaignsView):
    template_name = 'crm/marketing/campaigns/create_campaign.html'

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(FollowUPCampaignsView, self).get_context_data(**kwargs)
        parent_campaign = get_object_or_404(Campaign, pk=kwargs.get('campaign_id'))
        context['nav_title'] = 'Follow Up {}'.format(parent_campaign.name)
        context['marketing'] = True
        context['campaign_type'] = 'follow_up'
        context['is_follow_up'] = True
        context['parent_campaign'] = parent_campaign.id
        context['parent_campaign_phone_id'] = parent_campaign.phone_id
        context['parent_campaign_company'] = parent_campaign.company
        return context


class EditCampaignsView(LoginRequiredMixin, TemplateView):
    template_name = 'crm/marketing/campaigns/create_campaign.html'

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EditCampaignsView, self).get_context_data(**kwargs)
        context['nav_title'] = 'Campaigns'
        campaign_id = kwargs.get('campaign_id')
        campaign = get_object_or_404(Campaign, pk=campaign_id)
        context['marketing'] = True
        context['campaign_id'] = campaign_id
        context['campaign_name'] = campaign.name
        context['nav_title'] = 'Edit Campaign'
        context['is_edit'] = True

        url = reverse('srm:api_marketing:campaigns:campaign-detail', args=[campaign_id])
        context['action_url'] = url + '?archive=true' if self.request.GET.get('archive') else url
        return context


class EditFollowUPCampaignsView(EditCampaignsView):
    template_name = 'crm/marketing/campaigns/create_campaign.html'

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EditFollowUPCampaignsView, self).get_context_data(**kwargs)
        campaign_id = kwargs.get('campaign_id')
        campaign = get_object_or_404(Campaign, pk=campaign_id)
        context['campaign_id'] = campaign_id
        context['campaign_type'] = 'follow_up'
        context['nav_title'] = 'Edit Follow-up ({})'.format(campaign.name)
        context['is_edit'] = True
        context['is_follow_up'] = True
        context['parent_campaign'] = campaign.parent_campaign.id
        context['parent_campaign_phone_id'] = campaign.parent_campaign.phone_id
        context['parent_campaign_company'] = campaign.parent_campaign.company
        url = reverse('srm:api_marketing:campaigns:campaign-detail', args=[campaign_id])
        context['action_url'] = url + '?archive=true' if self.request.GET.get('archive') else url
        return context


class ActiveCampaignsView(LoginRequiredMixin, TemplateView):
    template_name = 'crm/marketing/campaigns/active-campaigns.html'

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ActiveCampaignsView, self).get_context_data(**kwargs)
        context['nav_title'] = 'Active Campaigns'
        context['marketing'] = True
        return context


class FollowUpCampaignsView(LoginRequiredMixin, TemplateView):
    template_name = 'crm/marketing/campaigns/followup-campaigns.html'

    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(FollowUpCampaignsView, self).get_context_data(**kwargs)
        context['nav_title'] = 'Follow-up Campaigns'
        context['marketing'] = True
        return context


campaign_types_readable = {
    'mms': 'MMS',
    'sms': 'SMS',
    'voice': 'Calls',
    'email': 'Emails'
}

campaign_types_templates = {
    'voice': 'crm/marketing/campaigns/voice/voice-campaigns.html',
    'incoming_voice': 'crm/marketing/campaigns/voice/received-calls.html',
    'outgoing_voice': 'crm/marketing/campaigns/voice/outgoing-calls.html',
    'sms': 'crm/marketing/campaigns/sms/sms-campaigns.html',
    'incoming_sms': 'crm/marketing/campaigns/sms/incoming-sms.html',
    'outgoing_sms': 'crm/marketing/campaigns/sms/outgoing-sms.html',
    'mms': 'crm/marketing/campaigns/mms/mms-campaigns.html',
    'incoming_mms': 'crm/marketing/campaigns/mms/incoming-mms.html',
    'outgoing_mms': 'crm/marketing/campaigns/mms/outgoing-mms.html',
    'email': 'crm/marketing/campaigns/email/email-campaigns.html',
    'incoming_email': 'crm/marketing/campaigns/email/incoming-emails.html',
    'outgoing_email': 'crm/marketing/campaigns/email/outgoing-emails.html',
}


class CampaignTypesView(LoginRequiredMixin, TemplateView):
    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_template_names(self):
        campaign_type = self.kwargs.get('campaign_type')
        return [campaign_types_templates.get(campaign_type)]

    def get_context_data(self, **kwargs):
        context = super(CampaignTypesView, self).get_context_data(**kwargs)
        campaign_type = kwargs.get('campaign_type')
        context['nav_title'] = '{} Campaigns'.format(campaign_type.capitalize())
        context['dashboard'] = True
        return context


class CampaignLogTypesView(LoginRequiredMixin, TemplateView):
    @method_decorator(check_user_subscription)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_template_names(self):
        campaign_type = self.kwargs.get('campaign_type')
        campaign_direction = self.kwargs.get('campaign_direction')
        return [campaign_types_templates[f'{campaign_direction}_{campaign_type}']]

    def get_context_data(self, **kwargs):
        campaign_type = self.kwargs.get('campaign_type')
        campaign_direction = self.kwargs.get('campaign_direction')
        context = super(CampaignLogTypesView, self).get_context_data(**kwargs)
        context['nav_title'] = '{} {}'.format(campaign_direction.capitalize(), campaign_types_readable[campaign_type])
        context['dashboard'] = True
        return context
