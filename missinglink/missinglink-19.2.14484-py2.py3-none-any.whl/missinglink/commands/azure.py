import click
from missinglink.core.context import Expando

from missinglink.commands.utilities import CommonOptions
from missinglink.commands.utilities.default_params_option import option_with_default_factory
from .resources import resources_commands


@resources_commands.group('azure')
@option_with_default_factory('--location', envvar="ML_AZURE_LOCATION", help='Azure location to use.', default_key='azure_location', required=False)
@click.pass_context
def azure_commands(ctx, **kwargs):
    ctx.obj.azure = Expando()
    ctx.obj.azure.location = kwargs.pop('location', None)


@azure_commands.command('init', help='Initialize Resource Management on Azure, creating the cloud connection and the default queue and resource group.')
@CommonOptions.org_option()
@click.pass_context
def init(ctx, **kwargs):
    from missinglink.commands.cloud.azure.azure_context import AzureContext

    azure_context = AzureContext(ctx, kwargs)
    azure_context.init_and_authorise_app()
