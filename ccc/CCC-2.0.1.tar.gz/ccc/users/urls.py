from django.conf.urls import url
from django.contrib.auth.views import password_change

from ccc.pages.views import home
from ccc.users.views import (ActivateAccountView, activate_success,
                             AnalyticsDataView, ChangePassword,
                             DashboardTemplateView,
                             login_authentication, NewPass, ProfileUpdate, PurchasePlan,
                             register, reg_success, ResendOtpView, ResetPass,
                             ResetPasswordView, ResetSuccess, SetTimeZoneView,
                             UpdateUnverifiedPhone,
                             VerifyOtpFormView, admincheck, api_login,
                             contacts, do_logout, email_campaign,
                             email_support, resume, settings, sms_campaign,
                             social_media, teams, voice_campaign, SubUsersView, DigitalBusinessCardView)

app_name = 'users'

urlpatterns = [
    url(r'^$', home, name='home'),

    url(r'^settimezone/', SetTimeZoneView.as_view(), name="set-timezone"),
    url(r'^dashboard/$', DashboardTemplateView.as_view(), name='users.dashboard'),
    url(r'^digital_buz_card/$', DigitalBusinessCardView.as_view(), name='users.digital_buz_card'),
    url(r'^sub/$', SubUsersView.as_view(), name='subusers'),
    url(r'^analytics_data/$', AnalyticsDataView.as_view(), name='analytics_data'),

    url(r'^register/$', register, name='register'),
    url(r'^login/$', login_authentication, name='user_login'),
    url(r'^api/login/$', api_login, name='api_login'),

    url(r'^settings/$', settings, name='users.settings'),
    url(r'^teams/$', teams, name='users.teams'),
    url(r'^contacts/$', contacts, name='users.contacts'),
    url(r'^social_media/$', social_media, name='users.social_media'),
    url(r'^resume/$', resume, name='users.resume'),

    url(r'^sms_campaign/$', sms_campaign, name='users.sms_campaign'),
    url(r'^voice_campaign/$', voice_campaign, name='users.voice_campaign'),
    url(r'^email_campaign/$', email_campaign, name='users.email_campaign'),

    url(r'^logout/$', do_logout, name='users.logout'),

    url(r'^purchase-plan/$', PurchasePlan, name='purchase-plan'),
    url(r'^confirm/$', ActivateAccountView.as_view(), name='users_confirm'),
    # url(r'^verified/$', ActivateSuccess, name='activate_success'),
    url(r'^register/success/$', reg_success, name='reg_success'),
    url(r'^reset-password/$', ResetPass, name='reset_pass'),
    url(r'^reset-password-email/$', ResetSuccess, name='reset_success'),
    url(r'^reset/(?P<activation_key>\w+)/$', NewPass, name='new_password'),
    url(r'^profile/$', ProfileUpdate.as_view(), name='user_profile'),
    url(r'^user_password_change/$', ChangePassword.as_view(), name='user_change_password'),
    # url(r'^add-user/$', AddSubUserView.as_view(), name='add_sub_account'),
    # url(r'^add-user/(?P<pk>\d+)/delete/$', DeleteSubAccountView.as_view(), name='delete_sub_account'),
    # url(r'^add-user/(?P<pk>\d+)/$', AddSubUserView.as_view(), name='edit_sub_account'),
    # url(r'^sub-user/$', SubUserView.as_view(), name='sub_account'),
    # url(r'^balances/$', admincheck, name='user_admin'),

    url(r'^password_change/', password_change, {
        'post_change_redirect': 'users.dashboard',
        'template_name': 'crm/users/profile.html'
    }, name='password_change'),

    url(r'^password-reset/$', ResetPasswordView.as_view(), name='password_reset'),

    url(r'^verify-otp/$', VerifyOtpFormView.as_view(), name='verify_otp'),
    url(r'^resend-otp/$', ResendOtpView.as_view(), name='resend_otp'),
    url(r'^update-phone/$', UpdateUnverifiedPhone.as_view(), name='update_phone'),
    url(r'^contact-support/$', email_support, name="email_support"),
]
