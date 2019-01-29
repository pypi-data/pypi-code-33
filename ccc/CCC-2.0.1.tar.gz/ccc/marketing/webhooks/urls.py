from django.conf.urls import url
from ccc.marketing.webhooks import twilio

urlpatterns_twilio_webhooks = [
    url(r'^twilio_sms_status/$', twilio.TwilioWebHookSMSStatus.as_view(), name='sms_callback'),
]
