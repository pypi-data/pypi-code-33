"""
Encrypts secrets using kms key wrapping.

Usage:
  add_secrets_user --env env_name gpg_user_id

Options:
  -e --env=<env name>          the name of the environment (i.e., if you want to use multiple encryption keys)
  gpg_user_id                  the id of the user in the user's gpg public key

n.b., the gpg key of the user you are adding as a secrets user must
      have already been imported into your keyring
"""
from argparse import ArgumentParser
from base64 import b64encode
import os
import sys
from djenga.encryption.helpers import _prefix_alias
from djenga.encryption.helpers import _get_client
from djenga.utils.print_utils import notice
from djenga.utils.print_utils import notice_end
from gnupg import GPG
from git import Repo
import subprocess


def get_parser():
    parser = ArgumentParser()
    parser.add_argument(
        '-e', '--env',
        dest='env',
        metavar='<env_name>',
        help='the name of the environment for the user',
        required=True,
    )
    parser.add_argument(
        'user_id',
        metavar='<user_id>',
        help='the user_id associated with the gpg public key '
             'of the user that will be given access to the secrets ',
    )
    return parser


def add_local_key(gpg, dir_name, data_key, fingerprint):
    notice('generating local key')
    filename = os.path.join(dir_name, fingerprint)
    gpg.encrypt(data_key, fingerprint, armor=True, output=filename)
    notice_end()
    return filename


def git_commit(*filenames, message: str):
    notice('commit to git')
    repo = Repo('.')
    repo.index.add(filenames)
    repo.index.commit(message=message)
    notice_end()


def validate_gpg():
    notice('validating gpg setup')
    home = os.environ.get('HOME')
    gpg_home = os.path.join(home, '.gnupg')
    gpg = GPG(homedir=gpg_home, use_agent=True)
    secret_keys = gpg.list_keys(secret=True)
    if not secret_keys:
        notice_end('uninitialized')
        print('It looks like you have not created a '
              'gpg private key for yourself.')
        sys.exit(1)
    notice_end()
    return gpg, secret_keys[0]


def find_gpg_key(gpg, user_id):
    keys = gpg.list_keys()
    user_id = f'<{user_id}>'
    for x in keys:
        for uid in x['uids']:
            if user_id in uid:
                return x['fingerprint']
    return None


def main():
    parser = get_parser()
    args = parser.parse_args()
    dir_name = os.path.join('.secrets', args.env)
    gpg, gpg_secret_key = validate_gpg()
    fingerprint = gpg_secret_key['fingerprint']
    my_data_key = os.path.join('.secrets', args.env, fingerprint)
    process = subprocess.run(
        ['--no-tty', '--no-emit-version', '-d', my_data_key ],
        executable=gpg.binary, stdout=subprocess.PIPE,
    )
    data_key = process.stdout

    notice(f'checking keyring for {args.user_id}')
    fingerprint = find_gpg_key(gpg, args.user_id)
    if not fingerprint:
        notice_end('not found', color='red')
        sys.exit(1)
    notice_end()
    my_filename = add_local_key(gpg, dir_name, data_key, fingerprint)
    uid = gpg_secret_key['uids'][0]
    message = f'[secrets]  {uid} added user {args.user_id} to {args.env}'
    git_commit(my_filename, message=message)


if __name__ == "__main__":
    main()
