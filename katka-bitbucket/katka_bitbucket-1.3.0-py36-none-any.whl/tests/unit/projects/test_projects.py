import mock
import pytest
from bitbucket.projects import BitbucketProjects


class TestBitbucketProjects:
    @mock.patch('bitbucket.service.BitbucketService.get')
    @mock.patch('bitbucket.service.KatkaProject.objects')
    def test_set_api_path(self, mock_db_katka_project, mock_get_request):
        repos_service = BitbucketProjects(katka_project_id='wonder_woman', permission='TEST_PERMISSION')
        repos_service.get_projects()

        assert repos_service.path == 'projects'

    @pytest.mark.parametrize(
        'params, name, permission, expected_final_params',
        (
            ({}, None, None, {}),
            ({'name': 'some_name'}, None, None, {'name': 'some_name'}),
            (
                {
                    'name': 'not_this_name',
                    'permission': 'not_this_permission',
                    'limit': 1
                },  # params
                'this_name',  # name
                'this_permission',  # permission
                {
                    'name': 'this_name',
                    'permission': 'this_permission',
                    'limit': 1
                },  # expected_final_params
            )
        )
    )
    @mock.patch('bitbucket.service.BitbucketService.get')
    @mock.patch('bitbucket.service.KatkaProject.objects')
    def test_params(self, mock_db_katka_project, mock_get_request, params, name, permission, expected_final_params):
        repos_service = BitbucketProjects(katka_project_id='wonder_woman', permission=permission, name=name)
        repos_service.get_projects(params=params)

        mock_get_request.assert_called_once_with(params=expected_final_params)
