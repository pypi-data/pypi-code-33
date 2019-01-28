""" Command line interface """
import argparse
import getpass

import quackdns.config as config

def configure_dns_parameters():
    print("Quack DNS configuration")
    print("-----------------------")
    print("Please, insert your Duck DNS data:")
    print("(If you don't remember, check on: https://www.duckdns.org)")
    settings = config.Settings()
    settings.set_domain(input("Please, insert your domain name:\n>>> "))
    settings.set_token(getpass.getpass("Please, insert your token:\n>>> "))
    print("\nConfiguration complete!\n")
    return settings


def parse_arguments(argv, only_config=False):
    parser = argparse.ArgumentParser(description='Quack DNS.')

    if only_config == False:
        parser.add_argument('action', choices=('start', 'stop', 'restart'))

    parser.add_argument('-c', '--config',
                        type=str,
                        required=False,
                        help='Configuration path',
                        default=config.__DEFAULT_CONFIG_PATH__)
    parser.add_argument('-i', '--interval',
                        type=int,
                        required=False,
                        help='Interval (seconds) between updates',
                        default=config.__DEFAULT_UPDATE_INTERVAL__)

    return parser.parse_args(argv[1:])
