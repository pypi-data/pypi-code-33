# -*- coding: utf8 -*-
import click
from missinglink.commands.commons import add_to_data_if_not_none, output_result
from missinglink.core.api import ApiCaller
from missinglink.commands.utilities.options import CommonOptions


@click.group('projects')
def projects_commands():
    pass


@projects_commands.command('list')
@click.pass_context
def list_projects(ctx):
    projects = ApiCaller.call(ctx.obj, ctx.obj.session, 'get', 'projects')

    output_result(ctx, projects.get('projects', []), ['project_id', 'display_name', 'description', 'token', 'org'])


max_project_display_name = 140
min_project_display_name = 1

max_project_description = 140
min_project_description = 0


@projects_commands.group('alerts')
def alerts_commands():
    pass


@alerts_commands.command('subscribe')
@CommonOptions.project_id_option(required=True)
@CommonOptions.alert_type_option(required=True, multiple=True)
@click.pass_context
def subscribe_alert(ctx, project, alert_type):
    data = {
        'alert_types': alert_type,
        'project_ids': project,
    }

    result = ApiCaller.call(ctx.obj, ctx.obj.session, 'post', 'projects/subscribe', data)

    output_result(ctx, result, ['ok'])


@alerts_commands.command('unsubscribe')
@CommonOptions.project_id_option(required=True, multiple=True)
@CommonOptions.alert_type_option(required=True, multiple=True)
@click.pass_context
def unsubscribe_alert(ctx, project, alert_type):
    data = {
        'alert_types': alert_type,
        'project_ids': project,
    }

    result = ApiCaller.call(ctx.obj, ctx.obj.session, 'post', 'projects/unsubscribe', data)

    output_result(ctx, result, ['ok'])


@alerts_commands.command('list')
@click.pass_context
def list_alert(ctx):
    alerts = ApiCaller.call(ctx.obj, ctx.obj.session, 'get', 'projects/subscriptions')

    output_result(ctx, alerts.get('alerts', []), ['project_id', 'display_name', 'org', 'alert_type', 'subscribed'])


@projects_commands.command('create')
@CommonOptions.display_name_option(min_length=min_project_display_name, max_length=max_project_display_name)
@CommonOptions.description_option(min_length=min_project_description, max_length=max_project_description)
@CommonOptions.org_option()
# deprecated option but some clients use it
@click.pass_context
def create_project(ctx, display_name, description, org):
    data = {}

    add_to_data_if_not_none(data, display_name, "display_name")
    add_to_data_if_not_none(data, org, "org")
    add_to_data_if_not_none(data, description, "description")

    result = ApiCaller.call(ctx.obj, ctx.obj.session, 'post', 'projects', data)

    output_result(ctx, result, ['id', 'token'])


@projects_commands.command('transfer')
@CommonOptions.project_id_option(required=True)
@click.option('--transfer-to', required=False)
@click.pass_context
def transfer_project(ctx, project, transfer_to):
    data = {}

    add_to_data_if_not_none(data, transfer_to, "transfer_to")

    result = ApiCaller.call(
        ctx.obj, ctx.obj.session, 'post', 'projects/{project_id}/transfer'.format(project_id=project), data)

    output_result(ctx, result, ['ok'])
