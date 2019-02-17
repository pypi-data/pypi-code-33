# Main file

import click
from ruamel.yaml import safe_load

from vmbox.cloud_images import LinuxDistro


@click.version_option()
@click.group()
def main():
    pass


@main.command()
@click.option("-l", "--local", is_flag=True, help="All available local images")
@click.option("-r", "--remote", is_flag=True, help="All available remote images")
def images(local, remote):
    """Get local or remote available image
    Args:
        local: default, will give local images
        remote: will return remote repository available images
    """
    with open("repositories.yaml", "r") as f:
        distros = safe_load(f).get("distros")

    if remote:
        distro_name = click.prompt(
            "Linux distribution:", default="cirros", type=click.Choice(distros.keys())
        )
        distro = LinuxDistro(distro_name)
        release = click.prompt(
            "Release:", default=distro.releases[-1], type=click.Choice(distro.releases)
        )
        for img in distro.images(release=release):
            click.echo(img)
    else:
        # local images
        pass
