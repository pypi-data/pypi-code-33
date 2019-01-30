import os
import platform
import sys
import time
import OpenSSL
import logging
import argparse
import requests

from requests.packages.urllib3.exceptions import InsecureRequestWarning

from v_bootstrap.onboard.board import Board, BoardVirtual, Config
from v_bootstrap.utils import security, yes_no, get_serial_devices
from v_bootstrap.utils.logs import init_bootstrap_log
from v_bootstrap.utils.errors import OnBoardingError, DeviceRegisterError

logger = logging.getLogger(__name__)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

_REGISTER_HOST = 'aoscloud.io'
_REGISTER_PORT = 10000
_REGISTER_URI_TPL = 'https://{}:{}/api/v1/vehicles/provisioning/'

_COMMAND_BOARD_WHICH = 'board'
_COMMAND_VIRTUAL_BOARD_WHICH = 'virt-board'


class SubParserHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def _format_action(self, action):
        """ Handles sub commands. """
        s_class = super(argparse.RawDescriptionHelpFormatter, self)
        parts = s_class._format_action(action)

        if action.nargs == argparse.PARSER:
            parts = "\n".join(parts.split("\n")[1:])

        return parts


def _parse_args():
    def _validate_file(source):
        """ Validates an identity file. """
        if not os.path.isfile(source):
            mess = "Identity file {} not accessible."
            raise argparse.ArgumentTypeError(mess.format(source))

        return source

    parser = argparse.ArgumentParser(
        description="The board provisioning tool",
        formatter_class=SubParserHelpFormatter,
        epilog="Run 'v-bootstrap COMMAND --help' for more information on a command.")
    parser.set_defaults(which=None)

    parser.add_argument('--register-host', default=_REGISTER_HOST,
                        help="Host address to register. Default: {}".format(
                            _REGISTER_HOST))
    parser.add_argument('--register-port', default=_REGISTER_PORT,
                        help="Port to register. Default: {}".format(
                            _REGISTER_PORT))
    parser.add_argument(
        '--cert', default=security.default_cert(), type=_validate_file,
        help="Certificate file. Default: {}".format(security.default_cert()))

    parser.add_argument(
        '-u', '--user', default='root',
        help="Specifies the user to log in as on the remote board.")
    parser.add_argument('-p', '--password',
                        default='Password1', help="User password.")

    # Commands
    sub_parser = parser.add_subparsers(title='Commands')

    # Board
    board = sub_parser.add_parser(
        _COMMAND_BOARD_WHICH,
        help='Launch a board provisioning procedure.')

    board.add_argument('--serial-port', default=None,
                            help="Board serial port (optional).")

    board.set_defaults(which=_COMMAND_BOARD_WHICH)

    # Virtual board
    virt_board = sub_parser.add_parser(
        _COMMAND_VIRTUAL_BOARD_WHICH,
        help='Launch a virtual board provisioning procedure.')

    virt_board.add_argument('--host', default='127.0.0.1',
                            help="Virtual board host name or IP. Default: 127.0.0.1")
    virt_board.add_argument('--port', default=2222,
                            help="Virtual board port. Default: 2222")

    virt_board.set_defaults(which=_COMMAND_VIRTUAL_BOARD_WHICH)

    args = parser.parse_args()
    if args.which is None:
        parser.print_help()

    return args


def _detect_device(ports):
    """ Detects a new device. """
    ports = set(ports)
    while True:
        new_devs = list(get_serial_devices())
        new_ports = set([d.device for d in new_devs])
        detected = ports ^ new_ports

        if detected:
            port = detected.pop()
            for d in new_devs:
                if d.device == port:
                    return d

        time.sleep(.5)


def _register_device(end_point, cert, payload):
    """ Registers device in cloud. Returns registered metadata.
    :param: str - end_point for registering
    :param: str - path to server pem that contains certs and a private one
    :param: dict
    :return: dict
    """
    logger.info("Registering the board ...")

    try:
        ret = requests.post(end_point, data=payload,
                            verify=False, cert=cert)
        ret.raise_for_status()
        response = ret.json()
    except (requests.exceptions.RequestException,
            ValueError, OSError, OpenSSL.SSL.Error) as e:
        logger.debug(e)
        raise DeviceRegisterError("Failed to register board.")

    return response


