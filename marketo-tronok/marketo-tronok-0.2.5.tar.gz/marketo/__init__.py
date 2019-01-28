import datetime
import json
from collections import namedtuple

from .version import VERSION

__version__ = VERSION

import requests
from .auth import header
import xml.etree.ElementTree as ET

from .wrapper import get_lead, get_lead_activity, request_campaign, \
    sync_lead, get_multiple_leads, get_lead_changes

from .exceptions import MktoSoapException, MktoRateLimitExceedException

class Client:

    def __init__(self, soap_endpoint=None, user_id=None, encryption_key=None, rate_limit_checker=None):

        if not soap_endpoint or not isinstance(soap_endpoint, str):
            raise ValueError('Must supply a soap_endpoint as a non empty string.')

        if not user_id or not isinstance(user_id, str):
            raise ValueError('Must supply a user_id as a non empty string.')

        if not encryption_key or not isinstance(encryption_key, bytes):
            raise ValueError('Must supply a encryption_key as a non empty encoded string.')

        self.soap_endpoint = soap_endpoint
        self.user_id = user_id
        self.encryption_key = encryption_key
        self.rate_limit_checker = rate_limit_checker

    def handle_error(self, response):
        resp = ET.fromstring(response.text.encode("utf-8"))
        error_code = int(resp.find(".//code").text)
        message = resp.find(".//message").text
        if error_code in (20015, 20023, 20024):
            raise MktoRateLimitExceedException(error_code=error_code, message=message)
        else:
            raise MktoSoapException(error_code=error_code, message=message)

    def wrap(self, body):
        return (
            '<?xml version="1.0" encoding="UTF-8"?>' +
            '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"' +
                          'xmlns:ns1="http://www.marketo.com/mktows/" ' +
                          'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'+
                header(self.user_id, self.encryption_key) +
                '<SOAP-ENV:Body>' +
                    body +
                '</SOAP-ENV:Body>' +
            '</SOAP-ENV:Envelope>')

    def request(self, body):
        if self.rate_limit_checker is not None:
            self.rate_limit_checker.run(None)
        envelope = self.wrap(body)
        response = requests.post(self.soap_endpoint, data=envelope,
            headers={
                'Connection': 'Keep-Alive',
                'Soapaction': '',
                'Content-Type': 'text/xml;charset=UTF-8',
                'Accept': '*/*'})

        return response

    def get_lead_changes(self, oldest_created_at, latest_created_at):
        if not oldest_created_at or not isinstance(oldest_created_at, datetime.datetime):
            raise ValueError('Must supply oldest_created_at as a datetime object')
        if not latest_created_at and not isinstance(latest_created_at, datetime.datetime):
            raise ValueError('Must supply latest_created_at as a datetime object')
        all_activities = []
        remaining_count = 1
        new_stream_position = namedtuple('newStreamPosition', ['latest_created_at', 'oldest_created_at', 'offset'])
        stream_position = new_stream_position(latest_created_at, oldest_created_at, False)
        while remaining_count:
            body = get_lead_changes.wrap(oldest_created_at=stream_position.oldest_created_at,
                                         latest_created_at=stream_position.latest_created_at,
                                         offset=stream_position.offset)
            response = self.request(body)
            if response.status_code == 200:
                stream_position, remaining_count, activities = get_lead_changes.unwrap(response, new_stream_position)
                all_activities.extend(activities)
            else:
                self.handle_error(response)

    def get_multiple_leads_last_update_selector(self,
                                                oldest_updated_at,
                                                latest_updated_at,
                                                file_stream=None):
        if not oldest_updated_at or not isinstance(oldest_updated_at, datetime.datetime):
            raise ValueError('Must supply oldest_updated_at as a datetime object')
        if not latest_updated_at and not isinstance(latest_updated_at, datetime.datetime):
            raise ValueError('Must supply latest_updated_at as a datetime object')

        all_leads = []
        new_stream_position = False
        remaining_count = 1
        number_of_fetched_leads = 0
        while remaining_count:
            body = get_multiple_leads.wrap(oldest_updated_at=oldest_updated_at,
                                           latest_updated_at=latest_updated_at,
                                           steam_position=new_stream_position)
            response = self.request(body)
            if response.status_code == 200:
                new_stream_position, remaining_count, leads = get_multiple_leads.unwrap(response)
                remaining_count = int(remaining_count)
                if file_stream is not None:
                    for lead in leads:
                        file_stream.write(json.dumps(lead.to_dict()) + "\n")
                else:
                    all_leads.extend(leads)
                number_of_fetched_leads += len(leads)
            else:
                self.handle_error(response)
        if file_stream is not None:
            file_stream.flush()
            return file_stream, number_of_fetched_leads
        return all_leads, number_of_fetched_leads

    def get_lead(self, email=None):

        if not email or not isinstance(email, str):
            raise ValueError('Must supply an email as a non empty string.')

        body = get_lead.wrap(email)
        response = self.request(body)
        if response.status_code == 200:
            return get_lead.unwrap(response)
        else:
            self.handle_error(response)

    def get_lead_activity(self, email=None, filters=[]):

        if not email or not isinstance(email, str):
            raise ValueError('Must supply an email as a non empty string.')

        body = get_lead_activity.wrap(email, filters)
        response = self.request(body)
        if response.status_code == 200:
            return get_lead_activity.unwrap(response)
        else:
            self.handle_error(response)

    def request_campaign(self, campaign=None, lead=None):

        if not campaign or not isinstance(campaign, str):
            raise ValueError('Must supply campaign id as a non empty string.')

        if not lead or not isinstance(lead, str):
            raise ValueError('Must supply lead id as a non empty string.')

        body = request_campaign.wrap(campaign, lead)

        response = self.request(body)
        if response.status_code == 200:
            return True
        else:
            self.handle_error(response)

    def sync_lead(self, email=None, attributes=None):

        if not email or not isinstance(email, str):
            raise ValueError('Must supply lead id as a non empty string.')

        if not attributes or not isinstance(attributes, tuple):
            raise ValueError('Must supply attributes as a non empty tuple.')

        body = sync_lead.wrap(email, attributes)

        response = self.request(body)
        if response.status_code == 200:
            return sync_lead.unwrap(response)
        else:
            self.handle_error(response)
