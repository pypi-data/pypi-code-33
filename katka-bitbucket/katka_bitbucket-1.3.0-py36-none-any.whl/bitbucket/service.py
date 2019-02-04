import logging

from django.conf import settings

import requests
from bitbucket.models import KatkaProject
from dataclasses import dataclass

log = logging.getLogger(__name__)


@dataclass
class BitbucketService:
    katka_project_id: str
    start: int = None
    limit: int = None

    def __post_init__(self):
        """
        Raises:
            bitbucket.models.KatkaProject.DoesNotExist: in case the given id for the katka project does not exist
        """
        self._katka_project = KatkaProject.objects.get(project_id=self.katka_project_id)

        if not self._katka_project.oauth_access_token:
            log.debug(f'No access token found for katka project {self.katka_project_id}')

        self.base_path = 'rest/api/1.0'
        self.path = ''

    @property
    def client(self) -> requests.sessions.Session:
        session = requests.Session()
        session.headers.update({
            'Authorization': f'Bearer {self._katka_project.oauth_access_token}',
            'Accept': 'application/json',
            'User-Agent': 'katka'
        })
        return session

    def get(self, params: dict = None) -> dict:
        '''
        Args:
            params(dict): the params for query string

        Returns:
            dict: the http response body

        Raises:
            requests.exceptions.HTTPError: in case there is a HTTP error during the request
        '''
        url = f'{self._katka_project.base_url}/{self.base_path}/{self.path}'
        params = params or {}
        if self.start is not None:
            params['start'] = self.start
        if self.limit is not None:
            params['limit'] = self.limit

        resp = self.client.get(url, params=params, verify=settings.REQUESTS_CA_BUNDLE)
        resp.raise_for_status()
        return resp.json()
