import json
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

    def update_person(self, data: dict):
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :return: status code for request and optional error message
        """
        allowed_fields = ['employee_id', 'mail_work', 'mail_private', 'mobile_work', 'mobile_private', 'nickname', 'first_name', 'initials', 'prefix', 'last_name',
                          'birth_name', 'gender', 'nationality', 'birth_date', 'country_of_birth', 'ssn', 'marital_status', 'date_of_marriage', 'phone_work', 'phone_private']
        required_fields = ['employee_id']
        for field in data.keys():
            if field not in allowed_fields and field not in required_fields:
                return 'Pietertje, field {field} is not allowed. Allowed fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields))

        for field in required_fields:
            if field not in data.keys():
                return 'Pietertje, field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee/KnPerson')
        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }
        base_body = {
            "AfasEmployee": {
                "Element": {
                    "@EmId": data['employee_id'],
                    "Objects": {
                        "KnPerson": {
                            "Element": {
                                "Fields": {
                                    "MatchPer": "0",
                                    "BcCo": data['employee_id']
                                }
                            }
                        }
                    }
                }
            }
        }
        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"EmA": data['mail_work']}) if 'mail_work' in data else fields_to_update
        fields_to_update.update({"EmA2": data['mail_private']}) if 'mail_private' in data else fields_to_update
        fields_to_update.update({"MbNr": data['mobile_work']}) if 'mobile_work' in data else fields_to_update
        fields_to_update.update({"MbN2": data['mobile_private']}) if 'mobile_private' in data else fields_to_update
        fields_to_update.update({"CaNm": data['nickname']}) if 'nickname' in data else fields_to_update
        fields_to_update.update({"FiNm": data['first_name']}) if 'first_name' in data else fields_to_update
        fields_to_update.update({"In": data['initials']}) if 'initials' in data else fields_to_update
        fields_to_update.update({"Is": data['prefix']}) if 'prefix' in data else fields_to_update
        fields_to_update.update({"LaNm": data['last_name']}) if 'last_name' in data else fields_to_update
        fields_to_update.update({"NmBi": data['birth_name']}) if 'birth_name' in data else fields_to_update
        fields_to_update.update({"ViGe": data['gender']}) if 'gender' in data else fields_to_update
        fields_to_update.update({"PsNa": data['nationality']}) if 'nationality' in data else fields_to_update
        fields_to_update.update({"DaBi": data['birth_date']}) if 'birth_date' in data else fields_to_update
        fields_to_update.update({"RsBi": data['country_of_birth']}) if 'country_of_birth' in data else fields_to_update
        fields_to_update.update({"SoSe": data['ssn']}) if 'ssn' in data else fields_to_update
        fields_to_update.update({"ViCs": data['marital_status']}) if 'marital_status' in data else fields_to_update
        fields_to_update.update({"DaMa": data['date_of_marriage']}) if 'date_of_marriage' in data else fields_to_update
        fields_to_update.update({"TeNr": data['phone_work']}) if 'phone_work' in data else fields_to_update
        fields_to_update.update({"TeN2": data['phone_private']}) if 'phone_private' in data else fields_to_update

        # Update the request body with update fields
        base_body['AfasEmployee']['Element']['Objects']['KnPerson']['Element']['Fields'].update(fields_to_update)

        update = requests.request("PUT", url, data=json.dumps(base_body), headers=headers)

        return update.text


    def update_address(self, data: dict):
        """
        :param data: Fields that are allowed are listed in allowed fields array. Update this whenever necessary
        :return: status code for request and optional error message
        """
        allowed_fields = ['street_number_add', 'city']
        required_fields = ['employee_id', 'country', 'street', 'street_number', 'postal_code']
        for field in data.keys():
            if field not in allowed_fields and field not in required_fields:
                return 'Pietertje, field {field} is not allowed. Allowed fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields))

        for field in required_fields:
            if field not in data.keys():
                return 'Pietertje, field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee/KnPerson')
        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }
        base_body = {
            "AfasEmployee": {
                "Element": {
                    "@EmId": data['employee_id'],
                    "Objects": {
                        "KnPerson": {
                            "Element": {
                                "Fields": {
                                    "MatchPer": "0",
                                    "BcCo": data['employee_id']
                                },
                                "Objects": {
                                    "KnBasicAddressAdr": {
                                        "Element": {
                                            "Fields": {
                                                "CoId": data['country'],
                                                "PbAd": True,
                                                "Ad": data['street'],
                                                "HmNr": data['street_number'],
                                                "BcCo": data['employee_id'],
                                                "ZpCd": data['postal_code'],
                                                "ResZip": True
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        fields_to_update = {}

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update.update({"HmAd": data['street_number_add']}) if 'street_number_add' in data else fields_to_update
        fields_to_update.update({"Rs": data['city']}) if 'city' in data else fields_to_update

        # Update the request body with update fields
        base_body['AfasEmployee']['Element']['Objects']['KnPerson']['Element']['Objects']['KnBasicAddressAdr']['Element']['Fields'].update(fields_to_update)

        update = requests.request("PUT", url, data=json.dumps(base_body), headers=headers)

        return update.text


    def new_contract(self, data: dict):
        """
        :param data: Dictionary of fields that you want to update in AFAS. Only fields listed in allowed arrays are accepted. Fields listed in required fields array, are mandatory
        :return: status code for request and optional error message
        """
        allowed_fields = ['employee_id', 'type_of_employment', 'enddate_contract']
        allowed_fields_function = ['organizational_unit', 'function_id', 'costcenter_id', 'costcarrier_id']
        allowed_fields_timetable = ['changing_work_pattern', 'weekly_hours', 'parttime_percentage']
        allowed_fields_salary = ['type_of_salary', 'step', 'salary_amount', 'period_table']
        allowed_fields = allowed_fields + allowed_fields_salary + allowed_fields_timetable + allowed_fields_function
        required_fields = ['employee_id', 'startdate_contract', 'cao', 'terms_of_employment', 'type_of_contract', 'employer_number', 'type_of_employee', 'employment']

        # Check if there are fields that are not allowed or fields missing that are required
        for field in data.keys():
            if field not in allowed_fields and field not in required_fields:
                return 'Pietertje, field {field} is not allowed. Allowed fields are: {allowed_fields}'.format(field=field, allowed_fields=tuple(allowed_fields))
        for field in required_fields:
            if field not in data.keys():
                return 'Pietertje, field {field} is required. Required fields are: {required_fields}'.format(field=field, required_fields=tuple(required_fields))

        url = 'https://{}.{}/profitrestservices/connectors/{}'.format(self.environment, self.base_url, 'KnEmployee/AfasContract')
        headers = {
            'authorization': "AfasToken {0}".format(self.base64token),
            'content-type': "application/json",
            'cache-control': "no-cache"
        }
        base_body = {
          "AfasEmployee": {
            "Element": {
              "@EmId": data['employee_id'],
              "Objects": {
                "AfasContract": {
                  "Element": {
                    "@DaBe": data['startdate_contract'],
                    "Fields": {
                      "ClId": data['cao'],
                      "WcId": data['terms_of_employment'],
                      "ApCo": data['type_of_contract'],
                      "CmId": data['employer_number'],
                      "EmMt": data['type_of_employee'],
                      "ViEt": data['employment']
                    }
                  }
                }
              }
            }
          }
        }

        # Extra JSON objects which are optional at contract creation
        function = {
            "AfasOrgunitFunction": {
                "Element": {
                    "@DaBe": data['startdate_contract'],
                    "Fields": {
                        "DpId": "SUP_0048",
                        "FuId": "0854",
                        "CcId": "RSD",
                        "CrId": "3420"
                    }
                }
            }
        }

        timetable = {
            "AfasTimeTable": {
                "Element": {
                    "@DaBg": data['startdate_contract'],
                    "Fields": {
                        "StPa": True,
                        "HrWk": 40,
                        "PcPt": 100
                    }
                }
            }
        }

        salary = {
            "AfasSalary": {
                "Element": {
                    "@DaBe": data['startdate_contract'],
                    "Fields": {
                        "SaPe": "V",
                        "EmSa": 3000,
                        "PtId": 5
                    }
                }
            }
        }

        # If one of the optional fields of a subelement is included, we need to merge the whole JSON object to the basebody
        if any(field in data.keys() for field in allowed_fields_function):
            # TODO: check if mandatory fields for subelement are present (they're initially not mandatory, but when you fill one, the others become mandatory)
            fields_to_update = {}
            fields_to_update.update({"DpId": data['organizational_unit']}) if 'organizational_unit' in data else fields_to_update
            fields_to_update.update({"FuId": data['function_id']}) if 'function_id' in data else fields_to_update
            fields_to_update.update({"CcId": data['costcenter_id']}) if 'costcenter_id' in data else fields_to_update
            fields_to_update.update({"CrId": data['costcarrier_id']}) if 'costcarrier_id' in data else fields_to_update

            # merge subelement with basebody
            function['AfasOrgunitFunction']['Element']['Fields'].update(fields_to_update)
            base_body['AfasEmployee']['Element']['Objects'].update(function)

        if any(field in data.keys() for field in allowed_fields_timetable):
            fields_to_update = {}
            fields_to_update.update({"SaSt": data['step']}) if 'step' in data else fields_to_update
            fields_to_update.update({"StPa": data['changing_work_pattern']}) if 'changing_work_pattern' in data else fields_to_update
            fields_to_update.update({"HrWk": data['weekly_hours']}) if 'weekly_hours' in data else fields_to_update
            fields_to_update.update({"PcPt": data['parttime_percentage']}) if 'parttime_percentage' in data else fields_to_update

            timetable['AfasTimeTable']['Element']['Fields'].update(fields_to_update)
            base_body['AfasEmployee']['Element']['Objects'].update(timetable)

        if any(field in data.keys() for field in allowed_fields_salary):
            fields_to_update = {}
            fields_to_update.update({"SaSt": data['step']}) if 'step' in data else fields_to_update
            fields_to_update.update({"SaPe": data['type_of_salary']}) if 'type_of_salary' in data else fields_to_update
            fields_to_update.update({"EmSa": data['salary_amount']}) if 'salary_amount' in data else fields_to_update
            fields_to_update.update({"PtId": data['period_table']}) if 'period_table' in data else fields_to_update

            salary['AfasSalary']['Element']['Fields'].update(fields_to_update)
            base_body['AfasEmployee']['Element']['Objects'].update(salary)

        # Add fields that you want to update a dict (adding to body itself is too much text)
        fields_to_update = {}
        fields_to_update.update({"DaEn": data['enddate_contract']}) if 'enddate_contract' in data else fields_to_update
        fields_to_update.update({"PEmTy": data['type_of_employment']}) if 'type_of_employment' in data else fields_to_update

        # Update the request body with update fields
        base_body['AfasEmployee']['Element']['Objects']['AfasContract']['Element']['Fields'].update(fields_to_update)

        update = requests.request("POST", url, data=json.dumps(base_body), headers=headers)

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