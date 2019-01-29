from django.urls import path

from ccc.social_media.social import views

app_name = 'social'

urlpatterns = [
    path('', views.HomePage.as_view(), name='social-home'),
    path('analytics/', views.SocialAnalytics.as_view(), name='social-analytics')
]
