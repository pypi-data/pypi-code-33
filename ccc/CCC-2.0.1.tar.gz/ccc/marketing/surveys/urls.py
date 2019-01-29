from django.urls import path, re_path

from ccc.marketing.surveys import views
from ccc.survey.views import TwilioCallHandler, TwilioSMSHandler

app_name = 'surveys'

urlpatterns = [

    path('', views.SurveysListView.as_view(), name='list_survey_actives'),
    path('keywords/', views.SurveyKeywordsView.as_view(), name='list_survey_keywords'),
    path('responses/', views.SurveyResponsesView.as_view(), name='responses'),
    path('responses/download/<str:id>/', views.SurveyResponsesDownloadView.as_view(), name='responses-download'),
    path('response/contact/<int:pk>/', views.SurveyResponseContactView.as_view(), name='response'),
    path('clicks/', views.SurveyURLClicks.as_view(), name='url-clicks'),
    re_path(r'^all/$', views.SurveysAllView.as_view(), name='list_survey_all'),
    re_path(r'^(?P<pk>\d+)/$', views.SurveyDetailView.as_view(), name='survey_detail'),

    # twilio surveys webhooks
    re_path(r'^sms-handler/$', TwilioSMSHandler.as_view(), name='sms_handler'),
    re_path(r'^voice-handler/$', TwilioCallHandler.as_view(), name='voice_handler'),
]
