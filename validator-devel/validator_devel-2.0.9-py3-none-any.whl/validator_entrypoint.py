#!/usr/bin/env python
import os
import click
import shutil
import logging
import pkg_resources

from validator_devel.main import main

APP_NAME = "validator-devel"

@click.command()
@click.option('--debug', is_flag=True)
def cli(debug):
    """Before starting the validator devel create the setting."""
    if debug:
        logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

    project_dir = click.get_app_dir(APP_NAME)
    os.makedirs(project_dir, exist_ok=True)

    # Check the existence of development path.
    download_dir = os.path.join(click.get_app_dir(APP_NAME), 'download')
    if os.path.exists(download_dir):
        # The download path must be delete.
        shutil.rmtree(download_dir)
        logging.debug(f"cleaned the download directory {download_dir}")
    os.makedirs(download_dir, exist_ok=True)
    logging.debug(f"download directory located at {download_dir}")

    if not pkg_resources.resource_exists("validator_devel", "config/settings_template.yaml"):
        click.echo("Not found settings.")
        return

    settings_file = os.path.join(project_dir, "settings.yaml")
    if not os.path.exists(settings_file):
        # When the settings file doesn't exists create it.
        settings = pkg_resources.resource_filename("validator_devel", "config/settings_template.yaml")
        shutil.copyfile(settings, os.path.join(project_dir, "settings.yaml"))

    # Setting the base directory where the config are stored.
    # https://dynaconf.readthedocs.io/en/latest/guides/configuration.html
    os.environ["PROJECT_ROOT_FOR_DYNACONF"] = project_dir

    logging.debug(f"found config path at {project_dir}")
    static_resource_path = pkg_resources.resource_filename("validator_devel", "static")
    logging.debug(f"found static resource {static_resource_path}")

    click.echo("Starting validator-devel...")

    try:
        main()
    except ValueError as e:
        click.echo(e)
        click.echo("Seems you haven't configured the application, please edit the config files and restart.")
        click.edit(filename=settings_file)
    finally:
        click.echo("Closing validator-devel")
