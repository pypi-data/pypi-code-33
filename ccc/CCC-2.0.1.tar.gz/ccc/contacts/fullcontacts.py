# -*- coding: utf-8 -*-
import json
from logging import getLogger

import requests
from django.conf import settings

log = getLogger(__name__)


class FullContacts(object):
    """Get Full contacts from email and organization name"""

    def __init__(self, *args, **kwargs):
        self.person_url = 'https://api.fullcontact.com/v3/person.enrich'
        self.domain_url = 'https://api.fullcontact.com/v3/company.enrich'
        self.headers = {'Authorization': 'Bearer {}'.format(settings.FULLCONTACT_API_KEY)}

    def get_social_profile_by_email(self, email):
        """Get social profile by email address
        args:
            email: Email address
        return:
            json: return json data for email
        """
        log.info("FullContacts for person by email: {}".format(email))
        response = requests.post(self.person_url, data=json.dumps({"email": email}), headers=self.headers)
        if response.status_code == 200:
            log.info("Successfully fetch FullContacts for person by email: {}".format(email))
            return response.json()
        log.error("Unable to fetch FullContacts for person by email: {}, error: {}".format(email, response.content))

    def get_social_profile_by_domain(self, domain):
        """Get social profile by domain name
        args:
            domain: Domain address ex "google.com"
        return:
            json: return json data for domain
        """
        log.info("FullContacts for organization by domain: {}".format(domain))
        response = requests.post(self.domain_url, data=json.dumps({"domain": domain}), headers=self.headers)
        if response.status_code == 200:
            log.info("Successfully fetch FullContacts for organization by domain: {}".format(domain))
            return response.json()
        log.error("Unable to fetch FullContacts for organization by domain: {}, error: {}".format(domain, response.content))
