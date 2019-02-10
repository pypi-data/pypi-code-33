import glob

import click

from github import Github


class GithubRelease(object):
    def __init__(self, github):
        self.github = github


@click.group()
@click.option(
    '--token',
    help='GitHub API token.',
    envvar='TOKEN',
    show_envvar=True,
    required=True,
)
@click.option(
    '--repo',
    help='GitHub repository name.',
    envvar='REPO',
    show_envvar=True,
    required=True,
)
@click.version_option()
@click.pass_context
def cli(ctx, token, repo):
    """Manage GitHub releases."""

    ctx.obj = Github(token).get_user().get_repo(repo)


@cli.command()
@click.option(
    '--tag',
    help='Release tag.',
    envvar='TAG',
    show_envvar=True,
    required=True,
)
@click.option(
    '--name',
    help='Release name.',
    envvar='NAME',
    show_envvar=True,
)
@click.option(
    '--message',
    help='Release message.',
    envvar='MESSAGE',
    show_envvar=True,
    required=True,
)
@click.option(
    '--draft/--no-draft',
    help='Release is a draft.',
    envvar='DRAFT',
    show_envvar=True,
    default=False,
)
@click.option(
    '--prerelease/--no-prelease',
    help='Release is a prerelease.',
    envvar='PRERELEASE',
    show_envvar=True,
    default=False,
)
@click.option(
    '--target',
    help='Release commit target.',
    envvar='TARGET',
    show_envvar=True,
)
@click.option(
    '--assets',
    help='Release assets to upload.',
    envvar='ASSETS',
    show_envvar=True,
)
@click.pass_obj
def create(repo, tag, name, message, draft, prerelease, target, assets):
    """Create release."""

    if not name:
        name = tag

    release = repo.create_git_release(
        tag=tag,
        name=tag,
        message=message,
        target_commitish=target,
        prerelease=prerelease,
    )

    for item in glob.glob(assets):
        release.upload_asset(item)


def main():
    cli(
        auto_envvar_prefix='GITHUB_RELEASE_CICD',
        prog_name='github_release_cicd',
    )
