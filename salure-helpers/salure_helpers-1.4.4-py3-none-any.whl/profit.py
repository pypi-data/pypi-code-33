import time
import requests


class GetConnector:

    def __init__(self,  environment, base64token, base_url='rest.afas.online'):
        self.environment = environment
        self.base64token = base64token
        self.base_url = base_url

    def get_metadata(self):
        url = 'https://{}.{}/profitrestservices/metainfo'.format(self.environment, self.base_url)
        authorizationHeader = {'Authorization': 'AfasToken ' + self.base64token}
        vResponse = requests.get(url, headers=authorizationHeader).json()['getConnectors']

        return vResponse
        # for key in vResponse:
        #     if len(key['id']) > 0:
        #         self.get_data(key['id'])


    def get_data(self, connector):
        start = time.time()

        vTotalResponse = []
        loopBoolean = True
        NoOfLoops = 0
        vNoOfRresults = 0

        while loopBoolean:
            url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, connector)
            parameters = { "skip": 40000 * NoOfLoops, "take": 40000}
            authorizationHeader = {'Authorization': 'AfasToken {}'.format(self.base64token)}
            vResponseJson = requests.get(url.encode("utf-8"), parameters, headers=authorizationHeader).json()['rows']
            NoOfLoops += 1
            vNoOfRresults += len(vResponseJson)
            loopBoolean = True if len(vResponseJson) == 40000 else False

            print(time.strftime('%H:%M:%S'), 'Got next connector from profit: ',connector, ' With nr of rows: ', vNoOfRresults)
            vTotalResponse += vResponseJson

        return vTotalResponse


    def get_filtered_data(self, connector, fields=None, values=None, operators=None):
        # possible operators are: [1:=, 2:>=, 3:<=, 4:>, 5:<, 6:exists, 7:!=, 8:isEmpty, 9:notEmpty]
        # for AND filter, use ',' between fields and values, for OR filter, use ';'

        vTotalResponse = []
        loopBoolean = True
        NoOfLoops = 0
        vNoOfRresults = 0


        if fields != None:
            parameters = {"filterfieldids": fields, "filtervalues": values, "operatortypes": operators}
        else:
            parameters = {}

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, connector)

        while loopBoolean:
            loopParameters = {"skip": 10000 * NoOfLoops, "take": 10000}
            parameters.update(loopParameters)
            authorizationHeader = {'Authorization': 'AfasToken ' + self.base64token}
            vResponseJson = requests.get(url.encode("utf-8"), parameters, headers=authorizationHeader).json()['rows']
            NoOfLoops += 1
            vNoOfRresults += len(vResponseJson)
            loopBoolean = True if len(vResponseJson) == 10000 else False
            print(time.strftime('%H:%M:%S'), connector, vNoOfRresults)

            vTotalResponse += vResponseJson

        return vTotalResponse


class UpdateConnector:

    def __init__(self, environment, base64token, base_url='rest.afas.online'):
        self.environment = environment
        self.base64token = base64token
        self.base_url = base_url

    def update(self, updateconnector, data):
        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, updateconnector)

        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }

        update = requests.request("PUT", url, data=data, headers=headers)

        return update.text


    def post(self, rest_type, updateconnector, data):
        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, updateconnector)

        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }

        update = requests.request(rest_type, url, data=data, headers=headers)

        return update.text