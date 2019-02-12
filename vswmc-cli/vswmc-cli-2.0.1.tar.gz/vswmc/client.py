import json

import requests

from vswmc.core.exceptions import (MaximumSessionsReached, NotFound,
                                   Unauthorized, VswmcError)
from vswmc.sockjs import SockJSSession

VSWMC_URL = 'https://spaceweather.hpc.kuleuven.be'
SSO_URL = 'https://sso.ssa.esa.int/openam_953/UI/Login'


class VswmcClient(object):

    def __init__(self, address, credentials=None, user_agent=None):
        self.address = address
        self.auth_root = address + '/auth'
        self.api_root = address + '/api'
        self.eb_root = address + '/eventbus'

        self.session = requests.Session()
        if credentials:
            self.login(credentials)

    def login(self, credentials):
        self.session.cookies.clear()
        res = self.session.get(VSWMC_URL)
        data = {'IDToken1': credentials.username, 'IDToken2': credentials.password}
        for line in res.text.splitlines():
            if 'input type="hidden"' in line:
                parts = line.split('"')
                if len(parts) > 6:
                    data[parts[3]] = parts[5]

        res = self.session.post(SSO_URL, data=data)

        if 'Authentication Failed' in res.text:
            raise Unauthorized('Authentication Failed')
        if 'Maximum Sessions' in res.text:
            raise MaximumSessionsReached('Maximum sessions reached or session quota has exhausted')
        parts = res.text.split('"')

        res = self.session.post(VSWMC_URL, data={'LARES': parts[13]})

        # Only read when contacting a server instance without
        # apache rev.proxy.
        token = res.cookies['iPlanetDirectoryPro']
        self.session.headers.update({
            'Authorization': 'Bearer ' + token
        })

    def list_models(self):
        path = '{}/models'.format(self.api_root)
        return self._request('get', path=path).json()['models']

    def get_model(self, name):
        path = '{}/models/{}'.format(self.api_root, name)
        return self._request('get', path=path).json()

    def list_simulations(self):
        path = '{}/simulations'.format(self.api_root)
        return self._request('get', path=path).json()['simulations']

    def get_simulation(self, id_):
        path = '{}/simulations/{}'.format(self.api_root, id_)
        return self._request('get', path=path).json()

    def list_runs(self, simulation=None, status=None):
        path = '{}/runs'.format(self.api_root)
        params = {}
        if simulation:
            params['simulation'] = simulation
        if status:
            params['status'] = status
        response = self._request('get', path=path, params=params).json()
        return response['runs'] if 'runs' in response else []

    def start_run(self, simulation, parameters=None):
        path = '{}/runs'.format(self.api_root)
        converted_parameters = {k: json.dumps(parameters[k])
                                for k in parameters or {}}
        data = {
            'simulation': simulation,
            'variables': converted_parameters,
        }
        return self._request('post', path=path, json=data).json()

    def get_run(self, run):
        path = '{}/runs/{}'.format(self.api_root, run)
        return self._request('get', path=path).json()

    def download_logs(self, run):
        path = '{}/runs/{}/log'.format(self.api_root, run)
        return self._request('get', path=path, params={'raw': 'yes'}).content

    def download_result(self, run, path):
        path = '{}/runs/{}/results/{}'.format(self.api_root, run, path)
        return self._request('get', path=path).content

    def download_results(self, run):
        path = '{}/runs/{}/results'.format(self.api_root, run)
        return self._request('get', path=path).content

    def follow_logs(self, user, run, on_data):
        def filter_(msg, sess):
            if run == msg['headers']['runId']:
                on_data(msg['body'], sess)

        session = SockJSSession(self.address, on_data=filter_, session=self.session)
        session.send(json.dumps({
            'type': 'register',
            'address': 'http.user.{}.runlog'.format(user),
            'headers': {},
        }))
        return session

    def stop_run(self, run):
        path = '{}/runs/{}/terminate'.format(self.api_root, run)
        self._request('post', path=path)

    def delete_run(self, run):
        path = '{}/runs/{}/delete'.format(self.api_root, run)
        self._request('post', path=path)

    def upload_magnetogram(self, f, name):
        path = '{}/products/magnetograms'.format(self.api_root)
        files = {'file': (name, f, 'binary/octet-stream')}
        return self._request('post', path=path, files=files).json()

    def upload_cme_file(self, f, name):
        path = '{}/products/cme'.format(self.api_root)
        files = {'file': (name, f, 'binary/octet-stream')}
        return self._request('post', path=path, files=files).json()

    def _request(self, method, path, **kwargs):
        response = self.session.request(method, path, **kwargs)

        if response.headers['content-type'].startswith('text/html'):
            if 'OpenAM' in response.text:
                raise Unauthorized('Invalid session')

        if 200 <= response.status_code < 300:
            return response

        if response.status_code == 401:
            raise Unauthorized('401 Client Error: Unauthorized')
        elif response.status_code == 404:
            raise NotFound('404 Client Error: {}'.format(response.content))
        elif 400 <= response.status_code < 500:
            raise VswmcError('{} Client Error: {}'.format(
                response.status_code, response.content))
        raise VswmcError('{} Server Error: {}'.format(
            response.status_code, response.content))
