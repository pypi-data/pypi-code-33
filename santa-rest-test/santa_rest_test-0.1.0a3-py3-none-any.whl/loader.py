import yaml
import os

from santa.context import Context
from santa.suite import Suite


class LoadError(Exception):
    pass

async def load_context(name):
    "load a context from its name"
    base_dir = os.path.join(os.curdir, "context")
    path = os.path.join(base_dir, name + ".yml")
    with open(path, 'r') as f:
        ctx = Context(f)
    extends = ctx.get("extends")
    if extends is not None:
        overlay = ctx
        ctx = await load_context(extends)
        ctx.update(overlay)
    return ctx


async def load_suite(name):
    tries = []
    path = os.path.join("suite", name)
    if os.path.isdir(path):
        path = os.path.join(path, "__main__")
    for ext in (".yaml", ".yml"):
        tried = path + ext
        if os.path.exists(tried) and os.path.isfile(tried):
            break
        tries.append(tried)
    else:
        raise LoadError("Can't find suite `%s`. Path searched: '%s'" % (name, tries))
    with open(tried, 'r') as f:
        data = yaml.load(f)
    s = Suite(data)
    s.__file__ = tried
    return s
