"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from __future__ import print_function

import os
import sys
from time import sleep
import calendar
import requests
import logging
import threading
import time
import subprocess

API_URL = 'https://vlab.jumper.io/api/v2'
if 'JUMPER_STAGING' in os.environ:
    API_URL = 'https://us-central1-jemu-web-app-staging.cloudfunctions.net/api/v2'
if 'JUMPER_STAGING_INBAR' in os.environ:
    API_URL = 'https://us-central1-jemu-web-app-inbar.cloudfunctions.net/api/v2'


class WebException(Exception):
    pass


class AuthorizationError(WebException):
    def __init__(self, message):
        super(WebException, self).__init__(message)
        self.exit_code = 4
        self.message = message


class UnInitializedError(WebException):
    def __init__(self):
        print("Failed to get user id. Please reach out to support@jumper.io for help")
        super(WebException, self).__init__("Failed to get user id. Please reach out to support@jumper.io for help")
        self.exit_code = 6
        self.message = "Failed to get user id. Please reach out to support@jumper.io for help"


class EmulatorGenerationError(WebException):
    def __init__(self, message):
        super(WebException, self).__init__(message)
        self.exit_code = 5
        self.message = message


class JemuWebApi(object):
    def __init__(self, jumper_token=None, api_url=API_URL, local_jemu=None):
        self._api_url = api_url
        self._token = jumper_token
        self._headers = {'Authorization': 'Bearer ' + self._token}
        self._local_jemu = local_jemu
        self._queried_pu = False
        self._is_pu_flag = False
        self._threads = []
        self._events_queue = None
        
        logging.getLogger("requests").setLevel(logging.WARNING)
        res = requests.get(self._api_url + '/hello', headers=self._headers)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == requests.codes['unauthorized'] or res.status_code == requests.codes['forbidden']:
                print("Error: Authorization failed. Check the token in your config.json file")
                raise AuthorizationError("Error: Authorization failed. Check the token in the config.json file.")
            else:
                raise e

        self._user_uid = res.json()['userUid']

    @property
    def user_uid(self):
        return self._user_uid

    def upload_firmware(self, filepath, user_error_reporting):
        filename = self._get_file_name(filepath)
        t = threading.Thread(target=self._upload_file, args=[filepath, filename, "fw", user_error_reporting])
        t.start()
        self._threads.append(t)

    def upload_log_file(self, filepath, filename, user_error_reporting):
        t = threading.Thread(target=self._upload_file, args=[filepath, filename, "log", user_error_reporting])
        t.start()
        self._threads.append(t)

    @staticmethod
    def _get_file_name(filepath):
        filename = os.path.basename(filepath)
        signs = {"$", "#", "[", "]"}
        num_of_signs = filename.count('.') - 1
        filename = filename.replace('.', '_', num_of_signs)
        for i in signs:
            filename = filename.replace(i, '_')

        filename = str(int(calendar.timegm(time.gmtime()))) + '_' + filename
        return filename

    def _upload_file(self, filepath, filename, type, user_error_reporting=None):
        if self._user_uid is None:
            raise UnInitializedError

        file_exist = False
        headers = self._headers
        headers['Content-Type'] = 'application/octet-stream'
        success = False

        for try_number in range(3):
            try:
                post_res = requests.post(
                    '{}/firmwares/upload/{}/{}'.format(self._api_url, self._user_uid, filename),
                    headers=headers
                )
                post_res.raise_for_status()
                storage_filename = os.path.basename(post_res.url)
                signed_url = post_res.text
                if os.path.isfile(filepath):
                    file_exist = True
                    script_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), "put_file.py")
                    subprocess.Popen(["python", os.path.expanduser(script_file), filepath, signed_url])
                    
            except requests.HTTPError, requests.ConnectionError:
                sleep(1)
                continue
            success = True
            break

        if success:
            if not file_exist:
                get_res = "no_link"
                storage_filename = "no_file"
            else:
                get_res = self._get_download_url(storage_filename)

            if type == "fw":
                user_error_reporting.set_file_download_link(get_res)
                user_error_reporting.set_filename(storage_filename)
            elif type == "log":
                get_res = self._get_download_url(storage_filename)
                user_error_reporting.set_log_file_download_link(get_res)
        else:
            sys.stderr.write("Error: Could not upload file")

    def _upload_log_file(self, filepath, filename):
        if self._user_uid is None:
            raise UnInitializedError

        headers = self._headers
        headers['Content-Type'] = 'application/octet-stream'
        success = False

        for try_number in range(3):
            try:
                post_res = requests.post(
                    '{}/firmwares/upload/{}/{}'.format(self._api_url, self._user_uid, filename),
                    headers=headers
                )
                post_res.raise_for_status()
                signed_url = post_res.text
                with open(filepath, 'rb') as data:
                    post_res = requests.put(signed_url, data=data)
                    post_res.raise_for_status()
            except requests.HTTPError, requests.ConnectionError:
                sleep(1)
                continue
            success = True
            break

        if not success:
            sys.stderr.write("Error: Could not upload file")

    def send_event(self, event_name, event_labels):
        if self._user_uid is None:
            raise UnInitializedError

        headers = self._headers
        headers['Content-Type'] = 'application/json'
        res = requests.post(
            '{}/analytics/{}/{}'.format(self._api_url, self._user_uid, event_name),
            headers=headers,
            json=event_labels,
            timeout=5
        )
        # print(res.text)
        return res

    def stop(self):
        for t in self._threads:
            if t.is_alive():
                t.join()

    def is_pu(self):
        if not self._queried_pu:
            self._queried_pu = True
            res = self._get('users/{}/pu'.format(self._user_uid))
            self._is_pu_flag = res.text == "true"
        
        return self._is_pu_flag

    def _get_download_url(self, filename):
        res = self._get('firmwares/{}/{}'.format(self._api_url, self._user_uid, os.path.basename(filename)))
        return res.text

    def _get(self, path):
        if self._user_uid is None:
            raise UnInitializedError
        headers = self._headers.copy()
        headers['Content-Type'] = 'application/text'
        return requests.get('{}/{}'.format(self._api_url, path), headers=headers)

    def __del__(self):
        self.stop()
