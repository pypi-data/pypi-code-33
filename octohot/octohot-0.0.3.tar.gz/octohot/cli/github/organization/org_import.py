import click


@click.command(name='import')
@click.argument('url_type', type=click.Choice(['https', 'ssh']), default='ssh')
def organization_import(url_type):
    """Import all repositories to octohot.yml config file from a Organization
    from GitHub"""
    from octohot.cli.github.organization.organization import url_list
    urls = url_list(url_type)

    from octohot.cli.config import config, save
    missed = [url for url in urls if url not in config['repositories']]
    [config['repositories'].append(url) for url in missed]
    save()
    click.echo("Added %s new repositories in config file" % len(missed))

