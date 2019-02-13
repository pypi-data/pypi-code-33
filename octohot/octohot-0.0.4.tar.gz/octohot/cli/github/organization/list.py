import click


@click.command(name='list')
@click.option('--type', '-t', type=click.Choice(['https', 'ssh']),
              default='https')
def list(type):
    """List all repositories to octohot.yml config file from a Organization
    from GitHub"""
    from octohot.cli.github.organization.organization import url_list
    print('\n'.join(url_list(type)))
