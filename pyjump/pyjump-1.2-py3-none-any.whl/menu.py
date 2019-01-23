#!/usr/bin/env python3

import locale
import os
import subprocess

import click
import dotenv
import requests
from dialog import Dialog


class Jump:
    items: list = []
    formatted_menu_items: list = []

    def __init__(self) -> None:
        self.d: Dialog = Dialog()
        self.get_item_list()
        self.run()

    def get_item_list(self) -> None:
        secret_key: str = os.environ.get('AUTH_KEY')
        extra_headers: dict = {}

        if secret_key is not None:
            extra_headers[os.environ.get('AUTH_HEADER')] = secret_key

        self.items: list = requests.get(os.environ.get('ENDPOINT'), headers=extra_headers).json()['items']

    def format_items(self, items: list, servers_list: bool = False) -> None:
        self.formatted_menu_items: list = []

        for item in items:
            if servers_list is False and item['in_jumpgate'] is False:
                pass
            else:
                self.formatted_menu_items.append((item['name'] if not servers_list else item['display_name'], ''))

    def create_menu(self, title: str, items: list, cancel_label: str = 'Back') -> tuple:
        return self.d.menu(
            text=title,
            choices=items,
            menu_height=15,
            cancel_label=cancel_label,
        )

    def get_server_info(self, app: str) -> dict:
        for item in self.items:
            if item['name'] == app:
                return item

    def get_server_items(self, app: str, server_name: str) -> dict:
        app_object: dict = self.get_server_info(app)

        for server in app_object['servers']:
            if server['display_name'] == server_name:
                return server

    def run(self):
        self.format_items(self.items)

        code, app = self.create_menu('Choose an application', self.formatted_menu_items, 'Exit')

        if code == self.d.OK:
            self.format_items(self.get_server_info(app)['servers'], True)

            code, server = self.create_menu('Choose a server', sorted(self.formatted_menu_items, key=self.sort_servers))

            if code == self.d.CANCEL:
                self.run()
            else:
                server_info: dict = self.get_server_items(app, server)

                if server_info['is_serverpilot']:
                    command: str = 'ssh -p{} {}@{} -t "cd /srv/users/serverpilot/apps/{}; exec /bin/bash -l"'
                else:
                    command: str = 'ssh -p{} {}@{}'

                subprocess.call(
                    command.format(
                        server_info['port'],
                        server_info['user'],
                        server_info['ip'],
                        app
                    ),
                    shell=True,
                )

                self.run()

    def sort_servers(self, server: tuple) -> int:
        weights = {
            'Staging': -1,
            'Acceptance': 0,
            'Production': 1,
        }

        return weights[server[0]] if server[0] in weights else -1


@click.command()
@click.option('--env-file')
def main(env_file):
    if env_file is None:
        env_file: str = '{}/.jump.env'.format(os.environ.get('HOME'))

    if os.path.exists(env_file) is False:
        click.secho('Can not find .env file in {}'.format(env_file), fg='red')
        exit(1)

    dotenv.load_dotenv(env_file)
    locale.setlocale(locale.LC_ALL, '')

    try:
        Jump()
    except KeyboardInterrupt:
        pass
