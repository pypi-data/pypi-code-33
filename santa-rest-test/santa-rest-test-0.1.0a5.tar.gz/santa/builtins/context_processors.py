from santa.context_processor import ContextProcessor
from santa.parser import MappingField
from .fields import ContextValueField


class Update(ContextProcessor):
    '''
    Update context values. Create context path if needed.
    '''
    updates = MappingField()

    def __init__(self, **kwargs):
        self.__fields__ = {}
        self.updates = kwargs

    async def __call__(self, ctx):
        for k, v in self.updates.items():
            ctx.bind(k, ctx.render(v), create=True)


class Copy(ContextProcessor):
    '''
    Copy a context value in another, creating missing path.
    '''
    src = ContextValueField()
    dest = ContextValueField()

    async def __call__(self, ctx):
        ctx.bind(self.dest, ctx.get_path(self.src))