def main(board, register_host, register_port, cert):
    """ Launches the bootstrapping procedure. """
    log_file = init_bootstrap_log()
    logger.info("Starting the provision procedure ... "
                "find the whole log info in %s", log_file)

    try:
        cfg = Config()

        with board() as b:
            # obtain a hardware secure ID
            cfg.hw_id = b.get_hw_id()
            logger.info("HW ID={}".format(cfg.hw_id))

            # generate a key pair
            pkeys = b.generate_pkeys()
            cfg.set_keys(pkeys)

        # register the device
        ep = _REGISTER_URI_TPL.format(register_host, register_port)
        payload = {
            'hardware_id': cfg.hw_id,
            'online_public_key': cfg.get_public_online(),
            'offline_public_key': cfg.get_public_offline()
        }
        server_cert = security.merge_certs(cert)
        res = _register_device(ep, server_cert, payload)

        cfg.vin = res.get('vin')
        cfg.online_certificate = res.get('online_certificate')
        cfg.offline_certificate = res.get('offline_certificate')
        cfg.user_claim = res.get('claim')
        cfg.model = res.get('model')
        cfg.manufacturer = res.get('manufacturer')

        cfg.validate()

        # configure the board
        with board() as b:
            b.configure(cfg)

        logger.info("Vehicle with VIN:%s has registered successfully.", cfg.vin)
    except OnBoardingError as e:
        logger.error('\nUnable to provision the board:\n%s', str(e))
        return 1
    except KeyboardInterrupt:
        logger.info('\nExiting ...')
        return 1

    return 0


def _init_board(board, *args, **kwargs):
    """ Initializes a board instance. """

    def _wrap():
        return board(*args, **kwargs)

    return _wrap


def _check_access_to_serial_ports():
    if platform.system() != "Linux":
        return True

    if os.getuid() == 0:
        # We run under sudo or root
        return True

    import grp
    import subprocess

    user_name = os.getlogin()
    user_groups = [g.gr_name for g in grp.getgrall() if user_name in g.gr_mem]

    if 'dialout' not in user_groups:
        # We need to add current user to group dialout
        # Check for rights for sudo
        if 'sudo' not in user_groups:
            sys.stdout.write('In Linux to access to serial ports you should be in group "dialout".\n'
                             'Contact your system administrator to add you to the group\n')
            raise AssertionError

        sys.stdout.write('Try to add your username to the "dialout" group using sudo.\n'
                         'Please enter your password if it will be asked\n')

        cmd = "sudo usermod -a -G dialout {}".format(user_name)
        ret_code = subprocess.call(cmd, shell=True, stdout=sys.stdout, stdin=sys.stdin, stderr=sys.stderr)
        if ret_code:
            logger.error("Error adding user to dialout group")
            raise AssertionError
        logger.info("User successful added to dialout group")
        sys.stdout.write("User successful added to dialout group\n")

    # get dialout group id
    dialout_group_id = int(grp.getgrnam('dialout')[2])

    if dialout_group_id not in os.getgroups():
        # We need to restart script with su - tuk

        sys.stdout.write('Before rights to dialout will be accessible you should relogin.\n'
                         'Now new shell session will be started (this may asks you for password one more time\n')

        python_cmd = sys.executable
        args = ["-i", "-g", "dialout", "-u", user_name, python_cmd, *sys.argv]
        ret_code = subprocess.call(args, executable="sudo", shell=False, stdout=sys.stdout, stdin=sys.stdin, stderr=sys.stderr)
        sys.exit(ret_code)

    return True


def run_cli():
    """ The main entry point. """
    status = 0
    args = _parse_args()

    board = None
    cred = args.user, args.password

    try:
        if not security.keys_exist():
            sys.stdout.write('Failed to find a key pair '
                             'in {}.\n'.format(security.get_security_dir()))
            raise AssertionError

        if args.which == _COMMAND_BOARD_WHICH:
            _check_access_to_serial_ports()

            serial_port_name = args.serial_port

            if serial_port_name is None:

                mess = "Please make sure that device is not plugged in.\n" \
                       "Unplug device before continue"
                if not yes_no(mess, "yes"):
                    raise AssertionError

                devices = get_serial_devices()
                sys.stdout.write("Please plug-in device. Waiting for ...\n")

                ports = [d.device for d in devices]
                dev = _detect_device(ports)

                mess = "{} device detected. Continue:".format(str(dev))
                if not yes_no(mess):
                    raise AssertionError

                mess = "Please, switch on your device \n" \
                       "  using the button near the sticker 'StarterKit'\n" \
                       "  and wait for 5 seconds, then press 'y'\n"
                if not yes_no(mess):
                    raise AssertionError

                board = _init_board(Board, dev.device, cred)

            else:
                board = _init_board(Board, serial_port_name, cred)

        elif args.which == _COMMAND_VIRTUAL_BOARD_WHICH:
            board = _init_board(BoardVirtual, args.host, args.port, cred)
    except (AssertionError, KeyboardInterrupt):
        sys.stdout.write('Exiting ...\n')
        status = 1

    if board:
        status = main(board, args.register_host,
                      args.register_port, args.cert)

    sys.exit(status)


if __name__ == '__main__':
    run_cli()
