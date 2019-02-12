#!/usr/bin/env python
# -*- coding: utf8 -*-
import logging
import os
import sys
import click
import sentry_sdk
from missinglink.core.context import init_context2
from missinglink.core.exceptions import MissingLinkException
from missinglink.legit.gcp_services import GooglePackagesMissing, GoogleAuthError
from missinglink.commands.global_cli import add_commands, cli, self_update, set_pre_call_hook
from missinglink.commands.mali_version import get_missinglink_cli_version
import click_completion
from missinglink.core.config import default_missing_link_folder
from missinglink.legit.path_utils import makedir


__prev_resolve_ctx = click_completion.resolve_ctx


@cli.command('install')
@click.argument('shell', required=False, type=click_completion.DocumentedChoice(click_completion.shells))
def install(shell):
    """Install the click-completion-command completion"""
    from missinglink.commands.install import rc_updater

    shell = shell or click_completion.get_auto_shell()

    code = click_completion.get_code(shell)

    file_name = '{dir}/completion.{shell}.inc'.format(dir=default_missing_link_folder(), shell=shell)

    makedir(file_name)

    with open(file_name, 'w') as f:
        f.write(code)

    rc_updater(shell, file_name)


def __ml_resolve_ctx(_cli, prog_name, args):
    def find_top_parent_ctx(current_ctx):
        parent = current_ctx
        while True:
            if current_ctx.parent is None:
                break

            parent = current_ctx.parent
            current_ctx = parent

        return parent

    ctx = __prev_resolve_ctx(cli, prog_name, args)

    top_ctx = find_top_parent_ctx(ctx)

    init_context2(
        ctx,
        top_ctx.params.get('session'),
        top_ctx.params.get('output_format'),
        top_ctx.params.get('config_prefix'),
        top_ctx.params.get('config_file'))

    return ctx


click_completion.resolve_ctx = __ml_resolve_ctx
click_completion.init()


def _setup_logger(log_level):
    if not log_level:
        return

    log_level = log_level.upper()

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    handler = logging.StreamHandler(stream=sys.stderr)
    formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(name)s %(levelname)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    logging_method = getattr(root_logger, log_level.lower())
    logging_method('log level set to %s (this is a test message)', log_level)


def main():
    def setup_pre_call(ctx):
        if ctx.obj.log_level is not None:
            _setup_logger(ctx.obj.log_level)

        with sentry_sdk.configure_scope() as cli_scope:
            token_data = ctx.obj.config.token_data

            cli_scope.set_tag('command', ctx.invoked_subcommand)
            cli_scope.user = {'id': token_data.get('uid'), 'email': token_data.get('email'), 'username': token_data.get('name')}

    def setup_sentry_sdk():
        cli_version = get_missinglink_cli_version()

        is_dev_version = cli_version is None or cli_version.startswith('0')
        if is_dev_version:
            return

        sentry_sdk.init(
            'https://604d5416743e430b814cd8ac79103201@sentry.io/1289799',
            release=cli_version)

        with sentry_sdk.configure_scope() as scope:
            scope.set_tag('source', 'ml-cli')

    setup_sentry_sdk()
    set_pre_call_hook(setup_pre_call)

    if sys.argv[0].endswith('/mali') and not os.environ.get('ML_DISABLE_DEPRECATED_WARNINGS'):
        click.echo('instead of mali use ml (same tool with a different name)', err=True)

    if os.environ.get('MISSINGLINKAI_ENABLE_SELF_UPDATE'):
        self_update()

    add_commands()
    cli.add_command(install)
    cli()


if __name__ == "__main__":
    try:
        main()
    except GooglePackagesMissing:
        click.echo('you to run "pip install missinglink[gcp]" in order to run this command', err=True)
    except GoogleAuthError:
        click.echo('Google default auth credentials not found, run gcloud auth application-default login', err=True)
    except MissingLinkException as ex:
        click.echo(ex, err=True)
