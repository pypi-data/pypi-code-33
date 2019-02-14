import click


@click.command(name='list')
@click.option('--url_type', '-t', type=click.Choice(['https', 'ssh']),
              default='https')
def org_list(url_type):
    """List all repositories to octohot.yml config file from a Organization
    from GitHub"""
    from octohot.cli.github.organization.organization import url_list
    print('\n'.join(url_list(url_type)))
