#!/usr/bin/env python

"""
Command line interface module for OpenTMI client
License: MIT
"""

from __future__ import print_function
import sys
import json
import argparse
import logging
import pkg_resources  # part of setuptools
from opentmi_client.api import OpenTmiClient
from opentmi_client.utils.exceptions import OpentmiException

EXIT_CODE_SUCCESS = 0
EXIT_CODE_NOT_IMPLEMENTED = 1
EXIT_CODE_CONNECTION_ERROR = 60
EXIT_CODE_OPERATION_TIMEOUT = 61
EXIT_CODE_INVALID_PARAMETERS = 62
EXIT_CODE_OPERATION_FAILED = 63


def get_subparser(subparsers, name, func=None, **kwargs):
    """
    Get subparser
    :param subparsers:
    :param name:
    :param func:
    :param kwargs:
    :return: Parser
    """
    tmp_parser = subparsers.add_parser(name, **kwargs)
    if func:
        tmp_parser.set_defaults(func=func)
    return tmp_parser


class OpentTMIClientCLI(object):
    """
    OpenTMICLientCLI
    """

    def __init__(self, args=None):
        """
        Constructor for CLI
        :param args:
        """
        self.console_handler = logging.StreamHandler()
        self.logger = logging.getLogger("opentmi")
        self.logger.handlers = [self.console_handler]
        if args is None:
            args = sys.argv[1:]
        self.args = self.argparser_setup(args)
        self.set_log_level_from_verbose()

    def execute(self):
        """
        Execute
        :return: 0
        """
        if hasattr(self.args, "func") and callable(self.args.func):
            try:
                return self.args.func(self.args)
            except NotImplementedError as error:
                self.logger.error("Not implemented %s", str(error))
                return EXIT_CODE_NOT_IMPLEMENTED
        self.parser.print_usage()
        return EXIT_CODE_SUCCESS

    def argparser_setup(self, sysargs):
        """
        Configure CLI (Command Line Options) options
        :param self:
        :param sysargs:
        :return: Returns OptionParser's tuple of (options, arguments)
        """
        parser = argparse.ArgumentParser()

        parser.add_argument('-v',
                            dest="verbose",
                            action="count",
                            help="verbose level... repeat up to three times.")

        parser.add_argument('-s', '--silent',
                            dest="silent", default=False,
                            action="store_true",
                            help="Silent - only errors will be printed")

        parser.add_argument('--host',
                            dest='host',
                            default='localhost',
                            help='OpenTMI host, default: localhost')

        parser.add_argument('--user',
                            dest='user',
                            default=None,
                            help='username')

        parser.add_argument('--password',
                            dest='password',
                            default=None,
                            help='password')

        parser.add_argument('--token',
                            dest='token',
                            default=None,
                            help='Authentication token')

        parser.add_argument('--token_service',
                            dest='token_service',
                            default=None,
                            help='Optional authentication service')

        parser.add_argument('-p', '--port',
                            dest='port',
                            type=int,
                            default=0,
                            help='OpenTMI port')

        subparsers = parser.add_subparsers(title='subcommand',
                                           help='sub-command help',
                                           metavar='<subcommand>')
        get_subparser(subparsers, 'version',
                      func=self.subcmd_version_handler,
                      help='Display version information')

        parser_list = get_subparser(subparsers, 'list',
                                    func=self.subcmd_list_handler,
                                    help='List something')

        parser_list.add_argument('--json',
                                 dest='json',
                                 default=False,
                                 action='store_true',
                                 help='results as json')

        parser_list.add_argument('--testcases',
                                 dest='testcases',
                                 action='store_true',
                                 default=None,
                                 help='Testcases')

        parser_list.add_argument('--campaigns',
                                 dest='campaigns',
                                 action='store_true',
                                 default=None,
                                 help='Campaigns')

        parser_list.add_argument('--builds',
                                 dest='builds',
                                 action='store_true',
                                 default=None,
                                 help='Builds')

        parser_store = get_subparser(subparsers, 'store',
                                     help='Create something')

        subsubparsers = parser_store.add_subparsers(title='subcommand',
                                                    help='sub-command help',
                                                    metavar='<subcommand>')

        parser_store_testcase = get_subparser(subsubparsers, 'testcase',
                                              func=self.subcmd_store_testcase,
                                              help='Store Testcase')
        parser_store_testcase.add_argument('--file',
                                           dest='file',
                                           default=None,
                                           help='Filename',
                                           type=self.read_json_file,
                                           required=True)

        parser_store_result = get_subparser(subsubparsers, 'result',
                                            func=self.subcmd_store_result,
                                            help='Store Test Result')
        parser_store_result.add_argument('--file',
                                         dest='file',
                                         default=None,
                                         help='Filename',
                                         type=self.read_json_file,
                                         required=True)

        parser_store_build = get_subparser(subsubparsers, 'build',
                                           func=self.subcmd_store_build,
                                           help='Store Build')
        parser_store_build.add_argument('--file',
                                        dest='file',
                                        default=None,
                                        help='Filename',
                                        type=self.read_json_file,
                                        required=True)

        args = parser.parse_args(args=sysargs)
        self.parser = parser
        return args

    def read_json_file(self, filename):
        """
        :param filename: json filename to be read
        :returns: Dict
        """
        try:
            with open(filename) as data_file:
                return json.load(data_file)
        except IOError as error:
            self.logger.error("Given file (%s) is not valid! %s", filename, error)
            raise argparse.ArgumentTypeError(error)

    def set_log_level_from_verbose(self):
        """
        Sets logging level, silent, or some of verbose level
        Args:
             command line arguments
        """
        if self.args.silent or not self.args.verbose:
            self.console_handler.setLevel('ERROR')
            self.logger.setLevel('ERROR')
        elif self.args.verbose == 1:
            self.console_handler.setLevel('WARNING')
            self.logger.setLevel('WARNING')
        elif self.args.verbose == 2:
            self.console_handler.setLevel('INFO')
            self.logger.setLevel('INFO')
        elif self.args.verbose >= 3:
            self.console_handler.setLevel('DEBUG')
            self.logger.setLevel('DEBUG')

    def subcmd_version_handler(self, _args):
        """
        :param self:
        :param _args:
        :return:
        """
        versions = pkg_resources.require("opentmi_client")
        if self.args.verbose:
            for ver in versions:
                print(ver)
        else:
            print(versions[0].version)
        return EXIT_CODE_SUCCESS

    def subcmd_store_handler(self, _args):
        """
        :param self:
        :param _args:
        :return:
        """

        raise NotImplementedError('store')

    @staticmethod
    def create_client(args):
        """
        Create OpenTmiClient instance based on args
        :param args: arguments
        :return: OpenTmiClient instance
        """
        client = OpenTmiClient(host=args.host, port=args.port)
        if args.user:
            if args.password:
                client.login(args.user, args.password)
            else:
                raise OpentmiException("password missing")
        elif args.token:
            service = args.token_service or "github"
            client.login_with_access_token(args.token, service)
        return client

    def subcmd_store_build(self, args):
        """
        :param self:
        :param args:
        :return:
        """
        client = self.create_client(args)
        client.upload_build(args.file)
        return EXIT_CODE_SUCCESS

    def subcmd_store_testcase(self, args):
        """
        :param self:
        :param args:
        :return:
        """
        client = self.create_client(args)
        client.update_testcase(args.file)
        return EXIT_CODE_SUCCESS

    def subcmd_store_result(self, args):
        """
        :param self:
        :param args:
        :return:
        """
        client = self.create_client(args)
        client.upload_results(args.file)
        return EXIT_CODE_SUCCESS

    def subcmd_list_handler(self, args):
        """
        :param args:
        :return:
        """
        client = self.create_client(args)
        if args.testcases:
            testcases = client.get_testcases()
            if args.json:
                print(json.dumps(testcases))
            else:
                print("Test cases:")
                for test_case in testcases:
                    print(test_case['tcid'])
        elif args.campaigns:
            campaigns = client.get_campaign_names()
            if args.json:
                print(campaigns)
            else:
                for campaign in campaigns:
                    print(campaign)
        return 0


def opentmiclient_main():
    """
    Function used to drive CLI (command line interface) application.
    Function exits back to command line with ERRORLEVEL
    Returns:
        Function exits with success-code
    """
    cli = OpentTMIClientCLI()
    try:
        sys.exit(cli.execute())
    except OpentmiException as error:
        print(str(error))
        sys.exit(EXIT_CODE_OPERATION_FAILED)


if __name__ == '__main__':
    opentmiclient_main()
