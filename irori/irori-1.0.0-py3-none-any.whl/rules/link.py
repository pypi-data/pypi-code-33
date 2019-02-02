import pathlib

from .static import StaticRule, build_target

from irori.context import build
from irori.context import runtime
from irori.executors import Executor


class LinkRule(StaticRule):
    def __init__(self, command=None, debug=None, release=None, rules=None):
        super(LinkRule, self).__init__(
            command=command, debug=debug, release=release, output_name_converter=build_target)
        if rules is None:
            rules = []
        elif not isinstance(rules, list):
            rules = [rules]
        self.__rules = rules

    def initialize(self, context: build.BuildContext):
        super(LinkRule, self).initialize(context)
        for rule in self.__rules:
            rule.initialize(context)

    def execute(self, context: runtime.RuntimeContext, executor: Executor):
        for rule in self.__rules:
            outputs = rule.execute(context, executor)
            executor.wait_all()
            context = runtime.RuntimeContext([pathlib.Path(output) for output in outputs])
        outputs = super(LinkRule, self).execute(context, executor)
        executor.wait_all()

        return outputs
