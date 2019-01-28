"""
    These sub-commands and their corresponding logic are both implamented in this file.
    TO DO: Break out the logic for these commands into a seperate behavior file.
"""

from pathlib import Path
from cli import pyke
import requests
import click
import json
import sys
import os

@click.group(help="Profiles add company context to commands. Almost all calls to Lumavate require context. \
Profiles use Envs to get tokens and then give those tokens context using the Org ID.")
def profile():
    pass

@click.command('ls', help="List the profiles you have configured.")
@click.option('--format', '-f', default='{profileName} {env} {orgName} {orgId}', help='The --format option takes the column name of the returned table wrapped in \
{} and returns only that column. It is not compatible with --json flag.')
@click.option('--json', 'json_flag', is_flag=True, help='Return raw json.')
def list(format, json_flag):
    config = pyke.auth.load_config()

    data = []
    for key in config['profiles'].keys():
        config['profiles'][key]['profileName'] = str(key)
        data.append(config['profiles'][key])

    if json_flag:
        click.echo(json.dumps(config))
        return

    pyke.Util().print_table(data, format)

@click.command()
@click.option('--profile-name', prompt=True, help='Profile Name')
@click.option('--env', default=None, help='The name of the Env you want to use with this profle')
@click.option('--format', '-f', default='{env} {orgName} {orgId}', help='The available column names for this command are {env} {orgName} {orgId}')
def add(profile_name, env, format):
    if not profile_name.strip():
        raise click.BadParameter(click.style("The --profile-name must contain more than just whitespace.", fg='red'))

    click.echo(' ')
    config = pyke.auth.load_config()

    titles = {
        'envName': 'Env Name',
        'app': 'App',
        'audience': 'Audience',
        'token': 'Token'
    }

    headers = '{envName} {app} {audience} {token}'

    if env is None:
        data = []
        for key in config['envs'].keys():
            config['envs'][key]['envName'] = str(key)
            data.append(config['envs'][key])

        pyke.Util().print_table(data, headers, titles=titles)
        click.echo(' ')

        env = input("Name of the Env you want to use with this profle: ")
        click.echo(' ')

    env_names = config["envs"].keys()
    if env not in env_names:
        raise click.BadParameter(click.style("You must select and Env that you have configured", fg='red'))

    config['profiles'][profile_name] = {
                                        "accessToken": " ",
                                        "env": env,
                                        "orgId": None,
                                        "orgName": ""
                                    }

    profile_data = config['profiles'][profile_name]

    resp = pyke.Util().list_companies(env)
    click.echo(' ')

    org_id = input("Org ID you want to associate with this profile: ")
    click.echo(' ')

    try:
        org_id = int(org_id)
    except Exception as e:
        raise click.BadParameter(click.style('You must provide the id of the organization', fg='red'))

    if str(org_id) not in [rec.get('id').replace(" ", "") for rec in resp]:
        raise click.BadParameter(click.style('You must provide the id of the organization you have access to', fg='red'))

    org_name = next(rec.get('name') for rec in resp if int(rec.get('id')) == org_id)

    profile_data["orgId"] = org_id
    profile_data["orgName"] = org_name.rstrip()

    config['profiles'][profile_name] = profile_data

    pyke.auth.save_config(config)

    profile_data["profile"] = profile_name

    titles = {
        'profile': 'Profile',
        'env': 'Environment',
        'orgName': 'Org Name',
        'orgId': 'Org ID'
    }

    pyke.Util().print_table([profile_data], format, titles=titles)
    click.echo(' ')

@click.command('rm')
@click.option('--profile', '-p', prompt=True, help='Profile to delete')
def delete(profile):
    config_data = pyke.auth.load_config()
    profile_data = config_data["profiles"][profile]
    del config_data["profiles"][profile]

    pyke.auth.save_config(config_data)

    click.echo("Deleted profile:")
    click.echo(json.dumps(profile_data))


profile.add_command(list)
profile.add_command(delete)
profile.add_command(add)
