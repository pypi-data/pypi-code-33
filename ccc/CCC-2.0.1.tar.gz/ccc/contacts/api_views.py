import json

import requests
from django.conf import settings
from django.db.models import Q
from django.urls import reverse
from requests_oauthlib import OAuth1Session
from rest_framework import status, viewsets
from rest_framework.generics import (GenericAPIView, ListAPIView,
                                     get_object_or_404)
from rest_framework.response import Response

from ccc.campaigns.models import Campaign
from ccc.contacts.models import Contact, ContactGroup
from ccc.contacts.serializers import ContactSerializer


class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    model = Contact

    def get_queryset(self):
        return self.request.user.contact_set.all()

    def pre_save(self, obj):
        obj.user = self.request.user
        obj.lead_type = '5'  # card scan


class ContactsForCampaignView(ListAPIView):
    serializer_class = ContactSerializer

    def get_queryset(self):
        # prevent from getting Contact info for another account
        campaign = get_object_or_404(Campaign, user=self.request.user,
                                     pk=self.kwargs['campaign_id'])
        q = self.request.query_params.get('q', None)
        query = Q()
        if q:
            words = q.split()
            for word in words:
                query |= Q(first_name__icontains=word) | \
                         Q(last_name__icontains=word) | \
                         Q(email__icontains=word)

        return campaign.contact_set.filter(query).distinct()


def parse_google_entries(data):
    contacts = []

    for entry in data['feed']['entry']:
        email = None
        gd_email = entry.get('gd$email', [])
        if len(gd_email):
            email = gd_email[0].get('address', None)

        phone = None
        gd_phoneNumber = entry.get('gd$phoneNumber', [])
        if len(gd_phoneNumber):
            phone = gd_phoneNumber[0]['$t']

        first_name = None
        last_name = None
        if entry.get('gd$name') and 'gd$givenName' in entry['gd$name'] and 'gd$familyName' in entry['gd$name']:
            first_name = entry['gd$name']['gd$givenName']['$t']
            last_name = entry['gd$name']['gd$familyName']['$t']

        if (first_name and last_name) and (email or phone):
            contacts.append({
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone': phone
            })

    return contacts


def parse_outlook_entries(data):
    contacts = []

    for entry in data['value']:

        email = None
        email_addresses = entry.get('EmailAddresses')
        if email_addresses:
            email = email_addresses[0].get('Address')

        phone = entry.get('MobilePhone1')
        if not phone:
            other_phones = entry.get('HomePhones', []) + entry.get('BusinessPhones', [])
            if other_phones:
                phone = other_phones[0]

        first_name = entry.get('GivenName')
        last_name = entry.get('Surname')

        if (first_name and last_name) and (email or phone):
            contacts.append({
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone': phone
            })

    return contacts


TOKEN_URL = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
CONTACTS_API_URL = 'https://outlook.office.com/api/v2.0/me/contacts/?$top=100'


class AccessTokenException(Exception):
    pass


class ContactImportView(GenericAPIView):
    def get_access_token(self):
        raise NotImplementedError()

    def fetch_raw_contacts(self):
        raise NotImplementedError()

    def post(self, request, *args, **kwargs):
        self.campaigns = Campaign.object.filter(user=self.request.user,
                                                pk__in=request.data.getlist('campaigns', []))
        self.groups = ContactGroup.object.filter(user=self.request.user,
                                                 pk__in=request.data.getlist('groups', []))
        try:
            self.token = self.get_access_token()
        except AccessTokenException as e:
            return Response({'error': json.loads(e.message)},
                            status=status.HTTP_400_BAD_REQUEST)

        raw_contacts = self.fetch_raw_contacts()
        return self.save_contacts(raw_contacts)

    def save_contacts(self, raw_contacts):
        num_created = 0
        for c in raw_contacts:
            contact, created = Contact.match_or_create(c['email'], c['phone'], self.request.user)
            if not contact.first_name:
                contact.first_name = c['first_name']
            if not contact.last_name:
                contact.last_name = c['last_name']

            contact.save()

            if created:
                num_created += 1

            for campaign in self.campaigns:
                contact.campaigns.add(campaign)

            for group in self.groups:
                group.contacts.add(contact)

        return Response({
            'total_contacts': len(raw_contacts),
            'new_contacts': num_created,
        }, status=status.HTTP_201_CREATED)


