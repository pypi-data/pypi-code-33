import mock
import pytest
from bitbucket.repos import BitbucketRepos


class TestBitbucketRepos:
    @mock.patch('bitbucket.service.BitbucketService.get')
    @mock.patch('bitbucket.service.KatkaProject.objects')
    def test_set_api_path(self, mock_db_katka_project, mock_get_request):
        repos_service = BitbucketRepos(katka_project_id='wonder_woman', project_id='the_wasp')
        repos_service.get_repos()

        assert repos_service.path == 'projects/the_wasp/repos'

    def test_empty_project_id(self):
        with pytest.raises(ValueError):
            BitbucketRepos(katka_project_id='wonder_woman').path
