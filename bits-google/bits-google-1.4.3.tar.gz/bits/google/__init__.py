"""Google class file."""

import argparse
import re

import google.auth

from httplib2 import Http
from google.oauth2 import service_account

# used for auth_stored_credentials
from oauth2client import client, tools
from oauth2client.file import Storage as FileStorage
from oauth2client.service_account import ServiceAccountCredentials

# bits-google service subclasses
from services.bigquery import BigQuery
from services.billing import CloudBilling
from services.cai import CloudAssetInventory
from services.calendar import Calendar
from services.compute import Compute
from services.crm import CloudResourceManager
from services.datastore import Datastore
from services.directory import Directory
from services.dns import CloudDNS
from services.drive import Drive
from services.gmail import Gmail
from services.groupssettings import GroupsSettings
from services.iam import IAM
from services.labelmanager import LabelManager
from services.licensing import Licensing
from services.people import People
from services.reports import Reports
from services.resourcesearch import ResourceSearch
from services.sheets import Sheets
from services.sql import SQL
from services.storage import Storage
from services.vault import Vault


class Google(object):
    """Google class definition."""

    def __init__(
        self,
        access_token=None,
        api_key=None,
        app_name=None,
        client_scopes=None,
        client_secrets_file='client_secrets.json',
        credentials_file='credentials.json',
        private_key_password='notasecret',
        redirect_uri='urn:ietf:wg:oauth:2.0:oob',
        scopes=[],
        service_account_email=None,
        service_account_file='service_account.json',
        subject=None,
        verbose=False,
    ):
        """Initialize a class instance."""
        # token authentication
        self.access_token = access_token

        # developer key authentication
        self.api_key = api_key

        # client secrets oauth2 authentication flow
        self.app_name = app_name
        self.client_secrets_file = client_secrets_file
        self.client_scopes = client_scopes
        self.credentials_file = credentials_file
        self.redirect_uri = redirect_uri

        # service account scopes
        self.scopes = scopes

        # service account authentication (json/p12)
        self.service_account_file = service_account_file
        self.subject = subject

        # service account authentication (p12)
        self.private_key_password = private_key_password
        self.service_account_email = service_account_email

        # enable verbose output
        self.verbose = verbose

        # authorized credentials
        self.credentials = None
        self.http = None

        # project ID
        self.project_id = None

    #
    # Authentication functions
    #
    def auth_google_credentials(self, scopes=None):
        """Authorize application default credentials."""
        credentials, project_id = google.auth.default(scopes=scopes)
        self.credentials = credentials
        self.project_id = project_id
        return credentials

    def auth_service_account_json(self, scopes, subject=None):
        """Authorize service account json file."""
        credentials = service_account.Credentials.from_service_account_file(
            self.service_account_file
        )
        if scopes:
            credentials = credentials.with_scopes(scopes)
        if subject:
            credentials = credentials.with_subject(subject)
        # store credentials
        self.credentials = credentials
        return credentials

    def auth_service_account_p12(self, scopes, subject=None):
        """Authorize service account p12 file."""
        # need to remove support for p12 accounts because of dependency
        # on oauth2client
        credentials = ServiceAccountCredentials.from_p12_keyfile(
            self.service_account_email,
            self.service_account_file,
            self.private_key_password,
            scopes,
        )
        if subject:
            credentials = credentials.create_scoped(subject)
        # store credentials
        self.credentials = credentials
        return credentials

    def auth_service_account(self, scopes=[], subject=None):
        """Authorize service account."""
        if not scopes:
            scopes = self.scopes
        if isinstance(scopes, str):
            scopes = [scopes]
        # need to remove support for p12 in a future version because
        # of dependency on oauth2client
        if re.search('.p12$', self.service_account_file):
            return self.auth_service_account_p12(scopes, subject)
        elif re.search('.json$', self.service_account_file):
            return self.auth_service_account_json(scopes, subject)

    def auth_stored_credentials(self, scopes=[]):
        """Authorize stored credentials."""
        # this has a dependency on oauth2client
        if not scopes:
            scopes = self.client_scopes
        try:
            parser = argparse.ArgumentParser(parents=[tools.argparser])
            parser.add_argument('args', nargs=argparse.REMAINDER)
            flags = parser.parse_args()
            flags.noauth_local_webserver = True
        except ImportError:
            flags = None
        # retrieve stored credentials, if they exist
        store = FileStorage(self.credentials_file)
        credentials = store.get()
        # create stored credentials
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(
                self.client_secrets_file,
                scopes,
            )
            flow.user_agent = self.app_name
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            if self.verbose:
                print('Saved credentials to %s' % (self.credentials_file))
        # authorize an Http instance
        self.http = credentials.authorize(Http())
        # store credentials
        self.credentials = credentials
        return credentials

    def get_auth_token(self, credentials):
        """Return an auth token from Google credentials."""
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        return credentials.token

    #
    # Sub-class functions
    #
    def bigquery(self):
        """Return the BigQuery class."""
        return BigQuery(self.credentials)

    def billing(self):
        """Return the CloudBilling class."""
        return CloudBilling(self.credentials, self.api_key)

    def cai(self):
        """Return the CloudAssetInventory class."""
        return CloudAssetInventory(self.credentials)

    def calendar(self):
        """Return the Calendar class."""
        return Calendar(self.credentials)

    def compute(self):
        """Return the Compute class."""
        return Compute(self.credentials)

    def crm(self):
        """Return the CloudResourceManager class."""
        return CloudResourceManager(self.credentials)

    def datastore(self, project):
        """Return the Datastore class."""
        return Datastore(project, self.credentials)

    def directory(self):
        """Return the Directory class."""
        return Directory(self.credentials)

    def dns(self):
        """Return the CloudDNS class."""
        return CloudDNS(self.credentials)

    def drive(self):
        """Return the Drive class."""
        return Drive(self.credentials)

    def gmail(self):
        """Return the Gmail class."""
        return Gmail(self.credentials)

    def groupssettings(self):
        """Return the GroupsSettings class."""
        return GroupsSettings(self.credentials)

    def iam(self):
        """Return the IAM class."""
        return IAM(self.credentials)

    def labelmanager(self):
        """Return the LabelManager class."""
        return LabelManager(self.credentials, self.api_key)

    def licensing(self):
        """Return the Licensing class."""
        return Licensing(self.http)

    def people(self):
        """Return the People class."""
        return People(self.credentials)

    def reports(self):
        """Return the Reports class."""
        return Reports(self.credentials)

    def resourcesearch(self):
        """Return the ResourceSearch class."""
        return ResourceSearch(self.credentials)

    def sheets(self):
        """Return the Sheets class."""
        return Sheets(self.credentials)

    def sql(self):
        """Return the SQL class."""
        return SQL(self.credentials)

    def storage(self):
        """Return the Storage class."""
        return Storage(self.credentials)

    def vault(self):
        """Return the Vault class."""
        return Vault(self.credentials)
