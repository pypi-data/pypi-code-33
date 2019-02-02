import abc

from irori.context import build
from irori.context import runtime
from irori.executors import Executor


class Rule(abc.ABC):
    def __init__(self):
        self.__build_context = None

    def initialize(self, context: build.BuildContext):
        self.__build_context = context

    @property
    def context(self) -> build.BuildContext:
        return self.__build_context

    @abc.abstractmethod
    def execute(self, context: runtime.RuntimeContext, executor: Executor):
        pass
