import mock
import pytest
from bitbucket.models import KatkaProject
from bitbucket.service import BitbucketService
from requests import HTTPError


class TestBitbucketService:
    @pytest.mark.django_db(transaction=True)
    def test_project_not_found(self):
        with pytest.raises(KatkaProject.DoesNotExist):
            BitbucketService(katka_project_id='bead677e-c414-4954-85eb-67ef09ca99f7')

    @mock.patch('bitbucket.service.KatkaProject.objects')
    def test_no_access_token(self, mock_db_katka_project):
        mock_db_katka_project.get.return_value = mock.Mock(oauth_access_token=None)

        service = BitbucketService(katka_project_id='catwoman')

        assert service._katka_project.oauth_access_token is None

    @mock.patch('requests.sessions.Session.get')
    @mock.patch('bitbucket.service.KatkaProject.objects')
    def test_successful(self, mock_db_katka_project, mock_get_request, settings):
        result = mock.Mock()
        result.json.return_value = {'key', 'value'}
        mock_get_request.return_value = result
        mock_db_katka_project.get.return_value = mock.Mock(oauth_access_token='some_access_token')
        settings.REQUESTS_CA_BUNDLE = 'path_for_ca_bundle'

        bitbucket_service = BitbucketService(katka_project_id='wonder_woman')
        service_result = bitbucket_service.get(params={'key': 'value'})

        assert bitbucket_service.base_path
        assert not bitbucket_service.path
        assert bitbucket_service.client.headers['Authorization'] == 'Bearer some_access_token'

        assert service_result == {'key', 'value'}
        mock_get_request.assert_called_once_with(
            f'{mock_db_katka_project.get().base_url}/rest/api/1.0/',
            params={'key': 'value'}, verify='path_for_ca_bundle'
        )
        result.raise_for_status.assert_called_once()

    @mock.patch('requests.sessions.Session.get')
    @mock.patch('bitbucket.service.KatkaProject.objects')
    def test_http_error(self, mock_db_katka_project, mock_get_request, settings):
        mock_get_request.side_effect = HTTPError
        mock_db_katka_project.get.return_value = mock.Mock(oauth_access_token='some_access_token')
        settings.REQUESTS_CA_BUNDLE = 'path_for_ca_bundle'

        bitbucket_service = BitbucketService(katka_project_id='wonder_woman', limit=2, start=0)

        with pytest.raises(HTTPError):
            bitbucket_service.get()

        mock_get_request.assert_called_once_with(
            f'{mock_db_katka_project.get().base_url}/rest/api/1.0/',
            params={'limit': 2, 'start': 0}, verify='path_for_ca_bundle'
        )
