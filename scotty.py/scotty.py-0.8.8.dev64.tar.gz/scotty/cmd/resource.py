import logging

from enum import Enum

from scotty.cmd.base import CommandParser
from scotty.cmd.base import CommandRegistry
from scotty.workflows.resource import ResourceInitWorkflow
from scotty.core.exceptions import ScottyException

logger = logging.getLogger(__name__)


class CommandAction(Enum):
    init = 'init'


@CommandRegistry.parser
class ResourceParser(CommandParser):
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(help='Action', dest='action')
        initparser = subparsers.add_parser(CommandAction.init.name)
        InitParser().add_arguments(initparser)


class InitParser(CommandParser):
    def add_arguments(self, parser):
        parser.add_argument(
            'name',
            metavar='name',
            type=str,
            help="Name for the resource")


@CommandRegistry.command
class Command(object):
    def __init__(self, options):
        self.options = options

    def execute(self):
        commandAction = CommandAction(self.options.action)
        if commandAction is CommandAction.init:
            try:
                workflow = ResourceInitWorkflow(self.options)
                workflow.run()
            except ScottyException as err:
                logger.error(err)
