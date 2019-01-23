"""
Workspace module
"""
import sys 
import os
import re
import sys
import json
import datetime

import click
import configobj

import onepanel.models.models as models
from onepanel.models.instance import Instance
from onepanel.commands.base import APIViewController
from onepanel.commands.login import login_required
from onepanel.commands.projects import ProjectViewController
from onepanel.types.duration import DURATION

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

    def get_credentials_from_current_path(self):
        home = os.getcwd()
        project_file = os.path.join(home, ProjectViewController.PROJECT_FILE)
        cfg = configobj.ConfigObj(project_file)

        if len(cfg) == 0:
            return None

        return {
            'account_uid' : cfg['account_uid'],
            'project_uid' : cfg['uid']
        }

    def init_endpoint(self):
        self.endpoint = '{root}/accounts/{account_uid}/projects/{project_uid}/instances'.format(
            root=self.conn.URL,
            account_uid=self.account_uid,
            project_uid=self.uid
        )

    def list(self, account_uid=None, project_uid=None, show_all=False):
        """List all of the workspaces for the provided account_uid, project_uid.
           If show_all is true, and there is no project_uid or account_uid, it will include all workspaces
           for projects the user is a member of too.
        """
        params = None

        if project_uid is not None and account_uid is not None:
            endpoint = '{root}/accounts/{account_uid}/projects/{project_uid}/instances'.format(
                root=self.conn.URL,
                account_uid=account_uid,
                project_uid=project_uid
            )
        else:
            endpoint = '{root}/instances'.format(
                root=self.conn.URL,
                account_uid=account_uid
            )

        if show_all:
            params = '?show_all=true'

        items = APIViewController.list(self, endpoint=endpoint, params=params)

        if items is None:
            return items

        return [Instance.from_json(item) for item in items]

    def create(self, instance):       
        return self.post(post_object=instance, json_encoder=models.APIJSONEncoder)
    
    def pause(self, instance_uid):
        return self.get('/'+instance_uid, '/stop')

    def resume(self, instance_uid):
        return self.get('/'+instance_uid, '/resume')

    def delete_instance(self, account_uid=None, project_uid=None, instance_uid=None):
        if account_uid is None and project_uid is None:
            return self.delete_v2(instance_uid)
        else:
            endpoint = '{root}/accounts/{account_uid}/projects/{project_uid}/instances'.format(
                root=self.conn.URL,
                account_uid=account_uid,
                project_uid=project_uid
            )

            return self.delete_v2(instance_uid, endpoint=endpoint)


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
    help='Machine type ID. Call "onepanel machine-types list" for IDs.'
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
    try:
        response = create_instance_internal(ctx.obj['vc'], workspace_uid, machine_type, environment, storage)
        if response['status_code'] == 200:
            click.echo('New workspace created: {}'.format(response['data']['uid']))
        else:
            click.echo('An error occurred with creating a new workspace.')
            click.echo("Details: {}".format(response['data']))

    except ValueError as error:
        click.echo('\tFailed - {}'.format(error))

@workspaces.command(
    'create-from-file',
    help='''Create new workspaces from a json file. 
    The JSON file contains an array. You can have muliple workspaces defined.

    \b
    sample.json
    [
        {
            "name": "test-5",
            "environment": "jupyter-py3-tensorflow1.11.0",
            "machine" : "aws-shared",
            "storage" : "default-storage-10"  
        }
    ]
    
    Each workspace is created sequentially, top down, one after another. If any fails, they are skipped. 
    '''
)
@click.argument(
    'file_path',
    type=click.Path(exists=True, dir_okay=False)
)
@click.pass_context
@login_required
def create_instances_from_file(ctx, file_path):
    with open(file_path, newline='') as file:
        instances = []

        try:
            instances = json.load(file)
        except json.decoder.JSONDecodeError as error:
            click.echo('Unable to parse json. {}'.format(error))
            return
        
        for instance in instances:
            click.echo('Creating instance {} - {} {} {}'.format(instance['name'], instance['machine'], instance['environment'], instance['storage']))
            try:
                response = create_instance_internal(ctx.obj['vc'], instance['name'], instance['machine'], instance['environment'], instance['storage'])
                if response['status_code'] == 200:
                    click.echo('\tSuccess')
                else:
                    click.echo('\tFailed - {}'.format(response['data']))
            except ValueError as error:
                click.echo('\tFailed - {}'.format(error))

