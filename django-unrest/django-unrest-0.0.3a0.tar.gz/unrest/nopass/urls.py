from django.urls import path

from . import views

urlpatterns = [
    path("create/",views.create,name="nopass_create"),
    path("change_email/",views.change_email,name="nopass_change_email"),
    path("send/",views.send,name="nopass_send"),
    path("bad_token/",views.bad_token,name="nopass_bad_token"),
    path("<uidb64>/<token>/",views.complete_login,name="nopass_login"),
]