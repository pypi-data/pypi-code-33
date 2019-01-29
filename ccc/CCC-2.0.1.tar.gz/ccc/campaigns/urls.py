from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from ccc.campaigns.views import campaign, edit
from ccc.campaigns.views.api import CampaignAppViewSet, ISMSViewSet
from ccc.campaigns.views.campaign import (CampaignForm, Campaigns,
                                          CreateEmailCampaign,
                                          CreateMMSCampaign, CreateSMSCampaign,
                                          CreateVoiceCampaign, EndedCampaigns,
                                          FUForm, FUMakeCall,
                                          HandleIncomingSms, HandleKey,
                                          IncomingEmail, IncomingMms,
                                          IncomingSms, IVoiceCallDeleteView,
                                          IVoiceListView, MakeCall, MyContact,
                                          MyEmailCampaign, MyMMSCampaign,
                                          MySMSCampaign, MyTeam,
                                          MyVoiceCampaign, OutGoingEmail,
                                          OutgoingMms, OutgoingSms,
                                          SupportEmail, TemplatePreview,
                                          ViewCampaign, VoiceCall,
                                          VoiceMessage, archive_campaign,
                                          edit_email, edit_mms, edit_sms,
                                          edit_voice, ovoice_reports,
                                          sample_voice_call, test_email_sample,
                                          test_mms_sample, test_sms_sample,
                                          test_voice_sample)
from ccc.campaigns.views.edit import NotificationView

from .app_views import TemplateImagesView, UploadImageView

router = DefaultRouter()
router.register(r'app_campaign', CampaignAppViewSet)
router.register(r'isms-data', ISMSViewSet)


