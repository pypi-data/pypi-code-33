import argparse
import hashlib
import logging
import os

import pyftpdlib.authorizers
import pyftpdlib.handlers
import pyftpdlib.servers

LOG_LEVELS = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG,
}


class SHA256Authorizer(pyftpdlib.authorizers.DummyAuthorizer):

    def validate_authentication(self, username, password, handler):
        # pyftpdlib/authorizers.py", line 110, in add_user
        #   dic = {'pwd': str(password),
        # so we can not compare against .digest()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if self.user_table[username]['pwd'] != password_hash.lower():
            raise pyftpdlib.authorizers.AuthenticationFailed()


def serve(root_dir_path, username, password_sha256_hexdigest,
          control_port, passive_port, passive_address, umask, log_level):
    logging.basicConfig(level=log_level)
    if umask:
        os.umask(umask)
        logging.info('umask=0o%o', umask)
    assert os.path.isdir(root_dir_path), root_dir_path
    authorizer = SHA256Authorizer()
    authorizer.add_user(
        username,
        password_sha256_hexdigest.lower(),
        homedir=root_dir_path,
        # https://pyftpdlib.readthedocs.io/en/latest/api.html#pyftpdlib.authorizers.DummyAuthorizer.add_user
        # e: change dir
        # m: mkdir
        # w: write
        perm='emw',
        msg_login='renshi ni hen gaoxing',
        msg_quit='zaijian',
    )
    handler = pyftpdlib.handlers.FTPHandler
    handler.authorizer = authorizer
    handler.banner = 'ni hao'
    handler.passive_ports = (passive_port,)
    handler.masquerade_address = passive_address
    server = pyftpdlib.servers.FTPServer((None, control_port), handler)
    # apparently requires +1 for unknown reasons
    server.max_cons = 1 + 1
    server.serve_forever()


class EnvDefaultArgparser(argparse.ArgumentParser):

    def add_argument(self, *args, envvar=None, **kwargs):
        if envvar:
            envvar_value = os.environ.get(envvar, None)
            if envvar_value:
                kwargs['required'] = False
                kwargs['default'] = envvar_value
        super().add_argument(*args, **kwargs)


def _init_argparser():
    argparser = EnvDefaultArgparser()
    argparser.add_argument(
        '--root', '--root-dir',
        metavar='path',
        dest='root_dir_path',
        default=os.getcwd(),
        help='default: current working directory',
    )
    argparser.add_argument(
        '--user', '--username',
        metavar='username',
        dest='username',
        required=True,
        envvar='FTP_USERNAME',
        help='default: env var $FTP_USERNAME',
    )
    argparser.add_argument(
        '--pwd-hash', '--password-hash',
        metavar='sha256_hexdigest',
        dest='password_sha256_hexdigest',
        required=True,
        envvar='FTP_PASSWORD_SHA256',
        help='default: env var $FTP_PASSWORD_SHA256',
    )
    argparser.add_argument(
        '--ctrl-port', '--control-port',
        metavar='port',
        type=int,
        dest='control_port',
        envvar='FTP_CONTROL_PORT',
        default=2121,
        help='default: env var $FTP_CONTROL_PORT or 2121',
    )
    argparser.add_argument(
        '--pasv-port', '--passive-port',
        metavar='port',
        type=int,
        dest='passive_port',
        envvar='FTP_PASSIVE_PORT',
        default=62121,
        help='port for passive (PASV) & extended passive (EPSV) mode;'
        + ' default: env var $FTP_PASSIVE_PORT or 62121',
    )
    argparser.add_argument(
        '--pasv-addr', '--passive-address', '--masquerade-address',
        metavar='ip_address',
        dest='passive_address',
        envvar='FTP_PASSIVE_ADDRESS',
        default=None,
        help='address returned to client (227)'
        + ' after opening port for passive mode (PASV)'
        + ' default: socket\'s own address',
    )
    argparser.add_argument(
        '--umask',
        type=int,
        envvar='UMASK',
        default=' default: env var $UMASK',
    )
    argparser.add_argument(
        '--log-level',
        metavar='level_name',
        dest='log_level_name',
        default='info',
        choices=LOG_LEVELS.keys(),
        help='default: %(default)s',
    )
    return argparser


def main():
    args = _init_argparser().parse_args()
    args.log_level = LOG_LEVELS[args.log_level_name]
    del args.log_level_name
    serve(**vars(args))
