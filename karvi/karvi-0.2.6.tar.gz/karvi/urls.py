from django.urls import path, include

from .views import UserCreationView

urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/signup", UserCreationView.as_view(), name="signup"),
]
