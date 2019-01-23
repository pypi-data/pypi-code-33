import json
import datetime
import requests
from opisense_client.http import POST, PUT, DELETE

""" Parameters """
STANDARD_PUSH_DATA_URL = 'https://push.opinum.com/api/data/'

""" Opisense Objects """


class ApiFilter:
    def __init__(self, path: str, **filters):
        """
        Builds a filter object used to set the parameters to request data from Opisense API.
        :param path: API path
        :param filters: filters to be applied to the GET request
        """
        self.path = path
        _ = {}
        for filter in filters:
            _[filter] = filters[filter]
        self.filters = _

    def __add__(self, **filters):
        """
        Add parameters to the API filter
        :param filters: parameters to add
        """
        for filter in filters:
            self.filters[filter] = filters[filter]


class DataPoints:
    def __init__(self, date: datetime, value: float):
        """
        Builds a standard datapoint list to build a StandardData object
        :param date: datetime object
        :param value: floating point value
        """
        date = date.strftime('%Y-%m-%dT%H:%M:%S%z')
        self.list = [{'date': date, 'value': value}]
        self.json = json.dumps(self.list)

    def __add__(self, date: datetime, value: float):
        """
        Add datapoints to
        :param date: datetime object
        :param value: floating point value
        :return:
        """
        date = date.strftime('%Y-%m-%dT%H:%M:%S%z')
        self.list.append({'date': date, 'value': value})
        self.json = json.dumps(self.list)


class StandardData:
    def __init__(self, datapoints: DataPoints, sourceId=None, sourceSerialNumber=None, meterNumber=None,
                 sourceEan=None, mappingConfig=None, variableId=None):
        """
        Builds a StandardData object to be pushed to Opisense API.
        At least one of the optionals args must be present.
        :param datapoints: DataPoint object
        :param sourceId: optional : Opisense Source internal identifier
        :param sourceSerialNumber: optional : Opisense Source Serial Number
        :param meterNumber: optional : Opisense Source Meter Number
        :param sourceEan: optional : Opisense Source EAN Number
        :param mappingConfig: optional : Opisense Variable Mapping
        :
        """
        if sourceId or sourceSerialNumber or sourceEan or meterNumber and mappingConfig:
            args = {}
            args['sourceId'] = sourceId
            args['sourceSerialNumber'] = sourceSerialNumber
            args['meterNumber'] = meterNumber
            args['sourceEan'] = sourceEan
            args['mappingConfig'] = mappingConfig
            args['data'] = datapoints.list
            self.list = [args]
            self.json = json.dumps(self.list)
        elif variableId:
            args = {}
            args['variableId'] = mappingConfig
            args['data'] = datapoints.list
            self.list = [args]
            self.json = json.dumps(self.list)

        else:
            raise ValueError(
                'At least one of the optional source parameters + mapping config or just the variableId is mandatory')

    def POST(self, opisense_token: str, feedback=False):
        """
        POST the StandardData object to the Opisense API
        :param opisense_token: Opisense Bearer token
        :param feedback: if feedback = True, returns the http response code
        :return:
        """
        result = requests.post(STANDARD_PUSH_DATA_URL,
                               data=self.json,
                               headers={"Authorization": opisense_token,
                                        "Content-Type": "application/json"})
        if feedback == True:
            print('Response: ' + str(result.status_code))
        return result


class OpisenseObject:
    def __init__(self, type: str, opisense_object: dict, id=None):
        """
        Creates an Opisense Object
        :param type: Opisense object type (site, gateway, source, variable, form,...)
        :param opisense_object: dictionary containing the Opisense structure for this object type
        :param id:optional : Opisense internal object ID
        """
        self.id = id
        self.type = type.lower()
        self.content = opisense_object
        self.api_path = self.type + 's'

    POST = POST
    PUT = PUT
    DELETE = DELETE

    def json(self):
        """
        Serialize the object in JSON
        :return: JSON
        """
        return json.dumps(self.content)
