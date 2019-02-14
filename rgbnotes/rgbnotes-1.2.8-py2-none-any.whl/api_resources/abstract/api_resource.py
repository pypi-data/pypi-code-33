from __future__ import absolute_import, division, print_function
import json
import requests
import rgbnotes


class APIError(Exception):
    '''RGB Notes API Error base class'''


def init_http_logger(level=None):
    '''initialize logging, otherwise you will not see anything from requests'''
    import logging
    import httplib

    logging.basicConfig()
    if level == 'debug':
        httplib.HTTPConnection.debuglevel = 1
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True



class APIResource(object):
    def __init__(self,
                 api_url=None,
                 client_key=None,
                 client_id=None,
                 log=None,
                 timeout=None):

        self._timeout = timeout or rgbnotes.timeout
        self._log = log or rgbnotes.log
        self._api_url = api_url or rgbnotes.api_url
        self._client_id = client_id or rgbnotes.client_id
        self._client_key = client_key or rgbnotes.client_key

        if self._log:
            init_http_logger(self._log)
            


    def parse_json(self, r):
        if isinstance(r, requests.Response):
            if 'application/json' in r.headers['content-type']:
                try:
                    d = r.json()
                except json.scanner.JSONDecodeError:
                    try:
                        # try and clean up junk
                        d = json.loads(r.content.split('\n')[0])
                    except json.scanner.JSONDecodeError as e:
                        raise APIError('There was an issue decoding the server response!')
                    else:
                        if 'error' in d:
                            raise APIError(d['error'])
                        else:
                            return d
                else:
                    return d


    def get_request(self, endpoint=None, **params):
        '''GET Request'''
        if not rgbnotes.client_token:
            raise APIError('Request a token first')

        try:
            r = requests.get(self._api_url + endpoint,
                             headers={'Rgb-Auth-Token':rgbnotes.client_token},
                             params=params,
                             timeout=self._timeout)
        except requests.RequestException as e:
            raise APIError(str(e))
        else:
            if r.status_code == requests.codes.ok:
                return r
            else:
                raise APIError('Request returned an error: {}'.format(r.status_code))


    def post_request(self, data, files=None, endpoint=None):
        '''POST Request'''
        if not rgbnotes.client_token:
            raise APIError('Request a token first')

        try:
            r = requests.post(self._api_url + endpoint,
                              headers={'Rgb-Auth-Token':rgbnotes.client_token},
                              data=data,
                              files=files,
                              timeout=self._timeout)
        except requests.RequestException as e:
            raise APIError(str(e))
        else:
            if r.status_code == requests.codes.ok:
                return r
            else:
                raise APIError('Request returned an error {}: {}'.format(r.status_code, r.text))

    
    def get_token(self, project=False, **data):
        if not rgbnotes.client_key or not rgbnotes.client_id:
            raise APIError("Missing 'api_id' or 'api_key'")

        if project:
            # If user_id is not passed, act as the current user by default
            if 'user_id' not in data:
                data['user_id'] = data['client_id']
            endpoint = '/token/project_member'
        else:
            endpoint = '/token/client'

        try:
            data.update({'client_id':rgbnotes.client_id,
                         'client_key':rgbnotes.client_key})

            r = requests.post(self._api_url + endpoint,
                              data=data,
                              timeout=self._timeout)

        except requests.RequestException as e:
            raise APIError(str(e))
        else:
            if r.status_code == requests.codes.ok:
                data = self.parse_json(r)
                if 'token' in data:
                    rgbnotes.client_token = data['token']
                else:
                    raise APIError("Token request didn't return a token dictionary")
            else:
                raise APIError(['Error: {}'.format(r.status_code),
                                     r.text])


    @classmethod
    def class_url(cls):
        if cls == APIResource:
            raise NotImplementedError(
                'APIResource is an abstract class.  You should perform '
                'actions on its subclasses (e.g. Project, Note)')
        # Namespaces are separated in object names with periods (.) and in URLs
        # with forward slashes (/), so replace the former with the latter.
        base = cls.OBJECT_NAME.replace('.', '/')
        return '/%s' % (base,)
