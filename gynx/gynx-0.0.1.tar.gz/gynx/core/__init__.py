#!/usr/bin/python2.7

from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from datetime import datetime
import pytz
import os

SCOPES = 'https://www.googleapis.com/auth/drive'

class Gynx():

    def __init__(self, quiet=False, debug=False, *args, **kwargs):
        '''
        Initialize by building Drive service with provided credentials.
        '''
        self.root = os.getcwd() + '/'
        self.appdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/'
        self.start = datetime.now().replace(tzinfo=pytz.UTC)
        self.quiet = quiet
        self.debug = debug
        creds = self.get_credentials()
        self.service = build('drive', 'v3', http=creds.authorize(Http()))

    def __str__(self):
        return 'gynx initialized at %s' % str(self.start)

    def get_credentials(self):
        '''
        Authenticate via user token combined with gynx app API credentials.
        Token generated initially after in-browser authorisation.
        '''
        store = file.Storage(self.appdir + 'credentials/token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(
                self.appdir + 'credentials/credentials.json',
                SCOPES
            )
            creds = tools.run_flow(flow, store)
        return creds

    def get_info(self):
        '''
        Information about the Drive user and library storage limits/usage.
        '''
        return self.service.about().get(fields='user, storageQuota').execute()

    def print_info(self):
        '''
        Print user information and calculate usage percentage.
        '''
        info = self.get_info()
        name = info['user']['displayName']
        print('Name:', name)
        usage = float(info['storageQuota']['usage'])
        print('Usage:', self.print_size(int(usage)))
        limit = float(info['storageQuota']['limit'])
        print('Limit:', self.print_size(int(limit)))
        used = float((usage/limit)*100)
        print('Used:', '{0:.2f}'.format(used) + '%')

    def print_size(self, bytes):
        '''
        Clean print file size in GB, MB, KB or B based on size
        '''
        if bytes >= 1000000000:
            return '{0:.2f}'.format(float(bytes)/1000000000.0) + ' GB'
        if bytes >= 1000000:
            return '{0:.2f}'.format(float(bytes)/1000000.0) + ' MB'
        if bytes >= 1000:
            return '{0:.2f}'.format(float(bytes)/1000.0) + ' KB'
        return str(bytes) + ' B'
