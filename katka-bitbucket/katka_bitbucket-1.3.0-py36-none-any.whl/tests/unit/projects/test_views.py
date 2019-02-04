from django.urls import reverse

import mock
from bitbucket.exceptions import BadRequestAPIException, ProjectNotFoundAPIException
from bitbucket.models import KatkaProject
from requests import HTTPError, Response


class TestGetBitbucketProjectsView:
    @mock.patch('bitbucket.views.BitbucketProjects')
    def test_get_existing_projects(self, mock_bitbucket_projects, client):
        result = mock.Mock()
        result.get_projects.return_value = {
            'values': [
                {'name': 'super_man', 'key': 'SM'},
                {'name': 'batman', 'slug': 'BAT'},
            ]
        }
        mock_bitbucket_projects.return_value = result

        endpoint = reverse('projects')
        response = client.get(
            endpoint,
            content_type='application/json',
            data={
                'katka_project_id': 'bead677e-c414-4954-85eb-67ef09ca99f7',
                'limit': 10, 'start': 2, 'permission': 'PROJECT_READ'
            }
        )

        assert response.status_code == 200
        assert len(response.data['values']) == 2

    @mock.patch('bitbucket.views.BitbucketProjects')
    def test_get_empty_projects_list(self, mock_bitbucket_projects, client):
        result = mock.Mock()
        result.get_projects.return_value = {
            'values': []
        }
        mock_bitbucket_projects.return_value = result

        endpoint = reverse('projects')
        response = client.get(
            endpoint,
            content_type='application/json',
            data={'katka_project_id': 'bead677e-c414-4954-85eb-67ef09ca99f7', 'limit': 10, 'start': 2}
        )

        assert response.status_code == 200
        assert len(response.data['values']) == 0

    @mock.patch('bitbucket.views.BitbucketProjects')
    def test_katka_project_not_found(self, mock_bitbucket_projects, client):
        result = mock.Mock()
        result.get_projects.side_effect = KatkaProject.DoesNotExist
        mock_bitbucket_projects.return_value = result

        endpoint = reverse('projects')
        response = client.get(
            endpoint,
            content_type='application/json',
            data={'katka_project_id': 'bead677e-c414-4954-85eb-67ef09ca99f7'}
        )

        assert response.status_code == 404
        assert str(response.data['detail']) == ProjectNotFoundAPIException.default_detail

    @mock.patch('bitbucket.views.BitbucketProjects')
    def test_project_http_error_no_error_message(self, mock_bitbucket_projects, client):
        result = mock.Mock()
        response = Response()
        response.status_code = 400
        result.get_projects.side_effect = HTTPError(response=response)
        mock_bitbucket_projects.return_value = result

        endpoint = reverse('projects')
        response = client.get(
            endpoint,
            content_type='application/json',
            data={'katka_project_id': 'bead677e-c414-4954-85eb-67ef09ca99f7'}
        )

        assert response.status_code == 400
        assert str(response.data['detail']) == BadRequestAPIException.default_detail