class GoogleImportView(ContactImportView):

    def get_access_token(self):
        return self.request.data.get('access_token')

    def fetch_raw_contacts(self):
        raw_contacts = []

        next_url = 'https://www.google.com/m8/feeds/contacts/default/thin?alt=json&access_token=%s&max-results=500&v=3.0' % self.token
        while next_url:
            data = requests.get(next_url).json()
            raw_contacts += parse_google_entries(data)

            next = filter(lambda x: x['rel'] == 'next', data['feed']['link'])
            if next:
                next_url = next[0]['href'] + '&access_token=%s' % self.token
            else:
                next_url = None

        return raw_contacts


class OutlookImportView(ContactImportView):

    def get_access_token(self):
        code = self.request.data.get('code')

        redirect_uri = self.request.build_absolute_uri(reverse('outlook_connect'))

        resp = requests.post(TOKEN_URL, {
            'client_id': settings.MICROSOFT_CLIENT_ID,
            'client_secret': settings.MICROSOFT_CLIENT_SECRET,
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'})

        if resp.status_code == 200:
            return resp.json().get('access_token')
        else:
            raise AccessTokenException(resp.content)

    def fetch_raw_contacts(self):
        raw_contacts = []

        headers = {
            'Accept': 'application/json; odata.metadata=none',
            'Authorization': 'Bearer ' + self.token
        }
        next_url = CONTACTS_API_URL
        while next_url:
            data = requests.get(next_url, headers=headers).json()
            raw_contacts += parse_outlook_entries(data)

            next_url = data.get('@odata.nextLink', None)

        return raw_contacts


class YahooGetAuthUrlView(GenericAPIView):
    def get(self, request, *args, **kwargs):
        redirect_url = request.build_absolute_uri(reverse('yahoo_connect'))
        session = OAuth1Session(
            settings.YAHOO_CLIENT_ID,
            client_secret=settings.YAHOO_CLIENT_SECRET,
            callback_uri=redirect_url)

        request_token_url = 'https://api.login.yahoo.com/oauth/v2/get_request_token'
        data = session.fetch_request_token(request_token_url)
        auth_url = data['xoauth_request_auth_url']

        self.request.session['oauth_token'] = data['oauth_token']
        self.request.session['oauth_token_secret'] = data['oauth_token_secret']

        return Response({'auth_url': auth_url})


def parse_yahoo_entries(data):
    contacts = []

    for entry in data['contacts']['contact']:

        first_name = None
        last_name = None
        name_fields = filter(lambda x: x["type"] == "name", entry.get('fields', []))
        if name_fields:
            first_name = name_fields[0].get('value', {}).get('givenName', None)
            last_name = name_fields[0].get('value', {}).get('familyName', None)

        email = None
        email_fields = filter(lambda x: x["type"] == "email", entry.get('fields', []))
        if email_fields:
            email = email_fields[0].get('value', None)

        phone = None
        phone_fields = filter(lambda x: x["type"] == "phone", entry.get('fields', []))
        if phone_fields:
            phone = phone_fields[0].get('value', None)

        if (first_name and last_name) and (email or phone):
            contacts.append({
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone': phone
            })

    return contacts


class YahooAuthorizeView(ContactImportView):
    def get_access_token(self):
        return None

    def fetch_raw_contacts(self):
        oauth_token = self.request.session.get('oauth_token')
        oauth_token_secret = self.request.session.get('oauth_token_secret')

        del self.request.session['oauth_token']
        del self.request.session['oauth_token_secret']

        self.auh_session = OAuth1Session(settings.YAHOO_CLIENT_ID,
                                         client_secret=settings.YAHOO_CLIENT_SECRET,
                                         resource_owner_key=oauth_token,
                                         resource_owner_secret=oauth_token_secret)

        self.token_data = self.auh_session.fetch_access_token(
            'https://api.login.yahoo.com/oauth/v2/get_token',
            verifier=self.request.data.get('oauth_verifier'))

        raw_contacts = []

        start = 0
        page_size = 50
        url_base = 'https://social.yahooapis.com/v1/user/' + \
                   self.token_data['xoauth_yahoo_guid'] + '/contacts;start=%d;count=%d?format=json'
        next_url = url_base % (start, page_size)
        while next_url:
            data = self.auh_session.get(next_url).json()
            total = data['contacts']['total']
            count = data['contacts']['count']

            raw_contacts += parse_yahoo_entries(data)

            start += count
            if start < total:
                next_url = url_base % (start, page_size)
            else:
                next_url = None

        return raw_contacts
