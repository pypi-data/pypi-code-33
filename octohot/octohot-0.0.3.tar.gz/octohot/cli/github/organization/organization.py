import click

from octohot.cli.config import config

try:
    ORG = config['github_organization']
except:
    ORG = None

@click.group()
@click.option('--name', '-n', default=None)
def org(name=None):
    """Organization from GitHub provider"""
    global ORG

    if name:
        ORG = name
    else:
        if not ORG:
            raise Exception("Missing organization")


from octohot.cli.github.organization.org_import import organization_import
org.add_command(organization_import)

from octohot.cli.github.organization.list import list
org.add_command(list)


def url_list(url_type):
    from github3 import GitHub
    from octohot.cli.github.github import GITHUB_TOKEN
    github = GitHub()
    github.login(token=GITHUB_TOKEN)
    org = github.organization(ORG)
    repos = org.repositories()
    if url_type == 'https':
        urls = [repo.clone_url for repo in repos]
    else:
        urls = [repo.ssh_url for repo in repos]
    return urls

