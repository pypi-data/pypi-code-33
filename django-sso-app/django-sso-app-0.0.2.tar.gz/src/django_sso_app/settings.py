import os

from django.conf import settings

def env_to_bool(name, default=False):
    var = os.environ.get(name, '')
    res = default
    if default == True:
        if var in ['false', 'False', 0]:
            res = False
    else:
        if var in ['true', 'True', 1]:
            res = True
    return res


SSO_COOKIE_DOMAIN = os.environ.get('COOKIE_DOMAIN', 'example.com')
SSO_USER_PROFILE_MODEL = getattr(settings, 'SSO_USER_PROFILE_MODEL', None)
SSO_DEACTIVATE_USER_ON_UNSUBSCRIPTION=env_to_bool('SSO_DEACTIVATE_USER_ON_UNSUBSCRIPTION')
SSO_SERVICE_SUBSCRIPTION_IS_MANDATORY=env_to_bool('SSO_SERVICE_SUBSCRIPTION_IS_MANDATORY')
SSO_STAFF_JWT = os.environ.get('SSO_STAFF_JWT', None)

SSO_URL = os.environ.get('SSO_URL', 'https://accounts.example.com')
SSO_BACKEND_URL = os.environ.get('SSO_BACKEND_URL', SSO_URL)
SSO_SERVICE_URL = os.environ.get('SSO_SERVICE_URL', 'https://protectedservice.example.com')

SSO_HEADER = "HTTP_X_CONSUMER_USERNAME"
SSO_ANONYMOUS_USERNAME = 'anonymous'


SSO_LOGIN_URL = SSO_URL + '/login/'
SSO_REGISTER_URL = SSO_URL + '/signup/'
SSO_PASSWORD_RESET_URL = SSO_URL + '/send-password-reset/'

SSO_API_URL = SSO_URL + '/api/v1'
SSO_BACKEND_API_URL = SSO_BACKEND_URL + '/api/v1'

SSO_LOGOUT_URL = SSO_API_URL + '/auth/logout/'

SSO_USERS_URL = SSO_API_URL + '/profiles/users/'
SSO_BACKEND_USERS_URL = SSO_BACKEND_API_URL + '/profiles/users/'

SSO_USER_URL = SSO_USERS_URL + '{user_id}/'
SSO_BACKEND_USER_URL = SSO_BACKEND_USERS_URL + '{user_id}/'

SSO_USERS_CHECK_URL = SSO_USERS_URL + 'check/'
SSO_BACKEND_USERS_CHECK_URL = SSO_BACKEND_USERS_URL + 'check/'

SSO_USER_SUBSCRIPTIONS_URL = SSO_API_URL + '/profiles/users/{user_id}/subscriptions/'
SSO_BACKEND_USER_SUBSCRIPTIONS_URL = SSO_BACKEND_API_URL + '/profiles/users/{user_id}/subscriptions/'

SSO_USER_SUBSCRIPTIONS_CREATE_URL = SSO_USER_SUBSCRIPTIONS_URL + 'create/{service_id}/'
SSO_BACKEND_USER_SUBSCRIPTIONS_CREATE_URL = SSO_BACKEND_USER_SUBSCRIPTIONS_URL + 'create/{service_id}/'

SSO_USER_SUBSCRIPTION_UNSUBSCRIBE_URL = SSO_USER_SUBSCRIPTIONS_URL + '{subscription_id}/unsubscribe/'
SSO_BACKEND_USER_SUBSCRIPTION_UNSUBSCRIBE_URL = SSO_BACKEND_USER_SUBSCRIPTIONS_URL + '{subscription_id}/unsubscribe/'

SSO_SERVICES_URL = SSO_API_URL + '/services/'
SSO_BACKEND_SERVICES_URL = SSO_BACKEND_API_URL + '/services/'

SSO_SERVICE_SUBSCRIBE_URL = SSO_SERVICES_URL + '{service_id}/subscribe/'
SSO_BACKEND_SERVICE_SUBSCRIBE_URL = SSO_BACKEND_SERVICES_URL + '{service_id}/subscribe/'

SSO_ADMIN_USER_URL = SSO_URL + '/admin/profiles/user/'

SSO_REQUIRED_PROFILE_FIELDS = ['sso_id', 'sso_rev',
                               "latitude", "longitude",
                               "first_name", "last_name",
                               "description",
                               "picture",
                               "birthdate",
                               "address", "country",
                               "language",
                               "is_unsubscribed"]
