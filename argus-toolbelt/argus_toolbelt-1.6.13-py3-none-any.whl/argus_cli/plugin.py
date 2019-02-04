import imp
from os.path import splitext, basename, exists
from glob import glob

from argus_cli import arguments
from argus_cli.helpers.formatting import to_caterpillar_case
from argus_cli.helpers.log import log


def register_command(alias: str = None, extending: tuple = None) -> callable:
    """Decorator used to register commands to a plugin

    :param alias: If the user wants a custom name on the plugin
    :param extending: A existing plugin to extend
    """
    extending = (extending,) if isinstance(extending, str) else extending

    def decorate(func):
        # Rename all plugins and commands to caterpillar-case-format to conform to common cli naming.
        plugin_name = tuple(map(to_caterpillar_case, extending or (func.__module__,)))
        command_name = to_caterpillar_case(alias or func.__name__)

        arguments.register_command(plugin_name, command_name, func)

        return func

    return decorate


def get_plugin_modules(locations: list) -> list:
    """Loads plugins from default plugin location and user defined plugin location,
    and attempts to load them as python modules.

    Directories can be loaded, provided they are python packages, i.e containing an __init__.py file.
    If a plugin is defined as a Python package with an __init__.py file, this file must export
    all functions decorated with `@register_command`, since these will be registered on import, and
    only the __init__.py will be initially imported.

    NOTE: Renames plugins to common unix command naming scheme

    :param list locations: Folder with plunspgins
    :rtype: list
    :returns: A list of python files with paths
    """
    modules = []

    for path in locations:
        log.debug("Loading plugins from %s..." % path)

        if not exists(path):
            log.warning("Plugin directory does not exist: %s" % path)
            continue

        # Load plugins that dont start with __ (__pycache__, __init__, __main__, etc)
        # and force the paths to the filenames
        for plugin in map(basename, glob("%s/[!__]*" % path)):
            log.debug("Extracting plugin metadata from: %s" % plugin)

            # Get the file without file extension
            module_name, file_ending = splitext(plugin)

            if file_ending and not file_ending.startswith(".py"):
                continue

            try:
                # Explicitly show the return types, to avoid confusion:
                file_reference, path_to_file, file_information = imp.find_module("%s" % module_name, [path])
            except ImportError:
                log.critical("Could not load module: %s (%s)" % (module_name, path))
                continue

            log.debug("Loaded plugin %s" % module_name)
            modules.append({
                "name": module_name,
                "info": (file_reference, path_to_file, file_information)
            })

    return modules


def load_plugin_module(plugin: dict) -> bool:
    """Loads a plugin

    :param dict plugin: A dict with the module name and info
    :returns: True if module was successfully loaded
    :rtype: bool
    """
    log.debug("Loading plugin: %s" % plugin["name"])

    try:
        imp.load_module(plugin["name"].replace("-", "_"), *plugin["info"])
    except Exception:
        log.exception("Error while loading plugin module %s:" % plugin["name"])
        return False
    finally:
        if plugin["info"][0]:
            plugin["info"][0].close()

    return True
