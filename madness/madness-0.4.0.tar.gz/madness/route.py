

from dataclasses import dataclass, field
from typing import Callable, List, Tuple

from more_itertools import collapse
from werkzeug.routing import Rule

from .context import bind



@dataclass
class Route():
    """
    path does not begin with a leading slash
    """
    path: str
    endpoint: Callable
    methods: List[str] = field(default_factory=list)
    context: List = field(default_factory=list)

    @property
    def rule(self) -> Rule:
        return Rule(
            f'/{self.path}',
            endpoint = bind(self.endpoint, self.context_decorators),
            methods = self.methods or None
        )

    @property
    def context_decorators(self) -> Tuple:
        """
        """
        return tuple(collapse(self.context))

    def __repr__(self):
        context = ','.join([func.__qualname__ for func in self.context_decorators])
        if context:
            context = f'-> @({context})'
        methods = ','.join(self.methods)
        if methods:
            methods = f'[{methods}]'
        parts = ' '.join(
            filter(
            bool, (
            self.__class__.__name__,
            f'/{self.path}',
            methods,
            context,
            f'-> {self.endpoint.__qualname__}',
        )))
        return f'<{parts}>'
