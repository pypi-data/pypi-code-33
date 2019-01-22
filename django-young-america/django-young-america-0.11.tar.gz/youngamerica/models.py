import dicttoxml
import xmltodict
import zeep

from django.conf import settings


class YaException(Exception):
    pass


class YaResponse():
    def __init__(self, xml_string):
        self.xml = xml_string
        self.prize_code = None
        self.error_code = None
        self.status = None
        self.is_new = False
        self.internal_id = None
        # deserialize response
        if '<YASubmissionResponse>' in self.xml:
            self.is_new = True  # New consumer
            resp = xmltodict.parse(self.xml).get('YASubmissionResponse')
        elif '<ConsumerAddEntryResponse>' in self.xml:
            resp = xmltodict.parse(self.xml).get('ConsumerAddEntryResponse')
        else:
            raise YaException('Failed to find <YASubmissionResponse> or <ConsumerAddEntryResponse> in response {}'.format(self.xml))

        self.status = resp.get('Status')
        self.severity = resp.get('Severity')
        if self.is_new and resp.get('ResponseItem'):
            if resp['ResponseItem'].get('InstantWinner'):
                self.internal_id = resp['ResponseItem']['InstantWinner'] \
                    .get('ConsumerGuid')
                self.prize_code = resp['ResponseItem']['InstantWinner'] \
                    .get('ItemCode')
            if resp['ResponseItem'].get('ErrorItem'):
                self.error_code = resp['ResponseItem']['ErrorItem'].get('Code')
        elif resp.get('InstantWinners'):
            self.internal_id = resp.get('ConsumerGuid')
            self.prize_code = resp['InstantWinners'].get('ItemCode')
        elif resp.get('ErrorItem'):
            self.internal_id = resp.get('ConsumerGuid')
            self.error_code = resp['ErrorItem'].get('Code')


class YaClient:
    def __init__(self):
        self.client = zeep.Client(wsdl=str(settings.YA_ENDPOINT_URL) + '?WSDL')
        self.config = {
            'client_id': settings.YA_CLIENT_ID,
            'offer_id': settings.YA_SWEEPS_ID,
            'offer_token': settings.YA_SWEEPS_TOKEN,
            'vendor_code': settings.YA_VENDOR_CODE,
            'entry_method': settings.YA_ENTRY_METHOD,
        }

    def send(self, profile: dict) -> YaResponse:
        request_dict = self.get_request_dictionary(profile)
        request_xml = dicttoxml.dicttoxml(request_dict, custom_root='YASubmissionRequest')
        response = self.client.service.ProcessRequest(request_xml)
        return YaResponse(response)

    def get_request_dictionary(self, profile):
        return {
            'RequestHeader': {
                'ClientID': self.config['client_id'],
                'OfferID': self.config['offer_id'],
                'SecurityToken': self.config['offer_token'],
                'Action': 'ConsumerInsertOrAddEntry',
                'VendorCode': self.config['vendor_code'],
                'RecordCount': 1,
                'ReturnIdsFlag': 'true',
            },
            'UniqueField': 'ExternalID',
            'ConsumerData': {
                'ExternalID': profile['email'],
                'EntryMethodID': self.config['entry_method'],
                'FirstName': profile['first_name'],
                'LastName': profile['last_name'],
                'Address1': profile['address'],
                'City': profile['city'],
                'State': profile['state'],
                'PostalCode': profile['zip_code'],
                'CountryCode': 'US',
                'Email': profile['email'],
                'DateOfBirth': profile['date_of_birth'],
                'DailyEntry': {
                    'EntryDate': profile['entry_date'],
                }
            }
        }
