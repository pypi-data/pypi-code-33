"""feedback_1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from stem_feedback import views

urlpatterns = [
    url(r'^feedback/event/', views.FeedbackEmailView.as_view(), name='feedback'),
    url(r'^feedback/payment_notification/', views.PaymentNotificationView.as_view(), name='payment_notification'),
    url(r'^feedback/money_back/(?P<pk>\d+)/$', views.MoneyBackView.as_view(), name='money_back'),
    url(r'^feedback/callback/', views.CallBackView.as_view(), name='callback'),
]
