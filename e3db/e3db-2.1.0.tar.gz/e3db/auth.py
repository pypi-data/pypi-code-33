import requests
from requests.auth import AuthBase
from requests.auth import HTTPBasicAuth
import datetime
from .exceptions import APIError


class E3DBAuth(AuthBase):
    DEFAULT_API_URL = "https://api.e3db.com"

    def __init__(self, api_key_id, api_secret, api_url=DEFAULT_API_URL):
        self.api_key_id = api_key_id
        self.api_secret = api_secret
        self.api_url = api_url
        self.token = None
        # guaranteed to be less than current time (Unix Epoch)
        self.expires_at = datetime.datetime(1970, 1, 1)

    def __call__(self, r):
        # if we need to renew the token for the request, we do that real quick.
        # otherwise, we add the bearer token header from our existing token
        if (self.token is None) or (datetime.datetime.utcnow() > self.expires_at):
            grant = {'grant_type': 'client_credentials'}
            refresh_request = requests.post(url="{0}/v1/auth/token".format(self.api_url), auth=HTTPBasicAuth(self.api_key_id, self.api_secret), data=grant)
            # check if status code was 200 OK
            if refresh_request.status_code == 200:
                refresh_json = refresh_request.json()
                self.token = refresh_json['access_token']
                expire_time = refresh_json['expires_at']
                # now save that as a datetime object so we can do later comparison
                self.expires_at = datetime.datetime.strptime(expire_time, "%Y-%m-%dT%H:%M:%S.%fZ")
            # we need to make sure if an error happened we raise the proper exception
            elif refresh_request.status_code == 401:
                raise APIError("Unauthorized. Check your API key pair to ensure it is valid.")
            else:
                raise APIError("Authentication failure: HTTP Status: {0}".format(refresh_request.status_code))

        # Add the bearer token to the request we want to send
        r.headers['Authorization'] = 'Bearer ' + str(self.token)
        return r
