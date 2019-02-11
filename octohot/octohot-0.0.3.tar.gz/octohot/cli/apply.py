import click


@click.command()
@click.argument('branch_name')
@click.argument('commit_name')
@click.argument('commit_description')
@click.option('--pull_request', '-pr', is_flag=True, default=False)
def apply(branch_name, commit_name, commit_description, pull_request):
    """Pull, create branch, add, commit, push and make an optional PR"""
    from octohot.cli.config import repositories
    for repo in repositories:
        if repo.tainted():
            click.echo(repo.print("Apply (Pull, change branch, add files, "
                       "commit, push and make a optional PR)"))
            repo.pull()
            repo.branch(branch_name)
            repo.add()
            repo.commit(commit_name, commit_description)
            repo.push(branch_name)
            if pull_request and repo.is_github():
                from octohot.cli.github.pr import _pr
                _pr(repo, commit_name, commit_description, branch_name)
            repo.branch(repo.default_branch())

