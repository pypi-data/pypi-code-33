#!/usr/bin/env python

__author__ = "Anand Tiwari (http://twitter.com/anandtiwarics)"
__contributors__ = ["Anand Tiwari"]
__status__ = "Production"
__license__ = "MIT"

import requests
import json


def all_headers(auth_token):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'JWT' + ' ' + auth_token,
    }
    return headers


class ArcheryAPI(object):
    def __init__(self, host):

        self.host = host

    def networkscan_result(self, auth, scan_id):
        """

        :param auth:
            Authentication Token variable
        :param scan_id:
            Target Scan ID
        :return:
        """

        # Network Results API end point
        url = '/api/networkscanresult/'

        # Headers included
        headers = all_headers(auth_token=auth)

        # Body data in json format
        data = {
            "scan_id": scan_id
        }
        data = json.dumps(data)

        return self._request('POST', url, params='format=json', headers=headers, data=data)

    def create_newtworkscan(self, auth, scan_ip, project_id):
        """

        :param auth:
            Authentication Token variable
        :param scan_ip:
            Target IP address
        :param project_id:
            Project ID
        :return:
        """

        # API end point
        url = '/api/networkscan/'

        # Headers included
        headers = all_headers(auth_token=auth)

        # Body data in json format
        data = {
            "scan_ip": scan_ip,
            "project_id": project_id,

        }
        data = json.dumps(data)

        return self._request('POST', url, params='format=json', headers=headers, data=data)

    def network_scan(self, auth):
        """

        :param auth:
        :return:
        """
        # Headers included
        headers = all_headers(auth_token=auth)

        # API End Point
        url = '/api/networkscan/'

        return self._request('GET', url, params='format=json', headers=headers)

    def webscan_result(self, auth, scan_id):
        """

        :param auth:
        :param scan_id:
        :return:
        """

        url = '/api/webscanresult/'

        # Headers included
        headers = all_headers(auth_token=auth)

        # Body data in json format
        data = {
            "scan_id": scan_id
        }
        data = json.dumps(data)

        return self._request('POST', url, params='format=json', headers=headers, data=data)

    def create_webscan(self, auth, scan_url, project_id, scanner):
        """
        Launch Web scan
        :param auth: Provide auth token.
        :param scan_url: Provide target URL
        :param project_id: Provide project id
        :param scanner: Select scanner. OWASP ZAP Scanner - zap_scan
                                        Burp Scanner - burp_scan
        :return:

        """
        url = '/api/webscan/'

        # Headers included
        headers = all_headers(auth_token=auth)

        # Body data in json format
        data = {
            "scan_url": scan_url,
            "project_id": project_id,
            "scanner": scanner
        }
        data = json.dumps(data)

        return self._request('POST', url, params='format=json', headers=headers, data=data)

    def web_scans(self, auth):
        """
        List all web scans
        :return:
        """
        # Headers included
        headers = all_headers(auth_token=auth)

        # Body data in json format
        url = '/api/webscan/'

        return self._request('GET', url, params='format=json', headers=headers)

    def zap_scans(self, auth):
        """
        List all web scans
        :return:
        """
        # Headers included
        headers = all_headers(auth_token=auth)

        # Body data in json format
        url = '/api/zapscanstatus/'

        return self._request('GET', url, params='format=json', headers=headers)

    def zap_scan_status(self, auth, scan_id):
        """

        :param auth:
        :param scan_id:
        :return:
        """

        url = '/api/zapscanstatus/'

        # Headers included
        headers = all_headers(auth_token=auth)

        # Body data in json format
        data = {
            "scan_scanid": scan_id
        }
        data = json.dumps(data)

        return self._request('POST', url, params='format=json', headers=headers, data=data)

    def burp_scan_status(self, auth, scan_id):
        """

        :param auth:
        :param scan_id:
        :return:
        """

        url = '/api/burpscanstatus/'

        # Headers included
        headers = all_headers(auth_token=auth)

        # Body data in json format
        data = {
            "scan_id": scan_id
        }
        data = json.dumps(data)

        return self._request('POST', url, params='format=json', headers=headers, data=data)

    def arachni_scan_status(self, auth, scan_id):
        """

        :param auth:
        :param scan_id:
        :return:
        """

        url = '/api/arachniscanstatus/'

        # Headers included
        headers = all_headers(auth_token=auth)

        # Body data in json format
        data = {
            "scan_id": scan_id
        }
        data = json.dumps(data)

        return self._request('POST', url, params='format=json', headers=headers, data=data)

    def dependencycheck_scan_status(self, auth, scan_id):
        """

        :param auth:
        :param scan_id:
        :return:
        """

        url = '/api/dependencycheckscanstatus/'

        # Headers included
        headers = all_headers(auth_token=auth)

        # Body data in json format
        data = {
            "scan_id": scan_id
        }
        data = json.dumps(data)

        return self._request('POST', url, params='format=json', headers=headers, data=data)

    def findbugs_scan_status(self, auth, scan_id):
        """

        :param auth:
        :param scan_id:
        :return:
        """

        url = '/api/findbugscanstatus/'

        # Headers included
        headers = all_headers(auth_token=auth)

        # Body data in json format
        data = {
            "scan_id": scan_id
        }
        data = json.dumps(data)

        return self._request('POST', url, params='format=json', headers=headers, data=data)

    def netsparker_scan_status(self, auth, scan_id):
        """

        :param auth:
        :param scan_id:
        :return:
        """

        url = '/api/netsparkerscanstatus/'

        # Headers included
        headers = all_headers(auth_token=auth)

        # Body data in json format
        data = {
            "scan_id": scan_id
        }
        data = json.dumps(data)

        return self._request('POST', url, params='format=json', headers=headers, data=data)

    def webinspect_scan_status(self, auth, scan_id):
        """

        :param auth:
        :param scan_id:
        :return:
        """

        url = '/api/webinspectscanstatus/'

        # Headers included
        headers = all_headers(auth_token=auth)

        # Body data in json format
        data = {
            "scan_id": scan_id
        }
        data = json.dumps(data)

        return self._request('POST', url, params='format=json', headers=headers, data=data)

    def acunetix_scan_status(self, auth, scan_id):
        """

        :param auth:
        :param scan_id:
        :return:
        """

        url = '/api/acunetixscanresult/'

        # Headers included
        headers = all_headers(auth_token=auth)

        # Body data in json format
        data = {
            "scan_id": scan_id
        }
        data = json.dumps(data)

        return self._request('POST', url, params='format=json', headers=headers, data=data)

    def create_project(self, auth, project_name, project_disc, project_start, project_end, project_owner):
        """
        Project Create
        :return:
        """
        url = '/api/project/'

        # Headers included
        headers = all_headers(auth_token=auth)
        print headers

        # Body data in json format
        data = {
            "project_name": project_name,
            "project_disc": project_disc,
            "project_start": project_start,
            "project_end": project_end,
            "project_owner": project_owner,
        }
        data = json.dumps(data)

        return self._request('POST', url, params='format=json', headers=headers, data=data)

    def list_project(self, auth):
        """
        Create Projects
        :return:
        """
        url = '/api/project/'

        # Headers included
        headers = all_headers(auth_token=auth)

        # Body data in json format
        return self._request('GET', url, params='format=json', headers=headers)

    def archery_auth(self, username, password):
        """
        Get the auth token.
        :return:
        """
        data = {"username": username, "password": password}
        data = json.dumps(data)
        url = '/api-token-auth/'
        return self._request('POST', url, params='format=json', data=data)

    def _request(self, method, url, params=None, headers=None, data=None):
        """Common handler for all the HTTP requests."""
        if not params:
            params = {}

        # set default headers
        if not headers:
            headers = {
                'Content-Type': 'application/json'
            }

        try:

            response = requests.request(method=method, url=self.host + url, params=params,
                                        headers=headers, data=data)

            try:
                response.raise_for_status()

                response_code = response.status_code
                success = True if response_code // 100 == 2 else False
                if response.text:
                    try:
                        data = response.json()
                    except ValueError:
                        data = response.content
                else:
                    data = ''

                return ArcheryResponse(success=success, response_code=response_code, data=data)
            except ValueError as e:
                return ArcheryResponse(success=False, message="JSON response could not be decoded {}.".format(e))
            except requests.exceptions.HTTPError as e:
                if response.status_code == 400:
                    return ArcheryResponse(success=False, response_code=400, message='Bad Request')
                else:
                    return ArcheryResponse(
                        message='There was an error while handling the request. {}'.format(response.content),
                        success=False)
        except Exception as e:
            return ArcheryResponse(success=False, message='Eerror is %s' % e)


class ArcheryResponse(object):
    """Container for all Archery REST API response, even errors."""

    def __init__(self, success, message='OK', response_code=-1, data=None):
        self.message = message
        self.success = success
        self.response_code = response_code
        self.data = data

    def __str__(self):
        if self.data:
            return str(self.data)
        else:
            return self.message

    def data_json(self, pintu=False):
        """Returns the data as a valid JSON String."""
        if pintu:
            return json.dumps(self.data, sort_keys=True, indent=4, separators=(',', ': '))
        else:
            return json.dumps(self.data)
