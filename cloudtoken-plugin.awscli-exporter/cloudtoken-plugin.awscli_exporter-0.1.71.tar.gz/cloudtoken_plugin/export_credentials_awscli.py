# AWS CLI export plugin for cloudtoken.
# Writes the assumed credentials to the ~/.aws/credentials file, under the default profile or optionally under a
# specified profile.
# Input: Credentials
# Output: Credentials written to ~/.aws/credentials

import os
import configparser
import collections
import argparse
import copy


class Plugin(object):
    def __init__(self, config):
        self._config = config
        self._name = 'export_credentials_cli'
        self._description = 'Exports credentials AWS CLI credentials file.'

    def __str__(self):
        return __file__

    @staticmethod
    def unset(args):
        pass

    @staticmethod
    def arguments(defaults):
        parser = argparse.ArgumentParser()
        parser.add_argument("--profile",
                            default=defaults.get("credentials-profile", None),
                            help="Profile to save credentials to in ~/.aws/credentials")
        return parser

    def execute(self, data, args, flags):
        try:
            credentials = next(
                filter(lambda plugin_payload: plugin_payload.get('plugin')
                       == 'saml' and 'data' in plugin_payload, data),
                None
            )['data']
        except KeyError:
            raise Exception("Unable to load credential data. Exiting.")

        if args.profile:
            if args.daemon and args.profile != 'default':
                raise Exception("DaemonModeConfigIssue", "Cannot run daemon mode with a custom profile.")
            profile_name = args.profile
        else:
            profile_name = 'default'

        awscli_dir = "{0}/.aws".format(os.path.expanduser('~'))
        awscli_credentials_filename = "{0}/credentials".format(awscli_dir)

        config = configparser.ConfigParser()

        config.read(awscli_credentials_filename)

        # If there are default credentials existing that are not managed by Cloudtoken then back them up.
        if not args.profile:
            if 'default' in config:
                if not config['default'].getboolean('cloudtoken'):
                    config['default_backup'] = copy.copy(config['default'])

        aws_cli_data = {
            'aws_access_key_id': credentials["AccessKeyId"],
            'aws_secret_access_key': credentials["SecretAccessKey"],
            'aws_session_token': credentials["Token"],
            'cloudtoken': 'true'
        }
        if args.daemon:
            config[profile_name] = {}
        else:
            config[profile_name] = collections.OrderedDict(sorted(aws_cli_data.items(), key=lambda t: t[0]))

        if not os.path.exists(awscli_dir):
            os.makedirs(awscli_dir)

        with open(awscli_credentials_filename, 'w') as fh:
            config.write(fh)
            os.chmod(awscli_credentials_filename, 0o600)

        data.append({'plugin': self._name, 'data': credentials})
        return data
