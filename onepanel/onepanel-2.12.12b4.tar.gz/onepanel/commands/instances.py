"""
Workspace module
"""
import os
import re
import sys

import click
import configobj

from onepanel.commands.base import APIViewController
from onepanel.commands.login import login_required
from onepanel.commands.projects import ProjectViewController


class InstanceViewController(APIViewController):

    account_uid = None
    uid = None

    def __init__(self, conn):
        APIViewController.__init__(self, conn)


    def init_credentials_retrieval(self):
        home = os.getcwd()
        project_file = os.path.join(home, ProjectViewController.PROJECT_FILE)
        cfg = configobj.ConfigObj(project_file)

        if len(cfg) == 0:
            print("ERROR.Cannot figure out the current project.")
            print("Make sure .onepanel/project exists and is accurate.")
            exit(-1)
        self.account_uid = cfg['account_uid']
        self.uid = cfg['uid']

    def init_endpoint(self):
        self.endpoint = '{root}/accounts/{account_uid}/projects/{project_uid}/instances'.format(
            root=self.conn.URL,
            account_uid=self.account_uid,
            project_uid=self.uid
        )

@click.group(help='Workspace commands group')
@click.pass_context
def workspaces(ctx):
    ctx.obj['vc'] = InstanceViewController(ctx.obj['connection'])


@workspaces.command(
    'create',
    help='Create a new workspace. The workspace\'s name: Max 25 chars, lower case alphanumeric or "-", '
         'must start and end with alphanumeric'
)
@click.argument(
    'workspace_uid',
    type=str
)
@click.option(
    '-m', '--machine-type',
    type=str,
    required=True,
    help='Machine type ID. Call "onepanel machine_types list" for IDs.'
)
@click.option(
    '-e', '--environment',
    type=str,
    required=True,
    help='Instance template ID. Call "onepanel environments list" for IDs.'
)
@click.option(
    '-s', '--storage',
    type=str,
    required=True,
    help='Storage type ID.'
)
@click.pass_context
@login_required
def create_instance(ctx, workspace_uid, machine_type, environment, storage):
    instance_uid = workspace_uid
    machine_type_uid = machine_type
    instance_template_uid = environment
    volume_type_uid = storage

    pattern = re.compile('^[a-z0-9][-a-z0-9]{1,23}[a-z0-9]$')
    if not pattern.match(instance_uid):
        click.echo('Name should be 3 to 25 characters long, lower case alphanumeric or \'-\' and must start and end with an alphanumeric character.')
        sys.exit(1)

    new_instance = {
        'uid': instance_uid,
        'machineType': {
            'uid': machine_type_uid
        },
        'volumeType': {
            'uid': volume_type_uid
        },
        'instanceTemplate': {
            'uid': instance_template_uid
        }
    }

    vc = ctx.obj['vc']
    vc.init_credentials_retrieval()
    vc.init_endpoint()
    response = ctx.obj['vc'].post(post_object=new_instance)

    if response['status_code'] == 200:
        print('New workspace created: {}'.format(response['data']['uid']))
    else:
        print('An error occurred with creating a new workspace.')
        print("Details: {}".format(response['data']))


@workspaces.command('list', help='Show active workspaces in the current project')
@click.pass_context
@login_required
def list_instances(ctx):
    vc = ctx.obj['vc']
    vc.init_credentials_retrieval()
    vc.init_endpoint()
    items = vc.list()

    if items is None or len(items) == 0:
        print('No workspaces found.')
        return

    for item in items:
        info = item['machineType']['info']
        item['cpu'] = info['cpu']
        item['gpu'] = info.get('gpu')
        item['ram'] = info['ram']
        item['hdd'] = item['volumeType']['info']['size']
    vc.print_items(items, fields=['uid', 'cpu', 'gpu', 'ram', 'hdd'], field_names=['ID', 'CPU', 'GPU', 'RAM', 'HDD'])


@workspaces.command('terminate', help='Terminate the workspace')
@click.argument(
    'workspace_uid',
    type=str
)
@click.pass_context
@login_required
def terminate_instance(ctx, workspace_uid):
    vc = ctx.obj['vc']
    vc.init_credentials_retrieval()
    vc.init_endpoint()
    ctx.obj['vc'].delete(workspace_uid, message_on_success='Workspace terminated')
