import sys, traceback
import click
from click import ClickException
import logging
import json
import csv
from datetime import date

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from cropper.harvest import Harvest

from cropper import VERSION

logging.basicConfig(
    level=logging.WARNING,
    format=' %(asctime)s [%(levelname)-7s] %(message)s',
    datefmt='%I:%M:%S %p')
logger = logging.getLogger('harvest_mapper')

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

def flatten(obj, entries):
    """
    Converts an object into a list of simple value pairs
    based on a list of entries to get and using the
    rule of nested object keys are declared as double underscores
    So to fro {'a': 1, 'b' : { 'b1': 3 }} you can get the 3 as 'b__b1'
    """

    result = {}

    for entry in entries:
        parts = entry.split('__')
        value_parts = obj[parts[0]]
        while len(parts) > 1:
            parts = parts[1:]
            value_parts = value_parts[parts[0]]
        result[entry] = value_parts.replace('\r\n',' ') if type(value_parts) is str else value_parts

    return result

def print_obj(obj, entries, print_active=False, template=None):
    """
    Returns a valid CSV row for an object and a list
    of key values to search from, it accepts nested keys using
    the double underscore
    """
    
    if print_active:
        color = "green" if obj['is_active'] else "yellow"
    else:
        color = "green"

    flattened = flatten(obj,entries)
    if template:
        result = template.format(**flattened)
    else:
        with StringIO(newline='') as writer:
            csv_writer = csv.DictWriter(writer, fieldnames=entries)
            csv_writer.writerow(flattened)
            result = writer.getvalue()
    
    click.secho(result.strip('\r\n'),fg=color)

def print_list_objs(entries, headers, print_active=False, print_headers=True, template=None):
    if print_headers:
        click.secho(",".join(headers),fg="green")
    for entry in entries:
        print_obj(entry, headers, print_active, template)

@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('-l', '--loglevel', type=click.Choice(['error', 'warn', 'info', 'debug']), default='warn')
@click.option('-t', '--token', required=True, type=str, envvar='HARVEST_TOKEN',
              help="Your Harvest Auth Token, you can set this using the environment variable HARVEST_TOKEN")
@click.option('-a', '--account-id', 'accountid', required=True, type=str, envvar='HARVEST_ID',
              help="Your Harvest Account ID, you can set this using the environment variable HARVEST_ID")
@click.option('-u', '--user-id', 'userid', required=False, type=int, envvar='HARVEST_USER_ID',
              help="Your Harvest User ID, you can set this using the environment variable HARVEST_USER_ID")
@click.version_option(VERSION, '--version', '-v')
@click.pass_context
def cli(ctx, loglevel, token, accountid, userid):
    """
    This command line tool helps you explore your Harvest account and
    modify time entries. Find more details on each command help instructions.
    """
    if loglevel == 'error':
        logger.setLevel(logging.ERROR)
    elif loglevel == 'warn':
        logger.setLevel(logging.WARNING)
    elif loglevel == 'info':
        logger.setLevel(logging.INFO)
    elif loglevel == 'debug':
        logger.setLevel(logging.DEBUG)
    else:
        ClickException('no log level')

    if ctx.invoked_subcommand is None:
        click.echo('I was invoked without subcommand')
    else:            
        # ensure that ctx.obj exists and is a dict (in case `cli()` is called
        # by means other than the `if` block below
        ctx.ensure_object(dict)

        ctx.obj['harvest'] = Harvest(
            logger=logger, token=token, accountid=accountid)
        ctx.obj['user_id'] = userid
    


@cli.command(help="Checks connectivity with Harvest and shows user info")
@click.pass_context
def check(ctx):
    hobj = ctx.obj['harvest']
    try:
        check = hobj.check()
        logger.info('Harvest auth worked!!\r\n')
        click.echo(json.dumps(check))
    except Exception as e:
        click.secho(str(e), fg='red')
        ctx.abort()


@cli.command(help="Get company data")
@click.pass_context
def company(ctx):
    hobj = ctx.obj['harvest']
    try:
        data = hobj.company()
        click.echo(json.dumps(data))
    except Exception as e:
        click.secho(str(e), fg='red')
        ctx.abort


@cli.command(help="Get clients data")
@click.option('-f', '--format', 'format', default='text', type=click.Choice(['text', 'json']), help="Output format")
@click.option('-a', '--active', 'active', type=click.Choice(['all', 'active', 'inactive']), default='all', help="Filter by status")
@click.pass_context
def clients(ctx, format, active):
    hobj = ctx.obj['harvest']
    try:
        data = hobj.clients(active)
        if format == "text":
            headers = ['id','name','is_active']
            print_list_objs(data, headers, True)
        else:
            click.echo(json.dumps(data))
    except Exception as e:
        click.secho(str(e), fg='red')
        ctx.abort

