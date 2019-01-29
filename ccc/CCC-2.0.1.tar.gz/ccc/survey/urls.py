from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from ccc.survey.views import (AssignKwywordsToSurveyView, SurveyAppViewSet,
                              SurveyKeywordAPIListView, SurveyResponseDownload,
                              SurveysAll)

from .views import (Dashboard, LinkClicks, QuestionCreate, QuestionDelete,
                    QuestionUpdate, SurveyArchive, SurveyCreate, SurveyDetail,
                    SurveyResponse, Surveys, SurveyUnArchive, SurveyUpdate,
                    TwilioCallHandler, TwilioSMSHandler)

router = DefaultRouter()
router.register(r'app_survey', SurveyAppViewSet)

urlpatterns = [
    # Surveys

    url(r'^$', Surveys.as_view(), name='survey_list'),


    url(r'^all/$', SurveysAll.as_view(), name='survey_list_all'),


    url(r'^add/$', SurveyCreate.as_view(), name='survey_create'),

    url(r'^(?P<pk>\d+)/$', SurveyDetail.as_view(), name='survey_detail'),

    url(r'^edit/(?P<pk>\d+)/$', SurveyUpdate.as_view(), name='survey_update'),

    url(r'^archive/(?P<pk>\d+)/$', SurveyArchive.as_view(), name='survey_archive'),
    url(r'^unarchive/(?P<pk>\d+)/$', SurveyUnArchive.as_view(), name='survey_unarchive'),

    url(r'^response/(?P<pk>\d+)/$', SurveyResponse.as_view(), name='survey_response'),

    # Questions
    url(r'^(?P<survey_pk>\d+)/add-question/$', QuestionCreate.as_view(), name='question_create'),
    url(r'^(?P<survey_pk>\d+)/add-question/(?P<type>[\w\-]+)/(?P<pk>\d+)$', QuestionCreate.as_view(), name='question_create'),
    url(r'^edit-question/(?P<pk>\d+)$', QuestionUpdate.as_view(), name='question_update'),
    url(r'^delete-question/(?P<pk>\d+)$', QuestionDelete.as_view(), name='question_delete'),

    # Handlers - Webhooks twillio
    url(r'^sms-handler/$', TwilioSMSHandler.as_view(), name='survey_sms_handler'),
    url(r'^voice-handler/$', TwilioCallHandler.as_view(), name='survey_voice_handler'),

    # Dashboard.
    url(r'^dashboard/clicks/$', LinkClicks.as_view(), name='survey_clicks_dashboard'),
    url(r'^dashboard/$', Dashboard.as_view(), name='survey_dashboard'),

    url(r'^download/(?P<id>\w+)/$', SurveyResponseDownload.as_view(), name='survey_download'),
    url(r'^keywords/list/$', SurveyKeywordAPIListView.as_view(), name='assign_keywords_to_survey_list'),
    url(r'^keywords/(?P<survey_id>\d+)/form/$',
        AssignKwywordsToSurveyView.as_view(), name='assign_keywords_to_survey_form'),
]
urlpatterns = urlpatterns + router.urls
