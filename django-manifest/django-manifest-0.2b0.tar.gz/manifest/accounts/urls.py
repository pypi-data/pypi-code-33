# -*- coding: utf-8 -*-
from django.urls import path, re_path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from manifest.accounts import views as accounts_views
from manifest.accounts import defaults


urlpatterns = [
    # Signup, login and logout
    re_path(r'^login/$', 
        accounts_views.Login.as_view(),
        name='accounts_login'),

    re_path(r'^logout/$', 
        auth_views.LogoutView.as_view(
            template_name='accounts/logout.html'
            ),
        name='accounts_logout'), 

    re_path(r'^register/$', 
        accounts_views.Register.as_view(),
        name='accounts_register'),

    re_path(r'^register/complete/(?P<username>\w+)/$', 
        accounts_views.UserView.as_view(
            template_name='accounts/register_complete.html',
            extra_context={
                'accounts_activation_required': 
                    defaults.ACCOUNTS_ACTIVATION_REQUIRED,
                'accounts_activation_days': 
                    defaults.ACCOUNTS_ACTIVATION_DAYS}),
        name='accounts_register_complete'),

    # Activate
    re_path(r'^activate/(?P<username>\w+)/(?P<activation_key>\w+)/$', 
        accounts_views.Activate.as_view(), 
        name='accounts_activate'),

    # Disabled
    re_path(r'^disabled/(?P<username>\w+)/$', 
        accounts_views.UserView.as_view(
            template_name='accounts/disabled.html'), 
        name='accounts_disabled'),

    # Settings
    re_path(r'^settings/$', 
        accounts_views.UserTemplateView.as_view(),
        name='accounts_settings'),

    # Edit profile
    re_path(r'^settings/update/$', 
        accounts_views.ProfileUpdate.as_view(),    
        name='accounts_update'),

    # Reset password using django.contrib.auth.views
    re_path(r'^password/reset/$', 
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset_form.html',
            email_template_name='accounts/emails/password_reset_message.txt'
            ),
        name='accounts_password_reset'),

    re_path(r'^password/reset/done/$', 
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html'
            ),
        name='password_reset_done'),

    re_path(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', 
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html'
            ),
        name='password_reset_confirm'),

    re_path(r'^password/reset/complete/$', 
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'
            ),
        name='password_reset_complete'),

    # Change email and confirm it
    re_path(r'^email/change/$', 
        accounts_views.EmailChange.as_view(),
        name='accounts_email_change'),

    re_path(r'^email/change/done/(?P<username>\w+)/$', 
        accounts_views.UserView.as_view(
            template_name='accounts/email_change_done.html'),
        name='accounts_email_change_done'),
    
    re_path(r'^email/change/confirm/(?P<username>\w+)/(?P<confirmation_key>\w+)/$', 
        accounts_views.EmailConfirm.as_view(),
        name='accounts_email_confirm'),

    re_path(r'^email/change/complete/(?P<username>\w+)/$', 
        accounts_views.UserView.as_view(
            template_name='accounts/email_change_complete.html'),
        name='accounts_email_change_complete'),

    # Change password
    re_path(r'^password/change/$', 
        accounts_views.PasswordChange.as_view(),
        name='accounts_password_change'),

    re_path(r'^password/change/done/(?P<username>\w+)/$', 
        accounts_views.UserView.as_view(
            template_name='accounts/password_change_complete.html'),
        name='accounts_password_change_done'),

    # View profiles
    re_path(r'^profiles/(?P<username>(?!logout|register|login|password|account|profile)\w+)/$', 
        accounts_views.ProfileDetail.as_view(),
        name='accounts_profile_detail'),

    re_path(r'^profiles/$', 
        accounts_views.ProfileList.as_view(),
        name='accounts_profile_list'),
]