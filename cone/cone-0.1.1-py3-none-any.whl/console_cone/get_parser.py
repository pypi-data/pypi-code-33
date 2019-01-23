from argparse import ArgumentParser


def add_deploy_command(subparsers):
    deploy_parser = subparsers.add_parser(
        "deploy", help="sync your code to the Roblox place")
    deploy_parser.add_argument('-t', '--tests', action='store_true', dest='include_tests',
                               default=False, help="test files will be sync (default: %(default)s)")
    deploy_parser.add_argument('-o', '--obfuscate', action='store_true',
                               dest='obfuscate', help="obfuscate the files", default=False)


def add_help_command(subparsers):
    subparsers.add_parser("help", help="show this help message and exit")


def add_revert_command(subparsers):
    subparsers.add_parser("revert", help="revert the last deploy")


def add_test_command(subparsers):
    subparsers.add_parser("test", help="sends a request to test your code")


def add_version_command(subparsers):
    subparsers.add_parser("version", help="show the installed version")


def get_parser(parser=None):
    if parser is None:
        parser = ArgumentParser(usage="""
cone <command> options [<args>]

Enter 'cone <command> help' to get help on any specific command
""")
    parser.add_argument("-p", "--port", type=int, nargs=1,
                        default=5000, help="the port where cone will run (default: %(default)s)")
    subparsers = parser.add_subparsers(dest="command", help="valid commands")
    subparsers.required = True

    add_deploy_command(subparsers)
    add_help_command(subparsers)
    add_revert_command(subparsers)
    add_test_command(subparsers)
    add_version_command(subparsers)

    return parser
