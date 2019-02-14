"""
Here we wrap usage of the lettuce world object for ease of porting
"""

from lettuce import world as _world

from fattoush.config import deprecated


def _world_attr(name, doc=None):
    return property(
        fget=lambda _: getattr(_world, name),
        fset=lambda _, value: setattr(_world, name, value),
        fdel=lambda _: delattr(_world, name),
        doc=doc
    )


class _Per(object):
    scenario = _world_attr('per_scenario')


class _World(object):
    @deprecated.FromVersion('1.0', 'Direct access prevents migration')
    def __getattr__(self, item):
        return getattr(_world, item)

    @deprecated.FromVersion('1.0', 'Direct access prevents migration')
    def __setattr__(self, key, value):
        return setattr(_world, key, value)

    @deprecated.FromVersion('1.0', 'Direct access prevents migration')
    def __delattr__(self, item):
        return delattr(_world, item)


per = _Per()
world = _World()
config = None
