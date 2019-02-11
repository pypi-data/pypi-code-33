import click


@click.command()
@click.argument('pr_title')
@click.argument('pr_comment')
@click.argument('branch_name')
def pr(pr_title, pr_comment, branch_name):
    from octohot.cli.config import repositories
    for repo in repositories:
        if repo.is_github() and repo.is_current_branch(branch_name):
            _pr(repo, pr_title, pr_comment, branch_name)


def _pr(repo, pr_title, pr_comment, branch_name):
    from github3 import GitHub
    from octohot.cli.github.github import GITHUB_TOKEN
    github = GitHub()
    github.login(token=GITHUB_TOKEN)
    github_repo = github.repository(repo.owner, repo.name)
    github_repo.create_pull(pr_title, 'master', branch_name, pr_comment)
    click.echo(f"PR github repo {repo.name} PR {pr_title} branch {branch_name}")