@cli.command(help="Get users data")
@click.option('-f', '--format', 'format', default='text', type=click.Choice(['text', 'json']), help="Output format")
@click.option('-a', '--active', 'active', type=click.Choice(['all', 'active', 'inactive']), default='all', help="Filter by status")
@click.pass_context
def users(ctx, format, active):
    hobj = ctx.obj['harvest']
    try:
        data = hobj.users(active)
        if format == "text":
            headers = ['id','first_name','last_name','is_admin']
            print_list_objs(data, headers, True)
        else:
            click.echo(json.dumps(data))
    except Exception as e:
        click.secho(str(e), fg='red')
        ctx.abort


@cli.command(help="Get the list of projects")
@click.option('-f', '--format', 'format', default='text', type=click.Choice(['text', 'json']), help="Output format")
@click.option('-a', '--active', 'active', type=click.Choice(['all', 'active', 'inactive']), default='all', help="Filter by status")
@click.option('-c', '--client', 'client', default=None, type=str, help="Filter by client identifier")
@click.pass_context
def projects(ctx, format, active, client):
    hobj = ctx.obj['harvest']
    try:
        data = hobj.projects(active, client)
        if format == "text":
            headers = ['id','name','client__name','is_active']
            print_list_objs(data, headers, True)
        else:
            click.echo(json.dumps(data))
    except Exception as e:
        click.secho(str(e), fg='red')
        ctx.abort


@cli.command(help="Get a project")
@click.option('-f', '--format', 'format', default='json', type=click.Choice(['text', 'json']), help="Output format")
@click.argument('project_id', type=int)
@click.pass_context
def project(ctx, format, project_id):
    hobj = ctx.obj['harvest']
    try:
        data = hobj.project(project_id)
        if format == "text":
            headers = ['id','name', 'code', 'client__name','is_active', 'is_billable' ,'created_at','updated_at','notes']
            print_list_objs([data], headers, True)
        else:
            click.echo(json.dumps(data))
    except Exception as e:
        click.secho(str(e), fg='red')
        ctx.abort


@cli.command(name="tasks", help="Tasks assignments")
@click.option('-f', '--format', 'format', default='text', type=click.Choice(['text', 'json']), help="Output format")
@click.argument('project_id', type=int)
@click.pass_context
def task_assignments(ctx, format, project_id):
    hobj = ctx.obj['harvest']
    try:
        data = hobj.task_assignments(project_id)
        if format == "text":
            headers = ['id','name','is_active']
            print_list_objs(data, headers, True)
        else:
            click.echo(json.dumps(data))
    except Exception as e:
        click.secho(str(e), fg='red')
        ctx.abort


@cli.command(name="time-entries", help="Get time entries for a given project")
@click.option('-f', '--format', 'format', default='text', required=False, type=click.Choice(['text', 'json']), help="Output format")
@click.option('-ti', '--task-id', 'task_id', required=False, type=int, help="Filter by task")
@click.option('-ui', '--user-id', 'user_id', required=False, type=int, help="Filter by user")
@click.argument('project_id',type=int)
@click.pass_context
def time_entries(ctx, format, project_id, task_id, user_id):
    hobj = ctx.obj['harvest']
    try:
        data = hobj.time_entries(project_id = project_id, user_id = user_id)
        if task_id:
            data = list(filter(lambda entry: entry['task']['id'] == task_id, data))
        if format == "text":
            headers = ['id','user__name','task__id','task__name', 'spent_date', 'hours','notes']
            print_list_objs(data, headers, False)
        else:
            click.echo(json.dumps(data))
    except Exception as e:
        click.secho(str(e), fg='red')
        ctx.abort

@cli.command(name="time-entry", help="Get a time entries")
@click.option('-f', '--format', 'format', default='text', type=click.Choice(['text', 'json']), help="Output format")
@click.argument('time_entry_id', type=int)
@click.pass_context
def time_entry(ctx, format, time_entry_id):
    hobj = ctx.obj['harvest']
    try:
        entry = hobj.time_entry(time_entry_id)
        if format == "text":
            headers = ['id','user__name','task__id','task__name', 'spent_date', 'hours','notes']
            print_list_objs([entry], headers, False)
        else:
            click.echo(json.dumps(entry))
    except Exception as e:
        click.secho(str(e), fg='red')
        ctx.abort


@cli.command(name="update-time-entry", help="Update a time entry with a new project and task identifiers")
@click.argument('time_entry_id', type=int)
@click.argument('project_id', type=int)
@click.argument('task_id', type=int)
@click.pass_context
def update_time_entry(ctx, time_entry_id, project_id, task_id):
    hobj = ctx.obj['harvest']
    try:
        data = hobj.update_time_entry(
            time_entry_id, project_id, task_id)
        click.echo(json.dumps(data))
    except Exception as e:
        click.secho(str(e), fg='red')
        ctx.abort


