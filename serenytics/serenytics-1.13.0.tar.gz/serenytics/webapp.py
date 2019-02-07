import base64
import json
import logging

from .helpers import make_request, SerenyticsException
from . import settings

logger = logging.getLogger(__name__)


class UnknownWebApp(SerenyticsException):
    def __init__(self, uuid_or_name):
        super(UnknownWebApp, self).__init__(u'Webapp with uuid or name "{}" does not exist'.format(uuid_or_name))


class WebApp(object):
    """
    Serenytics web app (dashboard)
    """

    def __init__(self, config, client):
        self._config = config
        self._client = client
        self._headers = client._headers

    @property
    def name(self):
        return self._config['name']

    @property
    def uuid(self):
        return self._config['uuid']

    def set_custom_css(self, css):
        """
        Apply given `css` to the web app.
        """
        self._config['jsonContent']['cssContent'] = css

    def set_custom_html_header(self, html):
        """
        Apply the given html header to the web app instead of just using the name by default.
        """
        self._config['jsonContent']['headerMode'] = 'custom_html'
        self._config['jsonContent']['htmlHeader'] = html

    def save(self):
        make_request('PUT', settings.SERENYTICS_API_DOMAIN + '/api/web_app/' + self.uuid,
                     data=json.dumps(self._config),
                     headers=self._headers)

    def warm_up_cache(self, payload=None, tabs_options=None):
        """
        Warm up Serenytics data cache for this dashboard.

        :param payload: dict to configure template dashboard. See
            https://doc.serenytics.com/developer/template_dashboards/ for more details.
        :param tabs_options: list of tabs options used to warm up cache of given tabs with specified dynfilters
        configurations.

        For instance:
            tabs_options=[
                {
                    'tabIndex': 't034a7b13042b529c',
                    # id: widget id
                    # values: dict of list of values for each dynfilter (uuid) of the specified widget
                    'dynfilters': [{'id': 2, 'values': {'2642b931c33373c1': ['France']}}]
                },
                {
                    'tabIndex': 't034a7b13042b529c',
                    'dynfilters': [{'id': 2, 'values': {'2642b931c33373c1': ['USA']}}]
                },
            ]
        """
        query_string = None
        if payload:
            if not isinstance(payload, dict):
                raise SerenyticsException('payload must be a dict')
            query_string = {
                'embeddedPayload': base64.b64encode(json.dumps(payload).encode('utf-8')).decode('utf-8')
            }

        response = make_request('post', settings.SERENYTICS_API_DOMAIN + '/api/web_app/' + self.uuid + '/generate_pdf',
                                headers=self._headers,
                                data=json.dumps({
                                    'store_pdf': False,
                                    'webapp_query_string': query_string,
                                    'tabs_options': tabs_options
                                }))
        stdout = response.json().get('stdout', [])
        return stdout

    def get_list_of_data_sources(self):
        """
        Retrieve the list of the data sources used in this dashboard.
        Each item in the list is a dict containing the uuid and the name of the data source.
        """
        response = make_request('get', settings.SERENYTICS_API_DOMAIN + '/api/web_app/' + self.uuid + '/data_sources',
                                headers=self._headers).json()
        if response['status'] == 'error':
            raise SerenyticsException(response['errors'][0])
        return response['objects']
