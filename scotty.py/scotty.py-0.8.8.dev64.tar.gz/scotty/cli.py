import sys
import argparse

from scotty.cmd.base import CommandRegistry
from scotty.cmd import *


class Cli(object):
    def parse_command(self, args):
        parser = argparse.ArgumentParser(usage="scotty <command> [<args>]")
        subparser = parser.add_subparsers(
            dest='command',
            help='Command')
        subparser.required = True
        for key in CommandRegistry.registry:
            subparser.add_parser(key)
        options = parser.parse_args(args)
        self.command_builder = CommandRegistry.getbuilder(options.command)
        self.command_parser = CommandRegistry.getparser(options.command)
        self.command_class = CommandRegistry.getcommand_class(options.command)
        return options.command

    def parse_command_options(self, args, command):
        parser = argparse.ArgumentParser(usage="scotty {} <action> [<args>]".format(command))
        self.command_parser.add_arguments(parser)
        options = parser.parse_args(args)
        return options

    def execute_command(self, options):
        cmd = self.command_builder.buildCommand(options, self.command_class)
        cmd.execute()


def run(args=sys.argv):
    cli = Cli()
    command = cli.parse_command(args[1:2])
    options = cli.parse_command_options(args[2:], command)
    cli.execute_command(options)
