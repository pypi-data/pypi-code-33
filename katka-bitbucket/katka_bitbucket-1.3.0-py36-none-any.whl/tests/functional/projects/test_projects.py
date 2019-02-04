from django.urls import reverse

import mock
import pytest


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures('load_db_fixture')
@pytest.mark.parametrize(
    'load_db_fixture', [{'fixture_filename': 'katka_project.json'}], indirect=True)
@mock.patch('requests.sessions.Session.request')
class TestGetProjects:
    def test_existing_projects(self, mock_request, load_db_fixture, load_json_fixture, client):
        response = mock.Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = load_json_fixture('bitbucket_projects.json')
        mock_request.return_value = response

        endpoint = reverse('projects')
        response = client.get(
            endpoint,
            content_type='application/json',
            data={'katka_project_id': '4cb432f5-0def-48b6-ad05-f1c082b1f1b8', 'limit': 10, 'start': 2}
        )

        assert len(response.data['values']) == 2
        assert response.data['start'] == 0
        assert response.data['limit'] == 2
        assert response.data['size'] == 2
        assert response.data['isLastPage'] is False
        assert response.data['nextPageStart'] == 2
        assert response.data['values'][0]['key'] == 'MSAP'
        assert response.data['values'][0]['description'] == 'My super awesome project'
        assert response.data['values'][1]['name'] == 'Not so awesome project'

    def test_no_projects(self, mock_request, load_db_fixture, load_json_fixture, client):
        response = mock.Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = load_json_fixture('bitbucket_no_projects.json')
        mock_request.return_value = response

        endpoint = reverse('projects')
        response = client.get(
            endpoint,
            content_type='application/json',
            data={'katka_project_id': '4cb432f5-0def-48b6-ad05-f1c082b1f1b8', 'limit': 10, 'start': 2}
        )

        assert response.status_code == 200
        assert len(response.data['values']) == 0
        assert response.data['start'] == 0
        assert response.data['limit'] == 0
        assert response.data['size'] == 0
        assert response.data['isLastPage'] is True
        assert response.data['nextPageStart'] == 0

    def test_invalid_token(self, mock_request, load_db_fixture, load_json_fixture, client):
        """ If the token is not valid bitbucket will retrieve an empty list of projects """
        response = mock.Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = load_json_fixture('bitbucket_invalid_token.json')
        mock_request.return_value = response

        endpoint = reverse('projects')
        response = client.get(
            endpoint,
            content_type='application/json',
            data={'katka_project_id': '4cb432f5-0def-48b6-ad05-f1c082b1f1b9', 'limit': 10, 'start': 2}
        )

        assert response.status_code == 200
        assert len(response.data['values']) == 0
        assert response.data['start'] == 0
        assert response.data['limit'] == 0
        assert response.data['size'] == 0
        assert response.data['isLastPage'] is True
        assert response.data['nextPageStart'] == 0
