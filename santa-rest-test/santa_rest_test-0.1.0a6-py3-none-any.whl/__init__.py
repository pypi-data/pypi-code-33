import os
from importlib import import_module


def init(plugin_modules=None):
    # init builtins
    import santa.tasks
    import santa.builtins

    # init plugins
    plugin_modules = plugin_modules if plugin_modules else ["plugins"]
    for p in plugin_modules:
        try:
            plugin = import_module(p)
        except ModuleNotFoundError:
            pass
        else:
            modpath = plugin.__file__
            if os.path.isfile(modpath):
                continue
            else:
                base_path = os.path.dirname(modpath)
                for file in os.listdir(base_path):
                    if file.startswith("__"):
                        continue
                    if file.endswith(".py"):
                        file = file[:-3]
                    import_module(".".join(p, file))
