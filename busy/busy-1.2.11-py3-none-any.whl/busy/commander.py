from argparse import ArgumentParser
from tempfile import TemporaryDirectory
import sys
from tempfile import TemporaryFile
from pathlib import Path
import importlib
import re

from .root import Root
from . import PYTHON_VERSION
import busy


MESSAGE = "Busy requires Python version %i.%i.%i or higher"


class Commander:

    def __init__(self, *args, root=None):
        if sys.version_info < PYTHON_VERSION:
            raise RuntimeError(MESSAGE % PYTHON_VERSION)
        # if root:
        self.root = Root(root)

    def handle(self, *args):
        parsed, remaining = self._parser.parse_known_args(args)
        parsed.criteria = remaining
        if parsed.root:
            self.root = Root(parsed.root)
        if hasattr(parsed, 'command'):
            command = parsed.command(self.root)
            result = command.execute(parsed)
            command.save()
            return result

    @property
    def root(self):
        # if not hasattr(self, '_root'):
        #     self._root = Root()
        return self._root

    @root.setter
    def root(self, value):
        assert not hasattr(self, '_path')
        assert isinstance(value, Root)
        self._root = value

    @classmethod
    def register(self, command_class):
        if not hasattr(self, '_parser'):
            self._parser = ArgumentParser()
            self._parser.add_argument('--root', action='store')
            self._subparsers = self._parser.add_subparsers()
        subparser = self._subparsers.add_parser(command_class.command)
        subparser.set_defaults(command=command_class)
        command_class.register(subparser)


class Command:

    def __init__(self, root):
        self._root = root

    def _list(self, queue, tasklist):
        fmtstring = "{0:>6}  " + queue.itemclass.listfmt
        texts = [fmtstring.format(i, t) for i, t in tasklist]
        return '\n'.join(texts)

    def save(self):
        self._root.save()

    def is_confirmed(self, parsed, itemlist, verb, noun):
        if hasattr(parsed, 'yes') and parsed.yes:
            confirmed = True
        else:
            print('\n'.join([str(i[1]) for i in itemlist]))
            confirmed = input(f'{verb}? (Y/n) ').startswith('Y')
        if not confirmed:
            print(f"{noun} must be confirmed")
        return confirmed


class QueueCommand(Command):

    @classmethod
    def register(self, parser):
        parser.add_argument('--queue', nargs=1, dest="queue")

    def execute(self, parsed):
        key = parsed.queue[0] if getattr(parsed, 'queue') else None
        queue = self._root.get_queue(key)
        return self.execute_on_queue(parsed, queue)

    def execute_on_queue(self, parsed, queue):
        method = getattr(queue, self.command)
        result = method(*parsed.criteria)
        return result


for folder in ['commands', 'plugins']:
    plugins_dir = Path(__file__).parent / folder
    for plugin_file in plugins_dir.iterdir():
        if re.match(r'^[^_].*\.py$', plugin_file.name):
            importlib.import_module(f'busy.{folder}.{plugin_file.stem}')
