# -*- coding: utf8 -*-
import click

from missinglink.core.api import ApiCaller

from missinglink.commands.utilities.options import CommonOptions
from .commons import add_to_data_if_not_none, output_result


@click.group('orgs')
def orgs_commands():
    pass


@orgs_commands.command('list')
@click.pass_context
def list_orgs(ctx):
    result = ApiCaller.call(ctx.obj, ctx.obj.session, 'get', 'orgs')

    output_result(ctx, result.get('orgs', []), ['org', 'display_name'])


@orgs_commands.command('create')
@CommonOptions.org_option()
@CommonOptions.display_name_option(required=False)
@CommonOptions.description_option()
@click.pass_context
def create_org(ctx, org, display_name, description):
    data = {}

    add_to_data_if_not_none(data, display_name, 'display_name')
    add_to_data_if_not_none(data, description, 'description')
    add_to_data_if_not_none(data, org, 'org')

    result = ApiCaller.call(ctx.obj, ctx.obj.session, 'post', 'orgs', data)

    output_result(ctx, result, ['ok'])


@orgs_commands.command('auto-join-domain')
@CommonOptions.org_option()
@click.option('--domain', required=True, multiple=True)
@click.pass_context
def auto_join_domain(ctx, org, domain):
    data = {}

    add_to_data_if_not_none(data, list(domain), 'domains')

    result = ApiCaller.call(ctx.obj, ctx.obj.session, 'post', 'orgs/{org}/autoJoin'.format(org=org), data)

    output_result(ctx, result, ['ok'])


@orgs_commands.command('metadata')
@CommonOptions.org_option()
@click.option('--name', '-N')
@click.option('--value', '-V')
@click.option('--add', '-A', is_flag=True)
@click.option('--replace', '-R', is_flag=True)
@click.option('--delete', '-D', is_flag=True)
@click.pass_context
def add_metadata_org(ctx, org, name, value, add, replace, delete):
    data = {}

    action, operation = _get_operation_and_action(add, replace, delete, name, value)

    metadata = {
        'operation': operation,
        'name': name,
        'value': value,
    }

    add_to_data_if_not_none(data, metadata, 'metadata')
    add_to_data_if_not_none(data, org, 'org')

    result = ApiCaller.call(ctx.obj, ctx.obj.session, action, 'orgs/{org}/metadata'.format(org=org), data)

    output_result(ctx, result, ['ok'])


def _get_operation_and_action(add, replace, delete, name, value):
    action = 'post'
    sum_args = int(add + replace + delete)

    if sum_args > 1:
        raise click.UsageError(
            'Use only --replace/-R or --delete/-D or --add/-A (default value), don\'t use more than one')

    operation = 'DELETE' if delete else 'REPLACE'

    if sum_args == 0:
        if name or value:
            operation = 'ADD'
            add = True
        else:
            action = 'get'
            # TODO: continue with metadata get

    if add:
        operation = 'ADD'

    if not(name and value):
        raise click.UsageError(
            'Use --name/-N and --value/-V to replace/delete/add')

    return action, operation