@cli.command(name="update-all-time-entries", help="Update all time entries from a given project and task to another project and task")
@click.option('-fp', '--from-project', 'from_project', required=True, type=int, help="Source project")
@click.option('-ft', '--from-task', 'from_task', required=True, type=int, help="Source task")
@click.option('-tp', '--to-project', 'to_project', required=True, type=int, help="Destination project")
@click.option('-tt', '--to-task', 'to_task', required=True, type=int, help="Destination task")
@click.option('-na', '--note-append', 'note_append', required=False, type=str, help="Text to add to the time entry note")
@click.pass_context
def update_all_time_entries(ctx, from_project, from_task, to_project, to_task, note_append):
    hobj = ctx.obj['harvest']
    try:
        # Get all the time entries
        data = hobj.time_entries(project_id = from_project)
        data = filter(lambda entry: entry['task']['id'] == from_task, data)
        for entry in data:
            tid = entry['id']
            if note_append:
                if entry['notes']:
                    notes = '{} - {}'.format(entry['notes'], note_append)
                else:
                    notes = note_append
                result = hobj.update_time_entry( tid, to_project, to_task, notes)
            else:
                result = hobj.update_time_entry( tid, to_project, to_task)

            if result:
                click.secho(f'Time entry {tid} updated', fg="green")
        else:
            click.secho('All entries migrated!', fg="green")
    except Exception as e:
        click.secho(str(e), fg='red')
        ctx.abort

@cli.command(name="running", help="Running time entries")
@click.option('-f', '--format', 'format', default='text', type=click.Choice(['text', 'json']), help="Output format")
@click.option('--mine/--all', 'mine', default=True, help="All the entries or just mine")
@click.pass_context
def runnnig(ctx, format, mine):
    hobj = ctx.obj['harvest']
    try:
        user_id = ctx.obj['user_id'] if mine else None
        data = hobj.time_entries(is_running = "true", user_id = user_id)

        if format == "text":
            data_by_user = {}
            for d in data:
                user_name = d['user']['name'] 
                if user_name in data_by_user:
                    data_by_user[user_name].append(d)
                else:
                    data_by_user[user_name] = [d]
            
            headers = ['hours', 'task__name','notes']
            base_template = "{hours:<4.2f} | {task__name:<30s} | {notes}"
            for user in data_by_user:
                if mine:
                    template = base_template
                else:
                    user_first = user.split(' ')[0]
                    template = "".join([f'{user_first:<10s}| ', base_template ])
                print_list_objs(
                    data_by_user[user], 
                    headers,
                    print_active = False, 
                    print_headers = False,
                    template = template)
    

        else:
            click.echo(json.dumps(data))
    except Exception as e:
        click.secho(str(e), fg='red')

        exc_traceback = sys.exc_info()[2]
        click.echo("*** print_tb:")
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        ctx.abort

@cli.command(name="today", help="Today time entries")
@click.option('-f', '--format', 'format', default='text', type=click.Choice(['text', 'json']), help="Output format")
@click.option('--mine/--all', 'mine', default=True, help="All the entries or just mine")
@click.pass_context
def today(ctx, format, mine):
    hobj = ctx.obj['harvest']
    try:
        user_id = ctx.obj['user_id'] if mine else None
        today = date.today().isoformat()
        data = hobj.time_entries(user_id = user_id, _from = today)

        if format == "text":
            data_by_user = {}
            for d in data:
                user_name = d['user']['name'] 
                if user_name in data_by_user:
                    data_by_user[user_name].append(d)
                else:
                    data_by_user[user_name] = [d]
            
            headers = ['hours', 'project__name', 'task__name','notes', 'is_running']
            base_template = "{hours:<4.2f} | {is_running:1} | {project__name:<30s} | {task__name:<30s} | {notes}"
            for user in data_by_user:
                if mine:
                    template = base_template
                else:
                    user_first = user.split(' ')[0]
                    template = "".join([f'{user_first:<10s}| ', base_template ])
                print_list_objs(
                    data_by_user[user], 
                    headers,
                    print_active = False, 
                    print_headers = False,
                    template = template)
                total = sum(map(lambda e : float(e['hours']), data_by_user[user]))
                if mine:
                    click.secho(f'Total: {total:4.2f}\r\n',fg="red")
                else:
                    click.secho(f'    Total | {total:4.2f}\r\n',fg="red")


        else:
            click.echo(json.dumps(data))
    except Exception as e:
        click.secho(str(e), fg='red')
        ctx.abort
