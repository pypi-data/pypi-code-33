from django.urls import path
from rest_framework.routers import SimpleRouter

from ccc.marketing.campaigns.api.views import (ArchiveCampaignViewSet,
                                               CampaignViewSet,
                                               HandleIncomingCallView,
                                               HandleIncomingSMSView,
                                               HandleKeyView,
                                               HandleRecordingView,
                                               MappedKeywordViewSet,
                                               RemoveFileFromCampaignViewSet,
                                               SendSampleCallView,
                                               TriggerCampaignViewSet,
                                               VoiceCallContentView)

app_name = 'campaigns'

router = SimpleRouter()
router.register(r'campaigns/keywords', MappedKeywordViewSet, base_name='mapped_keywords')
router.register(r'campaigns', CampaignViewSet, base_name='campaign')
router.register(r'campaigns/(?P<campaign_id>\d+)/(?P<campaign_type>\w+)', CampaignViewSet, base_name='all_campaign')

urlpatterns = [
    path('campaigns/<int:campaign_id>/trigger/', TriggerCampaignViewSet.as_view(), name='trigger_campaign'),
    path('campaigns/<int:pk>/archive_campaign/', ArchiveCampaignViewSet.as_view(), name="archive_campaign"),
    path('campaigns/<int:pk>/<str:channel_type>/remove_file_link/', RemoveFileFromCampaignViewSet.as_view(),
         name="remove_file_link"),
    path('campaigns/handle-recording/', HandleRecordingView.as_view(), name='handle_recording'),
    # Path called by twilio to handle incoming contents to numbers
    path('campaigns/incoming/call/', HandleIncomingCallView.as_view(), name='handle-incoming-call'),
    path('campaigns/incoming/key/', HandleKeyView.as_view(), name='handle-incoming-key'),
    path('campaigns/incoming/sms/', HandleIncomingSMSView.as_view(), name='handle-incoming-sms'),
    # Paths called by twilio to get voice campaign content
    path('campaigns/<int:pk>/send-sample-voice/', SendSampleCallView.as_view(), name='sample_voice_call'),
    path('campaigns/<int:pk>/voice-call-content/', VoiceCallContentView.as_view(), name='get-voice-call-content')
] + router.urls
