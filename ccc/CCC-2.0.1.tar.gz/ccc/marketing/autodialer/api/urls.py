from django.urls import path
from rest_framework.routers import DefaultRouter

from ccc.marketing.autodialer.api import views

app_name = 'autodialer_api'

router = DefaultRouter()
router.register('dial/master', views.AssociateMasterListViewSet, base_name='dial-master-list')
router.register('dial', views.AutoDialListViewSet, base_name='dial')
router.register('personalized-messages', views.PersonalizedMessagesView, base_name='personalized-messages')

urlpatterns = [
    path('<int:pk>/send-conversation/', views.EmailPhoneConversationView.as_view(), name='email-phone-conversation'),
    # This is called by twilio to handle phone call
    path('dial/get_token/', views.RetrieveCapabilityToken.as_view(), name='retrieve-call-token'),
    path('dial/handle-phone-call/', views.HandlePhoneCallView.as_view(), name='handle-phone-call'),
    path('dial/handle-phone-call-record/<int:outgoing_voice_id>/callback/',
         views.HandlePhoneCallRecordCallbackView.as_view(),
         name='handle-recording-callback'),
    path('dial/<str:twilio_number_id>/<str:outgoing_voice_id>/callback/', views.HandlePhoneCallCallBackView.as_view(),
         name='handle-phone-call-call-back'),
    # Still called by twilio, but to get content of personalized phone call
    path('personalized-messages/<int:pk>/get-content/', views.TwilioGetPersonalizedMessage.as_view(),
         name='twilio-get-content')
]

urlpatterns += router.urls
