import re

from github import Github, GithubException
from reliabilly.settings import Constants


def get_default_svn_client(token, baseurl=Constants.SOURCE_CONTROL_URL_DEFAULT):
    client = None
    try:
        # This accepts anything as creds and only throws errors on being used
        # A 404 would be valid while a 401 would not be?
        client = Github(base_url=baseurl, login_or_token=token)
    except GithubException as ex:
        print(ex)
        exit(False)

    return client


class SourceControlClient:
    def __init__(self, token, url=Constants.SOURCE_CONTROL_URL_DEFAULT, client=None):
        self.client = client
        if not self.client:
            self.client = get_default_svn_client(token, url)

    def get_organisation(self, org_name):
        try:
            return self.client.get_organization(org_name)
        except GithubException:
            return False

    def get_user(self, username):
        try:
            return self.client.get_user(username)
        except GithubException:
            return False

    def get_user_repository(self, username, repository_name):
        try:
            user = self.get_user(username)
            return user.get_repo(repository_name)
        except GithubException:
            return False

    def get_organisation_repository(self, org_name, repo_name):
        try:
            organisation = self.get_organisation(org_name)
            return organisation.get_repo(repo_name)
        except GithubException:
            return False

    def get_organisation_commit(self, org_name, repo_name, commit_sha):
        try:
            organisation = self.get_organisation(org_name)
            repo = organisation.get_repo(repo_name)
            return repo.get_commit(commit_sha)
        except GithubException:
            return False

    def get_organisation_pull_request(self, org_name, repo_name, number):
        try:
            organisation = self.get_organisation(org_name)
            repo = organisation.get_repo(repo_name)
            return repo.get_pull(int(number))
        except GithubException:
            return False

    def get_pr_for_commit(self, org_name, repo_name, commit_sha):
        commit = self.get_organisation_commit(org_name, repo_name, commit_sha)
        message = commit.commit.message
        if '#' not in message:
            return False
        match = re.search(r"#([0-9]+)", message)
        if match is None:
            return False
        return int(match.group(1))

    def get_origin_pr(self, org_name, repo_name, commit_sha):
        pr_number = self.get_pr_for_commit(org_name, repo_name, commit_sha)
        if not pr_number:
            return False
        pull_request = self.get_organisation_pull_request(org_name, repo_name, pr_number)
        if not pull_request:
            return False
        return pull_request

    def create_release(self, job_name, jira_num, jira_url, version):
        try:
            owner = job_name.split("/")[0]
            repo = job_name.split("/")[1]
            org_repo = self.get_organisation_repository(owner, repo)
            message = f"[{jira_num}]({jira_url}/browse/{jira_num})"
            return org_repo.create_git_release(tag=version, name=version, message=message)
        except GithubException:
            return False
