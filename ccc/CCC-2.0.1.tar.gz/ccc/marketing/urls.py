from django.urls import include, re_path

from ccc.marketing.views import (CampaignNumbersView,
                                 CampaignRedirectNumbersView, ReportsView)
from ccc.packages.views import DefaultSMSHandler, DefaultVoiceHandler
from ccc.marketing.webhooks.urls import urlpatterns_twilio_webhooks

app_name = 'marketing'

urlpatterns = [
    re_path(r'^campaigns/', include('ccc.marketing.campaigns.urls', 'campaigns')),
    re_path(r'^surveys/', include('ccc.marketing.surveys.urls', 'surveys')),
    re_path(r'^default_voice_handler/$', DefaultVoiceHandler.as_view(), name='default_voice_handler'),
    re_path(r'^default_sms_handler/$', DefaultSMSHandler.as_view(), name='default_sms_handler'),
    re_path(r'^reports/$', ReportsView.as_view(), name='marketing_reports'),
    re_path(r'^numbers/$', CampaignNumbersView.as_view(), name='campaign_numbers'),
    re_path(r'^numbers/redirects/$', CampaignRedirectNumbersView.as_view(), name='redirect_numbers'),

    re_path(r'^autodialer/', include('ccc.marketing.autodialer.urls', namespace='autodialer'))
]

urlpatterns += urlpatterns_twilio_webhooks
