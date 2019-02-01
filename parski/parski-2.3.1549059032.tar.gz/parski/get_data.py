"""module for loading data from json file or from api"""
from __future__ import print_function

from os import environ
from time import sleep
import json

try:
    from urllib import quote_plus
except ImportError:
    from urllib.parse import quote_plus
import requests


def get_data(url=None, file_name='output.json', source="file", key=None, ssl_verify=True,
             key_var="PCT_API_READ_KEY", silent=False, api_retry=3, write_file=True, naapi=False):
    """get data class/function wrapper"""

    options = {
        'url': url,
        'file_name' : file_name,
        'source': source.lower(),
        'key': key,
        'key_var': key_var,
        'silent': silent,
        'api_retry': api_retry,
        'write_file': write_file,
        'naapi': naapi,
        'ssl_verify': ssl_verify
    }

    data_object = GetData(options)
    data_object.get_data()
    return data_object


class GetData(dict):
    """load data from json file or api"""
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, options):
        dict.__init__(self)
        self.data = None
        self.status_code = None
        self.error_msg = None
        self._headers = None

        self.options = options


    # Util Functions ------------------------------------------

    def _whisper(self, text, conditional=True):
        """print wrapper to check silent parameter"""
        if not self.options['silent'] and conditional:
            print(text)

    def _get_key(self):
        if self.options['key']:
            return self.options['key']
        return environ.get(self.options['key_var'], None) 
    
    def _set_response(self, response):
        self.data = response['data']
        self.status_code = response['status_code']
        self.error_msg = response['error_msg']

    def _write_data(self, data):
        if self.options['write_file']:
            with open(self.options['file_name'], 'w') as output_file:
                output_file.write(json.dumps(data, sort_keys=True, indent=4))
                output_file.close()
            self._whisper("File written successfully.")
    
    @staticmethod
    def __standardize(item):
        key_map = {
            "awsAccountId": "AccountId",
            "awsAccountAlias": "Alias",
            "AwsRegion": "Region",
            "Arn": "Arn",
            "AvailabilityZone": "AvailabilityZone"
        }

        new_item = {} if not item.get('configuration', None) else item.get('configuration', {})

        for (key, value) in key_map.items():
            new_item[value] = item[key]

        return new_item

    # Get Data Functions --------------------------------------

    def get_data(self):
        """Load data from either a source file or the api"""

        self._whisper("\nGetting Data...")

        # load from file
        if self.options['source'] == "file":
            self._whisper("Loading File %s..." % self.options['file_name'])
            try:
                response = self._file_load()
            except (IOError, ValueError) as error:
                if self.options['url']:
                    self._whisper("No file exists.", error.__class__.__name__ == "IOError")
                    self._whisper("File isn't valid JSON.", error.__class__.__name__ == "ValueError")
                    response = self._api_load()
                else:
                    self._whisper("Bad file AND no url specified.  No data returned.")
                    response = {
                        'status_code': 404,
                        'error_msg': "Bad file AND no url specified.  No data returned.",
                        'data': None
                    }

        # load from api
        elif self.options['source'] == "api":
            response = self._api_load()

        # bad source
        else:
            self._whisper("Source paramater must be 'api' or 'file'")
            response = {
                'status_code': 500,
                'error_msg': "Invalid source parameter.  Must be 'api' or 'file'",
                'data': None
            }

        self._set_response(response)
        return response

    def _file_load(self):
        with open(self.options['file_name'], 'rb') as stored_file:
            data = json.loads(stored_file.read())
            self._whisper("File Loaded.")
            stored_file.close()
        return {
            'status_code': 200,
            'error_msg': None,
            'data': data
        }

    # Api Functions ----------------------------------------------

    def _api_load(self):
        """load data from api"""

        # Set headers
        key = self._get_key()
        if not key:
            self._whisper("WARNING:  No key found.")
            return {
                'status_code': 401,
                'error_msg': self.options['key_var'] + ' could not be loaded.  Unauthorized.',
                'data': None
            }

        self._headers = {'x-api-key': key, 'Cache-Control': 'no-cache'}

        if self.options['naapi']:
            return self._naapi_load()
        return self._clapshot_load()

    def _clapshot_load(self):
        # Initial api try
        response, resp_headers = self._api_try(None)
        if response['data'] is None:
            return response

        # Get page count, output of none or page count is 1
        try:
            page_count = int(resp_headers.get("x-pagination-page-count"))
            if page_count == 1:
                raise BaseException
            response['data'] = []
        except (KeyError, TypeError, BaseException):
            self._whisper(
                "No page count / One page specified.  Writing Single Page...")
            json_string = response['data']
            clean_json_string = '[' + json_string.lstrip('[').rstrip(']') + ']'
            response['data'] = json.loads(clean_json_string)
            self._write_data(json.loads(clean_json_string))
            return response

        # Download each page
        self._whisper("%s pages to be downloaded" % page_count)
        for page in range(1, page_count+1):
            single_response = self._api_try(page)[0]
            if single_response['data']:
                json_string = single_response['data']
                clean_json_string = "[%s]" % json_string.lstrip('[').rstrip(']')
                response['data'].extend(json.loads(clean_json_string))
        self._write_data(response['data'])
        return response


    def _naapi_load(self):
        # Initial api try
        response = self._api_try(None)[0]
        if response['data'] is None:
            return response

        resources = json.loads(response['data'])['hits']['hits']
        if not resources:
            self._whisper("No results, check your query.")
            return response

        data = [x['_source'] for x in resources]

        while resources:
            last_id = resources[len(resources) - 1]['_id']
            response = self._api_try(last_id)[0]
            resources = json.loads(response['data'])['hits']['hits']
            data.extend([x['_source'] for x in resources])

        response['data'] = [self.__standardize(x) for x in data]
        self._write_data(response['data'])
        return response


    def _api_try(self, page):
        tries = 0
        self._whisper("\nPage: %s" % page)
        while tries < self.options['api_retry']:
            self._whisper("Sending API request...")
            response, resp_headers = self._api_call(page)
            self._whisper(response['error_msg'], response['error_msg'])
            if response['status_code'] == 401 or response['status_code'] == 404:
                return response, None
            if str(response['status_code']).startswith("2"):
                self._whisper("Response returned successfully.")
                return response, resp_headers
            self._whisper("Trying again in %s seconds\n" % ((tries+1)**2))
            sleep((tries+1)**2)
            self._whisper("LET'S DO THIS!!!!")
            tries += 1
        response['error_msg'] = "Amount of Fails Exceeded.  The API doesn't want to talk to you."
        return response, resp_headers

    def _api_call(self, page):
        response = {
            'status_code': 200,
            'data': None,
            'error_msg': None
        }

        temp_url = self.options['url']
        url_key = "search_after" if self.options['naapi'] else "Page"
        if page is not None and "?" not in self.options['url']:
            temp_url += "?%s=%s" % (url_key, quote_plus(str(page)))
        elif page is not None:
            temp_url += "&%s=%s" % (url_key, quote_plus(str(page)))
        try:
            self._whisper("GET %s" % temp_url)
            req = requests.get(temp_url, headers=self._headers, verify=self.options['ssl_verify'])
        except Exception as error:
            response['error_msg'] = 'API Server could not be reached'
            response['status_code'] = 404
            return response, None

        response['status_code'] = req.status_code
        if req.status_code != 200:
            self._whisper("WARNING:  API call status code was %s" % req.status_code)

        status_messages = {
            "200": None,
            "401": "Unauthorized.  Your API key isn't working...",
            "404": "Not found.  Your url is probably wrong or you're not on VPN",
            "500": "Internal Server Error.  The API might be down.",
            "502": "The response failed.  This happens from time to time.",
            "503": "Internal Server Error.  The API might be down."
        }

        response['error_msg'] = status_messages.get(str(req.status_code), "Unknown Error")
        if not str(response['status_code']).startswith("2"):
            try:
                 response['error_msg'] = json.dumps(req.json())
            except ValueError:
                pass
        else:
            try:
                response['data'] = json.dumps(req.json())
            except ValueError:
                response['error_msg'] = 'Returned request could not be converted to json'

        return response, req.headers
