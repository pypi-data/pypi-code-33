
import os


class CommandError(ValueError):
    pass


class Command:

    @staticmethod
    def null_func(*args, **kwargs):
        pass

    def __init__(self, name=None):
        if name:
            self._name = name
        else:
            self._name = __class__.name

    def __call__(self, *args, **kwargs):
        pass

    @property
    def name(self):
        return self._name


class EchoCommand(Command):

    def __call__(self, *args, **kwargs):

        print(f"Running: {self._name}({args}, {kwargs})")


class StatCommand(Command):

    def __call__(self, filename):
        return os.stat(filename)


class CommandRunner:

    def __init__(self, command):
        self._commands = {}
        self.add_command(command)

    def add_command(self, command):
        if isinstance(command, Command):
            self._commands[command.name] = command
        else:
            raise CommandError(f"{command} is not an instance of Command")

    def __call__(self, files, *args, **kwargs):
        for i in files:
            for name, cmd in self._commands.items():
                yield cmd(i, *args, **kwargs)
