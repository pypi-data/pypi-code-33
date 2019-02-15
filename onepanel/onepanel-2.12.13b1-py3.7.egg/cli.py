""" Command line interface for the OnePanel Machine Learning platform

Entry point for command line interface.
"""


import os

import click

from onepanel.commands.common import clone, download, push, pull, background_dataset_push, timer_sync_output
from onepanel.utilities.original_connection import Connection

from onepanel.commands.datasets import datasets
from onepanel.commands.environments import environments
from onepanel.commands.instances import workspaces
from onepanel.commands.jobs import jobs
from onepanel.commands.login import login, login_with_token, logout
from onepanel.commands.machine_types import machine_types
from onepanel.commands.projects import projects
from onepanel.commands.volume_types import volume_types
from onepanel.constants import *
from onepanel.utilities.git_hook_utility import GitHookUtility
from onepanel.utilities.git_utility import CheckGitLfsInstalled


@click.group()
@click.version_option(version=CLI_VERSION, prog_name='Onepanel CLI')
@click.pass_context
def cli(ctx):
    conn = Connection()
    conn.load_credentials()
    utility = CheckGitLfsInstalled()

    ctx.obj['connection'] = conn
    ctx.obj['git_utility'] = utility
    utility.figure_out_git_installed()
    if utility.git_installed is False:
        print('Error. Cannot detect git, please verify git is installed.')
        exit(-1)


# Ensure that our git-hook to ping an end-point exits
# Are we in a OnePanel dataset (or project), and is the .git folder available in the current dir?
cwd = os.getcwd()
git_hook_utility = GitHookUtility()
if git_hook_utility.safe_to_add_git_hooks(cwd):
    if git_hook_utility.check_pre_push_gitlab_update_hook(cwd) is False:
        git_hook_utility.add_pre_push_gitlab_update_hook(cwd)
    if git_hook_utility.check_pre_commit_hook(cwd) is False:
        git_hook_utility.add_pre_commit_hook(cwd)

cli.add_command(login)
cli.add_command(login_with_token)
cli.add_command(logout)
cli.add_command(clone)
cli.add_command(download)
cli.add_command(push)
cli.add_command(pull)
cli.add_command(projects)
cli.add_command(datasets)
cli.add_command(background_dataset_push)
cli.add_command(jobs)
cli.add_command(machine_types)
cli.add_command(environments)
cli.add_command(volume_types)
cli.add_command(workspaces)
cli.add_command(timer_sync_output)


def main():
    return cli(obj={})


if __name__ == '__main__':
    cli(obj={})
