import unittest
from unittest.mock import MagicMock
from github import GithubException

from reliabilly.components.tools.source_control_client import SourceControlClient


class SourceControlClientTests(unittest.TestCase):  # pylint: disable=R0904

    def test_get_org(self):
        mock = MagicMock()
        mock_response = MagicMock()
        mock_response.email = "methodman@wutangfinancial.biz"
        mock.get_organization.return_value = mock_response
        client = SourceControlClient(mock, mock, mock)
        org = client.get_organisation("wu-tang-financial")
        self.assertEqual(org.email, "methodman@wutangfinancial.biz")

    def test_get_org_failure(self):
        mock = MagicMock()
        mock.get_organization.side_effect = GithubException(404, "Not Found")
        client = SourceControlClient(mock, mock, mock)
        org = client.get_organisation(123)
        self.assertFalse(org)

    def test_get_user(self):
        mock = MagicMock()
        mock_response = MagicMock()
        mock_response.name = "Test User"
        mock.get_user.return_value = mock_response
        client = SourceControlClient(mock, mock, mock)
        user = client.get_user("test-user")
        self.assertEqual(user.name, "Test User")

    def test_get_user_failure(self):
        mock = MagicMock()
        mock.get_user.side_effect = GithubException(404, "Not Found")
        client = SourceControlClient(mock, mock, mock)
        user = client.get_user("deleted-user")
        self.assertFalse(user)

    def test_get_user_repo(self):
        mock = MagicMock()
        mock_repo = MagicMock()
        mock_user = MagicMock()
        mock_repo.url = "https://ice-cold-world.net"
        mock_user.get_repo.return_value = mock_repo
        mock.get_user.return_value = mock_user
        client = SourceControlClient(mock, mock, mock)
        repo = client.get_user_repository("gza", "liquid-swords")
        self.assertEqual(repo.url, "https://ice-cold-world.net")

    def test_get_user_repo_failure(self):
        mock = MagicMock()
        mock_user = MagicMock()
        mock_user.get_repo.side_effect = GithubException(404, "Not Found")
        mock.get_user.return_value = mock_user
        client = SourceControlClient(mock, mock, mock)
        user_repo = client.get_user_repository("mf-doom", "mm.. food")
        self.assertFalse(user_repo)

    def test_get_org_repo(self):
        mock = MagicMock()
        mock_repo = MagicMock()
        mock_org = MagicMock()
        mock_repo.open_issues_count = 0
        mock_org.get_repo.return_value = mock_repo
        mock.get_organization.return_value = mock_org
        client = SourceControlClient(mock, mock, mock)
        org_repo = client.get_organisation_repository("tribe-called-quest", "midnight-marauders")
        self.assertEqual(org_repo.open_issues_count, 0)

    def test_get_org_repo_failure(self):
        mock = MagicMock()
        mock_org = MagicMock()
        mock_org.get_repo.side_effect = GithubException(404, "Not Found")
        mock.get_organization.return_value = mock_org
        client = SourceControlClient(mock, mock, mock)
        org_repo = client.get_organisation_repository("tribe-called-quest", "midnight-marauders")
        self.assertFalse(org_repo)

    def test_get_org_commit(self):
        mock = MagicMock()
        mock_commit = MagicMock()
        mock_repo = MagicMock()
        mock_org = MagicMock()
        commit_sha = "123shasha"
        mock_commit.sha = commit_sha
        mock_repo.get_commit.return_value = mock_commit
        mock_org.get_repo.return_value = mock_repo
        mock.get_organization.return_value = mock_org
        client = SourceControlClient(mock, mock, mock)
        org_commit = client.get_organisation_commit("tribe-called-quest", "midnight-marauders", commit_sha)
        self.assertEqual(org_commit.sha, commit_sha)

    def test_get_org_commit_fail(self):
        mock = MagicMock()
        mock_repo = MagicMock()
        mock_org = MagicMock()
        mock_repo.get_commit.side_effect = GithubException(404, "Not Found")
        mock_org.get_repo.return_value = mock_repo
        mock.get_organization.return_value = mock_org
        client = SourceControlClient(mock, mock, mock)
        org_commit = client.get_organisation_commit("tribe-called-quest", "midnight-marauders", "yahyah")
        self.assertFalse(org_commit)

    def test_get_org_pr(self):
        mock = MagicMock()
        mock_pr = MagicMock()
        mock_repo = MagicMock()
        mock_org = MagicMock()
        mock_pr.title = "did a thing"
        mock_repo.get_pull.return_value = mock_pr
        mock_org.get_repo.return_value = mock_repo
        mock.get_organization.return_value = mock_org
        client = SourceControlClient(mock, mock, mock)
        org_pr = client.get_organisation_pull_request("tribe-called-quest", "midnight-marauders", 123)
        self.assertEqual(org_pr.title, "did a thing")

    def test_get_org_pr_fail(self):
        mock = MagicMock()
        mock_repo = MagicMock()
        mock_org = MagicMock()
        mock_repo.get_pull.side_effect = GithubException(404, "Not Found")
        mock_org.get_repo.return_value = mock_repo
        mock.get_organization.return_value = mock_org
        client = SourceControlClient(mock, mock, mock)
        org_pr = client.get_organisation_pull_request("tribe-called-quest", "midnight-marauders", 123)
        self.assertFalse(org_pr)

    def test_get_pr_number_old_format(self):
        mock = MagicMock()
        mock_repo = MagicMock()
        mock_org = MagicMock()
        mock_commit = MagicMock()
        mock_commit.commit.message = 'Merge pull request #197 from test/master'
        mock_repo.get_commit.return_value = mock_commit
        mock_org.get_repo.return_value = mock_repo
        mock.get_organization.return_value = mock_org
        client = SourceControlClient(mock, mock, mock)
        og_pr_number = client.get_pr_for_commit('blah', 'bleh', 'bluh')
        self.assertEqual(og_pr_number, 197)

    def test_get_pr_number_new_format(self):
        mock = MagicMock()
        mock_repo = MagicMock()
        mock_org = MagicMock()
        mock_commit = MagicMock()
        mock_commit.commit.message = 'New PR format on github very cool (#123)'
        mock_repo.get_commit.return_value = mock_commit
        mock_org.get_repo.return_value = mock_repo
        mock.get_organization.return_value = mock_org
        client = SourceControlClient(mock, mock, mock)
        og_pr_number = client.get_pr_for_commit('blah', 'bleh', 'bluh')
        self.assertEqual(og_pr_number, 123)

    def test_get_pr_number_fail(self):
        mock = MagicMock()
        mock_repo = MagicMock()
        mock_org = MagicMock()
        mock_commit = MagicMock()
        mock_commit.commit.message = 'Not a pr title'
        mock_repo.get_commit.return_value = mock_commit
        mock_org.get_repo.return_value = mock_repo
        mock.get_organization.return_value = mock_org
        client = SourceControlClient(mock, mock, mock)
        og_pr_number = client.get_pr_for_commit('blah', 'bleh', 'bluh')
        self.assertFalse(og_pr_number)

    def test_get_pr_number_no_match(self):
        mock = MagicMock()
        mock_repo = MagicMock()
        mock_org = MagicMock()
        mock_commit = MagicMock()
        mock_commit.commit.message = 'New PR format on github very cool'
        mock_repo.get_commit.return_value = mock_commit
        mock_org.get_repo.return_value = mock_repo
        mock.get_organization.return_value = mock_org
        client = SourceControlClient(mock, mock, mock)
        og_pr_number = client.get_pr_for_commit('blah', 'bleh', 'bluh')
        self.assertFalse(og_pr_number)

    def test_get_origin_pr_old_format(self):
        mock = MagicMock()
        mock_repo = MagicMock()
        mock_org = MagicMock()
        mock_commit = MagicMock()
        mock_commit.commit.message = 'Merge pull request #197 from test/master'
        mock_repo.get_pull.return_value = 'a pr object'
        mock_repo.get_commit.return_value = mock_commit
        mock_org.get_repo.return_value = mock_repo
        mock.get_organization.return_value = mock_org
        client = SourceControlClient(mock, mock, mock)
        origin_pr = client.get_origin_pr('blah', 'bleh', 'shashasha')
        self.assertEqual(origin_pr, 'a pr object')

    def test_get_origin_pr_new_format(self):
        mock = MagicMock()
        mock_repo = MagicMock()
        mock_org = MagicMock()
        mock_commit = MagicMock()
        mock_commit.commit.message = 'New PR format on github very cool (#198)'
        mock_repo.get_pull.return_value = 'a pr object'
        mock_repo.get_commit.return_value = mock_commit
        mock_org.get_repo.return_value = mock_repo
        mock.get_organization.return_value = mock_org
        client = SourceControlClient(mock, mock, mock)
        origin_pr = client.get_origin_pr('blah', 'bleh', 'shashasha')
        self.assertEqual(origin_pr, 'a pr object')

    def test_get_origin_non_pr(self):
        mock = MagicMock()
        mock_repo = MagicMock()
        mock_org = MagicMock()
        mock_commit = MagicMock()
        mock_commit.commit.message = 'I am not pull request!'
        mock_org.get_repo.return_value = mock_repo
        mock.get_organization.return_value = mock_org
        client = SourceControlClient(mock, mock, mock)
        origin_pr = client.get_origin_pr('blah', 'bleh', 'shashasha')
        self.assertEqual(origin_pr, False)

    def test_get_origin_pr_fail(self):
        mock = MagicMock()
        mock_repo = MagicMock()
        mock_org = MagicMock()
        mock_commit = MagicMock()
        mock_commit.commit.message = 'I am not pull request!'
        mock_repo.get_pull.side_effect = GithubException(404, "Not Found")
        mock_org.get_repo.return_value = mock_repo
        mock.get_organization.return_value = mock_org
        client = SourceControlClient(mock, mock, mock)
        origin_pr = client.get_origin_pr('blah', 'bleh', 'shashasha')
        self.assertEqual(origin_pr, False)

    def test_create_release(self):
        mock = MagicMock()
        mock_org = MagicMock()
        mock_repo = MagicMock()
        mock_release = MagicMock()
        mock_release.body = '[ODB-420](http://dogs.com/browse/ODB-420)'
        mock_repo.create_git_release.return_value = mock_release
        mock_org.get_repo.return_value = mock_repo
        mock.get_organization.return_value = mock_org
        client = SourceControlClient(mock, mock, mock)
        release = client.create_release("marcus/platform", "ODB-420", "http://dogs.com", "1.0.0")
        expected = "[ODB-420](http://dogs.com/browse/ODB-420)"
        self.assertEqual(release.body, expected)

    def test_create_release_failure(self):
        mock = MagicMock()
        mock_org = MagicMock()
        mock_repo = MagicMock()
        mock_release = MagicMock()
        mock_release.body = '[ODB-420](http://dogs.com/browse/ODB-420)'
        mock_repo.create_git_release.side_effect = GithubException(422, "Validation Failed")
        mock_org.get_repo.return_value = mock_repo
        mock.get_organization.return_value = mock_org
        client = SourceControlClient(mock, mock, mock)
        release = client.create_release("marcus/platform", "ODB-420", "http://dogs.com", "1.0.0")
        self.assertFalse(release)
