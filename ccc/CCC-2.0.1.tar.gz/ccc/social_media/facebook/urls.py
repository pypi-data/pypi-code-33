from django.urls import path

from ccc.social_media.facebook import views

app_name = 'facebook'

urlpatterns = [
    # path('redirect_handler/', views.GetAccessToken.as_view(), name='smm_redirect_handler'),
    # path('get_initial_code/', views.GetCode.as_view(), name='get_initial_code'),
    path('get_access_code/', views.FacebookAuth.as_view(), name='smm_get_access_code'),
]
