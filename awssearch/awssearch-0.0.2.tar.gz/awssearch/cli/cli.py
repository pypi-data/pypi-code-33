import click


aws_profiles = output_format = None


@click.group()
@click.option('--verbose', '-v', is_flag=True, default=False,
              help='Enables verbose mode.')
@click.option('--profile', '-p',
              help='AWS Profile, if not set check all profiles')
@click.option('--output', '-o', default="json",
              help='Output format: json, csv')
def cli(verbose, profile, output):
    """Command line interface for the awssearch package"""
    if verbose:
        import logging
        logging.getLogger().setLevel(logging.INFO)

    global aws_profiles
    aws_profiles = profile

    global output_format
    output_format = output


@click.command()
def version():
    """Display the current version."""
    import pkg_resources  # part of setuptools
    v = pkg_resources.require("awssearch")[0].version
    click.echo(f'version: {v}')


cli.add_command(version)

from .ip import ip
cli.add_command(ip.ip)

if __name__ == '__main__':
    cli()
