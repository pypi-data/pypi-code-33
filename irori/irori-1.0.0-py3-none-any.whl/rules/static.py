import pathlib
import typing

from . import base
from irori.context import build
from irori.context import runtime
from irori.executors import Executor
from irori import depend


def _convert_command_2nd(command: str):
    return command.replace('$@', '{output}')


def _convert_command_1st(command: str, default):
    if command is None:
        return default
    return command.replace('$<', '{dependency}').replace('$^', '{dependencies}')


def _latest_deps_time(output, dependencies: typing.List[pathlib.Path], deps: depend.Dependencies):
    lt = deps.latest_time(output)
    return max(lt, max([depend.get_modified_time(str(f)) for f in dependencies]))


def single_output_name_converter(context: build.BuildContext, dependencies: typing.List[pathlib.Path]):
    context.object_directory.mkdir(parents=True, exist_ok=True)
    return '{}/{}.o'.format(context.object_directory, dependencies[0].name)


def build_target(context: build.BuildContext, _: typing.List[pathlib.Path]):
    return context.output_file


class StaticRule(base.Rule):
    def __init__(
            self, command=None, debug=None, release=None,
            output_name_converter=single_output_name_converter, force=False):
        super(StaticRule, self).__init__()
        self.__command = _convert_command_1st(command, '')
        self.__debug = _convert_command_1st(debug, '')
        self.__release = _convert_command_1st(release, '')
        self.__output_name_converter = output_name_converter
        self.__force = force

    def initialize(self, context: build.BuildContext):
        super(StaticRule, self).initialize(context)
        self.__command += ' '
        self.__command += self.__debug if context.is_debug else self.__release

    def execute(self, context: runtime.RuntimeContext, executor: Executor):
        command = self.__command
        if '{dependency}' in command:
            dependencies = context.consume()
            command = command.format(dependency=dependencies[0])
        elif '{dependencies}' in command:
            dependencies = context.consume_all()
            command = command.format(dependencies=' '.join([str(dep) for dep in dependencies]))
        else:
            dependencies = []
            command = command
        command = _convert_command_2nd(command)

        output = self.__output_name_converter(self.context, dependencies)

        if _latest_deps_time(output, dependencies, self.context.dependencies) > depend.get_modified_time(output):
            command = command.format(output=output)
            executor.start_process(command)
            print('execute: {}'.format(command))
        else:
            print('skipped: {}'.format(output))

        return [output]
