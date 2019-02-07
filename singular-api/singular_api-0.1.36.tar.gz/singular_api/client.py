import inspect
import urllib
import simplejson
import time

import requests
try:
    from exceptions import SingularException
    from singular_api.settings import (
            ENDPOINTS,
            SINGULAR_URL,
            )
    from singular_api.models import Activity
except ImportError:
    from .exceptions import SingularException
    from .settings import (
            ENDPOINTS,
            SINGULAR_URL,
            )
    from .models import Activity


# TODO add arguments descriptions in function doctrings

def myself():
    """Returns name of function that is one step above in stack"""
    return inspect.stack()[1][3]


class Client:
    """Singular API client class. Provides methods to call Singular API from python scripts."""
    # TODO do we need appname here?
    def __init__(self, singular_token=None, singular_url=SINGULAR_URL,
                 connect_timeout=60, read_timeout=60, client_id=None,
                 client_secret=None):
        """Basic Client init method

Keyword arguments:
singular_token (optional) -- OAuth2 Singular API token
singular_url (optional) -- defines Singular API URL. Uses default if not provided. Example - 'http://localhost:8000'.
connect_timeout (optional) -- connect timeout (see Requests module)
read_timeout (optional) -- read timeout (see Requests module)
client_id (optional) -- used to refresh token(see OpenID)
client_secret (optional) -- used to refresh token(see OpenID"""
        self._singular_url = singular_url
        self._singular_token = singular_token
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout
        self._client_id = client_id
        self._client_secret = client_secret
        self.token_managed = False

    def set_singular_token(self, token):
        """Sets Singular Token, which will be used to make every subsequent calls to Singular API"""
        self._singular_token = token

    def ping(self):
        """Tests connection to Singular API"""
        response, status_code = self._call_singular(
            ENDPOINTS[myself()]['url'],
            ENDPOINTS[myself()]['method'])
        connection_status = response.get('ping') == 'pong'
        return connection_status, status_code

    def schedule(self, start_time=None):
        endpoint = 'api/schedule/'
        if start_time is None:
            method = 'GET'
            data = None
        else:
            method = 'POST'
            data = {'start_time': start_time}

        activities, _ = self._call_singular(endpoint, method, json_body=data)
        ret_activities = []
        for activity in activities:
            ret_activities.append(Activity(id=activity['id'], client=self,
                                  dictionary=activity))
        return ret_activities


    def user_data(self):
        endpoint = 'api/user_data/'
        return self._call_singular(endpoint, 'GET')

    def get_authorization_url(self, client_id, redirect_uri, state, scopes=[]):
        """Generates authorization URL with for registering new app

Keyword arguments:
client_id -- App client id
redirect_uri -- URL to user registering endpoint
state -- oauth state interpreted by app"""
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'scope': ' '.join(scopes),
            'response_type': 'code',
            'state': state
        }
        params_str = urllib.parse.urlencode(params)
        url = '{}openid/authorize?{}'.format(self._singular_url, params_str)
        return url

    def register_user(self, client_id, client_secret, code, redirect_uri):
        """Registers app for user
Keyword arguments:
client_id -- App client id
client_secret -- App secret token
code -- code returned earlier from singular-api
redirect_uri -- oauth redirect uri"""
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        response, status = self._call_singular('openid/token/',
                                               'POST', encoded_body=data)
        token = response.get('access_token')
        refresh_token = response.get('refresh_token')
        return token, refresh_token

    def create_mapping(self, cid):
        """Creates user mapping in singular, that is required for notifies
Keyword arguments:
cid -- App client id"""
        data = {
            'cid': cid,
        }
        self._call_singular('connector_manager/api/add_listener/', 'POST', json_body=data)

    def refresh_token(self, refresh_token, client_id, client_secret):
        """
curl -X POST \
-H "Cache-Control: no-cache" \
-H "Content-Type: application/x-www-form-urlencoded" \
"http://api-taski.websensa.com/openid/token/" \
-d "client_id=706824" \
-d "client_secret=c082a814884af08cb8be03baca546809ce3119456b635188c443723d" \
-d "grant_type=refresh_token" \
-d "refresh_token=58dae7dc2c9d41748aebb9520256a5d5"
        """
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        response, status = self._call_singular('openid/token/',
                                               'POST', encoded_body=data)
        token = response.get('access_token')
        refresh_token = response.get('refresh_token')
        expires_in = response.get('expires_in')

        return token, refresh_token, expires_in

    def _call_singular(self, url, method, params=None, json_body=None,
                       encoded_body=None, request_headers=None):
        """Makes actual Singular API requests

Keyword arguments:
endpoind -- Singular API endpoint dictionary, containing URL and HTTP request method. See settings.py.
params (optional) -- URL parameters dictionary
json_body (optional) -- json which should be sent in HTTP POST request body
encoded_body (optional) -- URL encoded data which should be sent in HTTP POST request body. Used only when json_body is None
request_headers (optional) -- HTTP request headers"""
        url = self._singular_url + url

        if self._singular_token is not None:
            headers = {
                'Authorization': 'Bearer {}'.format(self._singular_token)
            }
        else:
            headers = {}

        if request_headers is not None:
            headers.update(request_headers)
        timeouts = (self.connect_timeout, self.read_timeout)

        def try_request():
            if json_body is not None:
                headers['Content-Type'] = 'application/json'
                response = requests.request(method, url, json=json_body,
                                            headers=headers, params=params,
                                            timeout=timeouts)
            elif encoded_body is not None:
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
                response = requests.request(method, url, data=encoded_body,
                                            headers=headers, params=params,
                                            timeout=timeouts)
            else:
                response = requests.request(method, url, headers=headers,
                                            params=params, timeout=timeouts)
            return response

        try:
            response = try_request()
            if response.status_code in [200, 201, 202, 204]:
                try:
                    return response.json(), response.status_code
                except simplejson.errors.JSONDecodeError:
                    return {}, response.status_code
            else:
                if self.token_managed is True:
                    # TODO(kuba): fix
                    raise NotImplementedError
                else:
                    raise SingularException.from_response(response.status_code,
                                                          response.text)

        except requests.exceptions.ConnectTimeout:
            raise SingularException.from_response(504, 'Connection timeout')
        except requests.exceptions.ReadTimeout:
            raise SingularException.from_response(504, 'Read timeout')
        except requests.exceptions.ConnectionError:
            raise SingularException.from_response(502, 'Connection error')