def create_instance_internal(vc, instance_uid, machine_type_uid, instance_template_uid, volume_type_uid):
    # TODO move this checking on the instance level and just pass around an instance
    pattern = re.compile('^[a-z0-9][-a-z0-9]{1,23}[a-z0-9]$')
    if not pattern.match(instance_uid):
        raise ValueError('Name should be 3 to 25 characters long, lower case alphanumeric or \'-\' and must start and end with an alphanumeric character.')

    vc.init_credentials_retrieval()
    vc.init_endpoint()

    i = Instance()
    i.uid = instance_uid
    i.machineType.uid = machine_type_uid
    i.volumeType.uid = volume_type_uid
    i.instanceTemplate.uid = instance_template_uid

    return vc.create(i)

@workspaces.command('list', 
    help='''Show workspaces. If this is done outside a project, it will show 
            all of the user's workspaces. If the --all flag is supplied, it will also show workspaces
            for projects the user is a member of.

            If this is done inside a project, only workspaces for that project are listed.
         '''
)
@click.option('-a', '--show_all', is_flag=True, default=False, 
    help='''If true, shows workspaces for projets the user is a member of.
            This has no effect if you are listing workspaces inside a project.
         '''
)
@click.option('-q', '--id_only', is_flag=True, default=False, 
    help='''Only prints the id information. Inside a proeject, this is just the workspace uid.
            Outside the project this is a tuple [account_uid, project_uid, workspace_uid]

            No message is printed if no workspaces are found.
         '''
)
@click.option('-g', '--duration_gt', 
    type=DURATION,
    help='''Only prints the id information. Inside a proeject, this is just the workspace uid.
            Outside the project this is a tuple [account_uid, project_uid, workspace_uid]

            No message is printed if no workspaces are found.
         '''
)
@click.pass_context
@login_required
def list_instances(ctx, show_all, id_only, duration_gt):
    vc = ctx.obj['vc']
    
    account_uid = None
    project_uid = None

    project_credentials = vc.get_credentials_from_current_path() 
    if project_credentials is not None:
        account_uid = project_credentials['account_uid']
        project_uid = project_credentials['project_uid']

    list_instances_internal(vc, account_uid, project_uid, show_all, id_only, duration_gt)

def list_instances_internal(vc, account_uid, project_uid, show_all, id_only, duration_gt=None):
    items = vc.list(account_uid, project_uid, show_all)

    if items is None or len(items) == 0:
        if not id_only:
            click.echo('No workspaces found.')
            
        return

    if duration_gt is not None:
        items = list(filter(lambda item: item.age() > duration_gt, items))
        # if sys.version_info[0] < 3:


        # items = [item]


    formatted_items = [item.simple_view() for item in items]    

    project_specific = account_uid is not None and project_uid is not None


    if id_only and not project_specific:
        click.echo(" ".join('[{},{},{}]'.format(item.project.account.uid, item.project.uid, item.uid) for item in items))
    elif id_only and project_specific:
        click.echo(" ".join(item.uid for item in items))
    elif project_specific:
        vc.print_items(formatted_items, fields=['uid', 'state', 'age', 'duration_ready', 'cpu', 'gpu', 'ram', 'hdd', ], field_names=['ID', 'STATE', 'AGE', 'RUNNING', 'CPU', 'GPU', 'RAM', 'HDD'])
    else:
        vc.print_items(formatted_items, fields=['account_uid', 'project_uid', 'uid', 'state', 'age', 'duration_ready', 'cpu', 'gpu', 'ram', 'hdd', ], field_names=['ACCOUNT', 'PROJECT', 'ID', 'STATE', 'AGE', 'RUNNING', 'CPU', 'GPU', 'RAM', 'HDD'])        

@workspaces.command('terminate', 
    help='''Terminate the workspace(s) given the uids of the workspace
    
            If executing this command inside a project, just the workspace uid is needed.
            Otherwise, you need a tuple of [account_uid, project_uid, workspace_uid]
         '''
)
@click.argument(
    'uids',
    type=str,
    nargs=-1
)
@click.pass_context
@login_required
def terminate_instance(ctx, uids):
    vc = ctx.obj['vc']

    if len(uids) == 0:
        click.echo('No uids passed in. No instances deleted')
        return

    for uid in uids:
        response = None

        if vc.get_credentials_from_current_path() is not None:
            vc.init_credentials_retrieval()
            vc.init_endpoint()
            response = vc.delete_instance(instance_uid=uid)
        else:
            uid = uid.replace('[', '')
            uid = uid.replace(']', '')
            uid = uid.replace(' ', '')

            ids = uid.split(',')
            response = vc.delete_instance(ids[0], ids[1], ids[2])

        if response['status_code'] == 200:
            click.echo('workspace {} deleted'.format(uid))
        elif response['status_code'] == 404:
            click.echo('workspace {} not found'.format(uid))
        else:
            click.echo('An error occurred with deleting workspace {}.'.format(uid))
            click.echo("Details: {}".format(response['data']))
    
