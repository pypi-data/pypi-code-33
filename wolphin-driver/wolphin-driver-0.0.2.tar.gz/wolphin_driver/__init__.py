import os
from .settings import PLUGIN_NAME

socket_dir = '/run/docker/plugins'
socket_file = PLUGIN_NAME + '.sock'
socket_path = os.path.join(socket_dir, socket_file)

def main():
    os.execvp(
        'gunicorn',
        [
            'gunicorn',
            '--bind=unix://{}'.format(socket_path),
            '--workers=1',
            'wolphin_driver.wsgi:app'
        ]
    )
