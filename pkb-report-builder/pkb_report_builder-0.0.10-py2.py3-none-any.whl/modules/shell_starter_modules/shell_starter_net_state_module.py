import click
import modules.net_state_modules.net_state_module as ns_module

@click.group()
def net_stats_commands_cli():
    pass


@net_stats_commands_cli.command()
def get_net_state():
    try:
        click.echo(ns_module.get_net_state_info())
        pass
    except Exception as e:
        pass
