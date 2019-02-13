import click


@click.group()
def git():
    """git provider for octohot"""


from octohot.cli.git.clone import clone
git.add_command(clone)

from octohot.cli.git.add import add
git.add_command(add)


from octohot.cli.git.pull import pull
git.add_command(pull)

from octohot.cli.git.reset import reset
git.add_command(reset)

from octohot.cli.git.branch import branch
git.add_command(branch)

from octohot.cli.git.commit import commit
git.add_command(commit)

from octohot.cli.git.push import push
git.add_command(push)

from octohot.cli.git.diff import diff
git.add_command(diff)

if __name__ == '__main__':
    git()
