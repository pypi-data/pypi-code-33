"""
NewRelic as Metric Provider
"""

import requests
from .exceptions import NewRelicApiException
from .exceptions import NewRelicInvalidApiKeyException
from .exceptions import NewRelicInvalidParameterException


class NewRelic():

    api_key = None
    __api_url = "https://api.newrelic.com"
    __api_version = "v2"
    __apps_list_endpoint = "{url}/{version}/applications.json"
    __app_info_endpoint = "{url}/{version}/applications/{app_id}.json"
    __metrics_list_endpoint = "{url}/{version}/applications/{app_id}/metrics.json"
    __metric_info_endpoint = "{url}/{version}/applications/{app_id}/metrics/data.json"

    def __init__(self, api_key):
        self.api_key = api_key

    def get_apps(self):
        try:
            request = requests.get(
                self.__apps_list_endpoint.format(url=self.__api_url, version=self.__api_version),
                headers=self.get_headers(),
                data=''
            )
            if request.status_code == 200:
                return request
            else:
                raise NewRelicApiException("Error, Invalid status code %d" % (request.status_code))
        except Exception as e:
            raise NewRelicApiException(str(e))

    def get_app(self, app_id):

        if app_id is None or app_id == "":
            raise NewRelicInvalidParameterException("NewRelic application id is required!")

        try:
            request = requests.get(
                self.__app_info_endpoint.format(url=self.__api_url, version=self.__api_version, app_id=app_id),
                headers=self.get_headers(),
                data=''
            )
            if request.status_code == 200:
                return request
            else:
                raise NewRelicApiException("Error, Invalid status code %d" % (request.status_code))
        except Exception as e:
            raise NewRelicApiException(str(e))

    def get_metrics(self, app_id, name=None):

        if app_id is None or app_id == "":
            raise NewRelicInvalidParameterException("NewRelic application id is required!")

        data = {}
        if name is not None and name.strip() != "":
            data["name"] = name

        try:
            request = requests.get(
                self.__metrics_list_endpoint.format(url=self.__api_url, version=self.__api_version, app_id=app_id),
                headers=self.get_headers(),
                data=data
            )
            if request.status_code == 200:
                return request
            else:
                raise NewRelicApiException("Error, Invalid status code %d" % (request.status_code))
        except Exception as e:
            raise NewRelicApiException(str(e))

    def get_metric(self, app_id, names=[], values=[], start=None, end=None, summarize=False):

        if app_id is None or app_id == "":
            raise NewRelicInvalidParameterException("NewRelic application id is required!")

        if len(names) == 0:
            raise NewRelicInvalidParameterException("NewRelic application metric name(s) is required!")

        if len(values) == 0:
            raise NewRelicInvalidParameterException("NewRelic application metric value(s) is required!")

        data = {}
        data["names[]"] = []
        data["values[]"] = []

        for name in names:
            data["names[]"].append(name)

        for value in values:
            data["values[]"].append(value)

        if start is not None:
            data["from"] = start

        if end is not None:
            data["to"] = end

        if summarize:
            data["summarize"] = "true"
        else:
            data["summarize"] = "false"

        try:
            request = requests.get(
                self.__metric_info_endpoint.format(url=self.__api_url, version=self.__api_version, app_id=app_id),
                headers=self.get_headers(),
                data=data
            )
            if request.status_code == 200:
                return request
            else:
                raise NewRelicApiException("Error, Invalid status code %d" % (request.status_code))
        except Exception as e:
            raise NewRelicApiException(str(e))

    def get_headers(self):
        if self.api_key.strip() == "":
            raise NewRelicInvalidApiKeyException("NewRelic API Key is required!")
        return {
            'X-Api-Key': self.api_key
        }
