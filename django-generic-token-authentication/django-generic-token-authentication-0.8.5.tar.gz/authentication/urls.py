from django.urls import path
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'authentication'

urlpatterns = [path('password', views.PasswordRequirementsView.as_view()), ]

router = routers.SimpleRouter()
router.register(r'users', views.UserViewSet, base_name='users')
router.register(r'changepassword', views.UpdatePasswordViewSet, base_name='changepassword')
router.register(r'profileimage', views.ProfileImageViewSet, base_name='profileimage')
router.register(r'register', views.RegisterViewSet, base_name='register')
router.register(r'token', views.TokenViewSet, base_name='token')
router.register(r'logout', views.LogoutViewSet, base_name='logout')
router.register(r'logoutall', views.LogoutAllViewSet, base_name='logoutall')
router.register(r'refresh', views.RefreshViewSet, base_name='logoutall')
router.register(r'resetpassword', views.ResetPasswordViewSet, base_name='resetpassword')
router.register(r'validatereset', views.ValidateResetPasswordViewSet, base_name='validatereset')
router.register(r'confirmreset', views.ConfirmResetPasswordViewSet, base_name='confirmreset')
router.register(r'confirmemail', views.ConfirmEmailViewSet, base_name='confirmemail')
urlpatterns += router.urls

urlpatterns = format_suffix_patterns(
    urlpatterns, suffix_required=True, allowed=['json'])
