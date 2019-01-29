"""
Router / Resources for api: /api/marketing/surveys/
"""
from django.urls import path
from rest_framework import routers

from ccc.marketing.surveys.api import views

app_name = 'api_surveys'

router = routers.DefaultRouter()

router.register(r'questions', views.QuestionsViewSet, base_name='questions')
router.register(r'keywords', views.MappedKeywordViewSet, base_name='keywords')
router.register(r'responses', views.SurveyResponsesViewSet, base_name='responses')
router.register(r'', views.SurveyViewSet, base_name='surveys')
router.register(r'questions/answer-options', views.AnswerChoiceViewSet, base_name='answer-options')

urlpatterns = [
    path('questions/options/', views.ListQuestionsOptions.as_view(), name='survey-questions-options'),
    path('<int:survey_id>/trigger/', views.TriggerSurveyView.as_view(), name='survey-trigger'),
    # Twilio questions
    path('voice/get-greetings/', views.GetSurveyGreetingsView.as_view(), name='twilio-get-greetings'),
    path('voice/get-final-message/', views.GetSurveyFinalMessageView.as_view(), name='twilio-get-final-message'),
    path('voice/retrieve-question/', views.GetQuestionView.as_view(), name='twilio-get-question'),
    path('voice/submit-answer/', views.SubmitAnswerView.as_view(), name='twilio-submit-answer')
]

urlpatterns += router.urls
