import click

from octohot.cli.config import config

try:
    GITHUB_TOKEN = config['github_token']
except:
    GITHUB_TOKEN = None

@click.group()
@click.option('--token', '-t')
def github(token=None):
    """GitHub provider for octohot"""
    global GITHUB_TOKEN
    if token:
        GITHUB_TOKEN = token
    else:
        if not GITHUB_TOKEN:
            raise Exception("Missing token")


from octohot.cli.github.pr import pr
github.add_command(pr)

from octohot.cli.github.organization.organization import org
github.add_command(org)

