import requests
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.models import Site
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View

from ccc.social_media.facebook.constants import REQUIRED_PERMISSIONS
from ccc.social_media.facebook.exceptions import SMMFacebookAuthError
from ccc.social_media.facebook.models import (AccessToken, AuthState,
                                              FacebookProfile)
from ccc.social_media.facebook.utils import (add_query_param_to_url,
                                             dict_to_url_args,
                                             reverse_or_fail_silently)


class FacebookAuthUtil(LoginRequiredMixin, View):
    debug_token_url = 'https://graph.facebook.com/debug_token?input_token={}&access_token={}|{}'
    profile_url = 'https://graph.facebook.com/me?access_token={}'
    # Profile accounts is to get the users group and pages
    profile_accounts_url = 'https://graph.facebook.com/me/accounts?access_token={}'

    def debug_access_token(self, access_token):
        # Return details about the access token
        debug_url = self.debug_token_url.format(access_token,
                                                settings.SMM_FACEBOOK_CLIENT_ID,
                                                settings.SMM_FACEBOOK_CLIENT_SECRET)
        response = requests.get(debug_url)

        return response.json()

    def save_or_update_access_code(self, access_code_data):
        #  Save the access token received
        token = access_code_data['access_token']
        token_type = access_code_data['token_type']
        expires_in = access_code_data.get('expires_in', 5184000)  # 60 days
        permissions = access_code_data['data']['scopes']
        facebook_uid = access_code_data['data']['user_id']
        # If the user has already connected his account and still does some re-auth, probably wants to add new
        # permissions, then do update
        old_stored_accesstoken = AccessToken.objects.filter(user=self.request.user, facebook_uid=facebook_uid)
        if old_stored_accesstoken.exists():
            acc = old_stored_accesstoken.first()
            acc.token = token
            acc.token_type = token_type
            acc.permissions = permissions
            acc.facebook_uid = facebook_uid
            acc.set_expiry(expires_in)
            acc.save()
        else:
            acc = AccessToken(token=token, token_type=token_type, user=self.request.user, permissions=permissions,
                              facebook_uid=facebook_uid)
            acc.set_expiry(int(expires_in))
            acc.save()
        return acc

    def save_or_update_stored_profile(self, access_token_object):
        self.profile_url = add_query_param_to_url(self.profile_url, {'fields': 'picture,first_name,last_name,'
                                                                               'middle_name,about,link'})
        response = requests.get(self.profile_url.format(access_token_object.token))
        if response.json().get('error', None) is None:
            picture = response.json().get('picture', {}).get('data', {}).get('url', '')
            first_name = response.json().get('first_name', '')
            last_name = response.json().get('last_name', '')
            middle_name = response.json().get('middle_name', '')
            link = response.json().get('link', 'https://facebook.com')

            stored_profile = FacebookProfile.objects.filter(access_token_id=access_token_object.id)
            if stored_profile.exists():
                stored_profile = stored_profile.first()
            else:
                stored_profile = FacebookProfile()
            stored_profile.picture = picture
            stored_profile.first_name = first_name
            stored_profile.last_name = last_name
            stored_profile.middle_name = middle_name
            stored_profile.link = link
            stored_profile.access_token = access_token_object
            stored_profile.save()
        else:
            # TODO: Handle get profile request error
            pass


class FacebookAuth(FacebookAuthUtil):
    auth_url = 'https://www.facebook.com/v' + settings.SMM_FACEBOOK_API_VERSION + '/dialog/oauth?'
    token_api_url = 'https://graph.facebook.com/v' + settings.SMM_FACEBOOK_API_VERSION + '/oauth/access_token?'

    @property
    def protocol(self):
        protocol = 'https'
        if 'localhost' in self.domain:
            protocol = 'http'
        return protocol

    @property
    def domain(self):
        return Site.objects.get_current(request=self.request).domain

    def get_auth_code(self):
        redirect_url = self.protocol + '://{}{}'.format(self.domain, reverse('srm:facebook:smm_get_access_code'))

        # Create auth_state so we can verify that the user making the request for the accesstoken is the same user
        # that made this current request
        auth_state = AuthState(user=self.request.user)
        auth_state.save()

        self.auth_url += dict_to_url_args({
            'client_id': settings.SMM_FACEBOOK_CLIENT_ID,
            'state': auth_state.__str__(),
            'redirect_uri': redirect_url,
            'scope': REQUIRED_PERMISSIONS
        })

        return redirect(self.auth_url)

    def get_access_code_local(self):
        return AccessToken.objects.filter(user=self.request.user, type=1)

    def verify_access_code_request(self):
        # Verify the user creating this request
        state_code = self.request.GET.get('state', None)
        if state_code is None or not AuthState.objects.filter(user=self.request.user, code=state_code).exists():
            raise AssertionError('Could not verify the auth code entered for retrieving access code!')

    def get_access_code_remote(self):
        redirect_url = self.protocol + '://{}{}'.format(self.domain, reverse('srm:facebook:smm_get_access_code'))
        auth_code = self.request.GET.get('code', None)
        if auth_code is None:
            raise ValueError('No auth code supplied for getting access code!')

        self.token_api_url += dict_to_url_args({
            'client_id': settings.SMM_FACEBOOK_CLIENT_ID,
            'client_secret': settings.SMM_FACEBOOK_CLIENT_SECRET,
            'redirect_uri': redirect_url,
            'code': auth_code
        })

        # Send the request to facebook
        response = requests.get(self.token_api_url)

        if response.json().get('access_token', None) is None:
            # Means an error occurred, We'll handle the error here
            return response.json()
        else:
            token = response.json()['access_token']
            # Debug access token to get other user_id, permissions that were granted
            access_token_details = self.debug_access_token(token)
            # Merge the token request response with the token debug response, both contain information for our to be
            # saved token
            new_access_code_token = {**response.json(), **access_token_details}
            access_code_object = self.save_or_update_access_code(new_access_code_token)
            # Save the user's profile to the system or update it if it already exists
            self.save_or_update_stored_profile(access_code_object)
            return access_code_object.token

    def get_access_code(self):
        # Check if the user wants to force re-auth maybe to change some permissions,
        # In this case the URL has to carry query-param 'forceReauth=true'
        self.verify_access_code_request()
        force_reauth = self.request.GET.get('forceReauth', None)

        local_access_code = self.get_access_code_local()
        if local_access_code.exists() and local_access_code.first().is_valid and force_reauth is None:
            return local_access_code.first().token
        else:
            return self.get_access_code_remote()

    def get(self, request):
        auth_code = request.GET.get('code', None)
        if auth_code is not None:  # This means that it's the initial request being sent to facebook
            access_code = self.get_access_code()
            if isinstance(access_code, dict):  # means it's an error
                raise SMMFacebookAuthError(str(access_code['error']['message']))
            else:
                return redirect(reverse_or_fail_silently(settings.SMM_FACEBOOK_LOGIN_REDIRECT))
        else:
            return self.get_auth_code()  # Redirect the user to facebook to get auth