urlpatterns = [
    url(r'^create-voice-campaign/$', CreateVoiceCampaign, name='create_voice'),
    url(r'^vci-report/$', IVoiceListView.as_view(), name='voiceincoming_reports'),
    url(r'^incoming-voice/(?P<pk>\d+)/$', IVoiceCallDeleteView.as_view(), name='delete_incoming_voice'),
    url(r'^vco-report/$', ovoice_reports, name='voutgoing_reports'),
    url(r'^voice-campaigns/$', MyVoiceCampaign, name='voice_campaign'),
    url(r'^view-campaign/(?P<c_id>\d+)/$', ViewCampaign, name='view_campaign'),


    url(r'^voice-incoming/$', VoiceCall, name='handle_voice'),
    url(r'^handle-key/$', HandleKey, name='handle_key'),
    url(r'^handle-recording/$', VoiceMessage, name='handle_record'),
    url(r'^sms-reply/$', HandleIncomingSms, name='handle_sms'),

    url(r'^make-call/(?P<c_id>\d+)/$', MakeCall, name='send_voice'),
    url(r'^fu-make-call/(?P<fuc_id>\d+)/$', FUMakeCall, name='fu_send_voice'),


    url(r'^osms-report/$', OutgoingSms, name='osms'),
    url(r'^isms-report/$', IncomingSms, name='isms'),
    url(r'^create-sms-campaign/$', CreateSMSCampaign, name='create_voice'),
    url(r'^sms-campaigns/$', MySMSCampaign, name='create_voice'),


    url(r'^imms-report/$', IncomingMms, name='imms'),
    url(r'^omms-report/$', OutgoingMms, name='omms'),
    url(r'^create-mms-campaign/$', CreateMMSCampaign, name='create_mms'),
    url(r'^mms-campaigns/$', MyMMSCampaign, name='mms_campaigns'),

    url(r'^create-email-campaign/$', CreateEmailCampaign, name='create_email'),
    url(r'^oemail-report/$', OutGoingEmail, name='outgoing_email'),
    url(r'^iemail-report/$', IncomingEmail, name='incoming_email'),
    url(r'^email-campaigns/$', MyEmailCampaign, name='email-campaigns'),


    url(r'^all-contacts/$', MyContact, name='my_contact'),
    url(r'^all-teams/$', MyTeam, name='my_team'),

    # Ajax form load
    url(r'^cp-form/$', CampaignForm, name='cp_form'),
    url(r'^fu-form/$', FUForm, name='fu_form'),



    # campaign flow

    url(r'^create-campaign/$', campaign.CampaignCreateView.as_view(), name='create_campaign'),
    url(r'^fu-add/(?P<campaign_id>[0-9]+)/$', campaign.FollowUpCampaignCreateView.as_view(),
        name='add_followup_camapign_url'),

    url(r'^edit-fu/(?P<pk>\d+)/$', edit.FollowUpCampaignUpdateView.as_view(), name='fu_edit'),
    url(r'^delete-fu/(?P<pk>\d+)/$', edit.FollowUpCampaignDeleteView.as_view(), name='fu_delete'),
    url(r'^campaigns/$', Campaigns, name='campaigns'),
    url(r'^ended-campaigns/$', EndedCampaigns, name='ended_campaigns'),

    url(r'^edit-campaign/(?P<pk>\d+)/$', edit.UpdateCampaignView.as_view(), name='edit_campaign_new'),
    url(r'^un-link-attched-file/$', edit.RemoveFileFromCampaign.as_view(), name='unlink_campaign_file'),
    url(r'^edit-mms/(?P<c_id>\d+)/$', edit_mms, name='edit_mms'),
    url(r'^edit-voice/(?P<c_id>\d+)/$', edit_voice, name='edit_voice'),
    url(r'^edit-email/(?P<c_id>\d+)/$', edit_email, name='edit_email'),
    url(r'^edit-sms/(?P<c_id>\d+)/$', edit_sms, name='edit_sms'),
    url(r'^support/$', SupportEmail.as_view(), name='support_email'),
    url(r'^notify/$', NotificationView.as_view(), name='notify'),

    url(r'^test-voice-sample/$', test_voice_sample, name="test_voice_sample"),

    url(r'^test-sms-sample/$', test_sms_sample, name="test_sms_sample"),

    url(r'^test-email-sample/$', test_email_sample, name="test_email_sample"),

    url(r'^sample-voice-call/(?P<id>\d+)/$', sample_voice_call, name="sample_voice_call"),

    url(r'^archive-campaign/(?P<id>\d+)/$', archive_campaign, name="archive_campaign"),

    url(r'^test-mms-sample/$', test_mms_sample, name="test_mms_sample"),
    url(r'^template_images/(?P<template_id>\d+)/$', TemplateImagesView.as_view(), name='template_images_url'),
    url(r'^upload_images/(?P<campaign_id>\d+)/$', UploadImageView.as_view(), name='upload_template_images_url'),

    url(r'^template_preview/(?P<pk>\d+)/$', TemplatePreview.as_view(), name="template_preview"),

    url(r'^campaigns/(?P<pk>\d+)/embed/show/$', edit.ShowCampaignEmbedForm.as_view(), name='show_campaign_embed'),
    url(r'^campaigns/(?P<pk>\d+)/embed/$', edit.UpdateCampaignSignupView.as_view(), name='edit_campaign_embed'),


    # Phone Numbers   buy, release, verify red Numbers
    #url(r'^edit-sms/(?P<c_id>\d+)/$', 'ccc.campaigns.views.campaign.edit_sms', name='edit_sms'),




    #url(r'^/list/$', 'api.phones.views.list', name='api.phone.list'),
    url(r'^voice-incoming/$', 'django_twilio.views.say', {'text': 'Welcome to Cloud Custom Connections. Talk Soon. Goodbye!'  }),

    url(r'^campaigns/(?P<pk>\d+)/assign_contacts/$',
        edit.AssignContactsToCampaignView.as_view(), name='assign_contacts_to_campaign'),
    url(r'^campaigns/keywords/$', edit.CampaignKeywordListView.as_view(), name='list_keywords_to_campaign'),
    url(r'^campaigns/keywords/(?P<campaign_id>\d+)/form/$',
        edit.AssignKwywordsToCampaignView.as_view(), name='assign_keywords_to_campaign_form'),
    url(r'^campaigns/keywords/list/$', edit.CampaignKeywordAPIListView.as_view(), name='assign_keywords_to_campaign'),
    url(r'^campaign/trigger/contact/(?P<campaign_id>\d+)/$',
        edit.TriggerCampaignContact.as_view(), name='trigger_contact'),

]
urlpatterns = urlpatterns + router.urls
