import sys

from irori.executors import Executor
from .base import Rule
from irori.context import build
from irori.context import runtime


class SuffixRule(Rule):
    def __init__(self, rules=None, **kw_rules):
        super(SuffixRule, self).__init__()
        if rules is None:
            rules = {}
        rules.update(kw_rules)

        self.__rules = {suffix.strip('/\\.'): rule for suffix, rule in rules.items()}

    def initialize(self, context: build.BuildContext):
        super(SuffixRule, self).initialize(context)
        for rule in self.__rules.values():
            rule.initialize(context)

    def execute(self, context: runtime.RuntimeContext, executor: Executor):
        outputs = []
        while context.is_remaining:
            suffix = context.next.suffix.strip('/\\.')
            if suffix in self.__rules:
                outputs.extend(self.__rules[suffix].execute(context, executor))
            else:
                print('unknown suffix: {}, file name: {}'.format(suffix, context.consume()[0]), file=sys.stderr)
        executor.wait_all()

        return outputs
