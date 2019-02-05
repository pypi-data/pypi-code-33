from types import MappingProxyType
from functools import lru_cache


@lru_cache()
def __getattr__(name):
    ids = MappingProxyType(dict(
        code = MappingProxyType(dict(
            short_name="c",
            default="demo",
            help="Code name to identify contributions on a given project.",
        )),
        env = MappingProxyType(dict(
            short_name="e",
            default="3d",
            help="Environment of a project, e.g. 'film', 'vr', 'ar'.",
        )),
        cluster = MappingProxyType(dict(
            short_name="cl",
            default="abc",
            help="Cluster of data type existing in a contribution, e.g. 'geo', 'audio', 'video'.",
        )),
        kind = MappingProxyType(dict(
            short_name="k",
            default="component",
            help="Higher level classification of contributions, e.g. 'component', 'subcomponent', 'prop'.",
        )),
        area = MappingProxyType(dict(
            short_name="a",
            default="rnd",
            help="Area in the creative process owning the contribution. Usually related to departments.",
        )),
        branch = MappingProxyType(dict(
            short_name="b",
            default="master",
            help="Branch where the contribution is being worked on (e.g. git workflow: 'master', 'develop').",
        )),
        item = MappingProxyType(dict(
            short_name="i",
            default="atom",
            help="Atomic unit of a contribution that makes sense on its own as a whole.",
        )),
        step = MappingProxyType(dict(
            short_name="s",
            default="main",
            help="Inner process of the current `area` during the life cycle of a contribution.",
        )),
        variant = MappingProxyType(dict(
            short_name="v",
            default="all",
            help="Variation expressing a different intent of the current `item`.",
        )),
        part = MappingProxyType(dict(
            short_name="p",
            default="whole",
            help="Partition of the current `variation` / `item`.",
        )),
    ))
    if name == 'IDS':
        return ids
    elif name in ids:
        return ids[name]
    raise AttributeError(f"module {__name__} has no attribute {name}")


def __dir__():
    return ['IDS', *__getattr__('IDS')]
