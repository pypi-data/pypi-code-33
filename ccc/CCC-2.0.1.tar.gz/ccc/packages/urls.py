from django.conf.urls import url

from ccc.api.phones.views import list
from ccc.packages.webhooks.urls import urlpatterns_stripe_webhooks
from ccc.packages.views import (BuyNumbers, CancelPackageView,
                                DefaultSMSHandler, DefaultVoiceHandler, Pay,
                                RechargePlanListView, RedirectNumberView,
                                ReleaseNumberView, SelectPlanView, BuySubscriptionFormView,
                                campaign_numbers,
                                check_avalaible_phone_numbers, BuyRechargeFormView,
                                remove_redirect)

app_name = 'packages'


urlpatterns = [
    url(r'^select-plan/$', SelectPlanView.as_view(), name='select_plan'),
    url(r'^payment-details/(?P<plan_id>\d+)/$', BuySubscriptionFormView.as_view(), name='buy_plan'),

    url(r'^paypal/$', Pay, name='pay_plan'),
    url(r'^check-number/$', check_avalaible_phone_numbers, name='check_number_int'),

    url(r'^recharge/(?P<plan_id>\d+)/$', BuyRechargeFormView.as_view(), name='recharge'),
    url(r'^recharge/$', RechargePlanListView.as_view(), name='recharge_plans'),

    url(r'^campaign-numbers/$', campaign_numbers, name='campaign_no'),

    url(r'^redirect-numbers/$', RedirectNumberView.as_view(), name='redirect_numbers'),

    url(r'^buy-number/$', BuyNumbers.as_view(), name='buy_no'),

    url(r'^list/$', list, name='api.phone.list'),
    url(r'^delete-redirect/(?P<red_id>\d+)/$', remove_redirect, name='delete_redirect'),

    url(r'^cancel/$', CancelPackageView.as_view(), name='cancel_package'),
    url(r'^release-number/(?P<pk>\d+)/$', ReleaseNumberView.as_view(), name='release_number'),

    url(r'^default-voice-handler/$', DefaultVoiceHandler.as_view(), name='default_voice_handler'),
    url(r'^default-sms-handler/$', DefaultSMSHandler.as_view(), name='default_sms_handler'),
]


urlpatterns += urlpatterns_stripe_webhooks
