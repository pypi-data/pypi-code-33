import argparse
import webbrowser
from jovian.utils.api import get_key
from jovian.utils.credentials import purge_config


def exec_init():
    print('[jovian] Visit https://app.jovian.ai to sign up and generate an API key.')
    # webbrowser.open('https://jvn.io/')
    purge_config()
    get_key()
    print('Credentials validated and saved to ~/.jovian/credentials.json.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command')
    args = parser.parse_args()
    command = args.command
    if command == 'init':
        exec_init()


if __name__ == '__main__':
    main()
