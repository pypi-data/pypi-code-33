# -*- coding: utf8 -*-
import logging
from functools import wraps
import botocore
import click
from click import exceptions

from missinglink.commands.utilities.options import CommonOptions
from .cloud.aws import AwsContext, BackendContext
from .commons import output_result
from missinglink.core.context import Expando
from .utilities.default_params_option import option_with_default_factory
from .resources import resources_commands


@resources_commands.group('aws')
@option_with_default_factory('--region', envvar="ML_AWS_REGION", help='AWS region to use', default_key='aws_region', required=False)
@click.pass_context
def aws_commands(ctx, **kwargs):
    ctx.obj.aws = Expando()
    ctx.obj.aws.region = kwargs.pop('region', None)


def handle_aws_errors(fn):
    @wraps(fn)
    def try_call(*args, **kwargs):
        # noinspection PyUnresolvedReferences
        try:
            return fn(*args, **kwargs)
        except botocore.exceptions.NoCredentialsError as ex:
            logging.info('Failed to validate authentication', exc_info=1)
            raise exceptions.ClickException('AWS configuration is incomplete. Please run `aws configure`. Error: %s' % str(ex))

    return try_call


@aws_commands.command('init')
@CommonOptions.org_option()
@click.option('--ssh-key-path', default=None, help='SSH Key to use in for git clone commands, and connecting to virtual machines')
@handle_aws_errors
@click.pass_context
def init_auth(ctx, **kwargs):
    aws = AwsContext(ctx, kwargs)

    aws.encrypt_and_send_connector()
    aws.setup_spot_role_if_needed()
    aws.setup_vpc_if_needed()
    aws.setup_s3_if_needed()
    click.echo(aws.auth_state)
