import importlib.util
import os


def load_plugin_modules(plugin_files, debug=False):
    modules = []
    for path in plugin_files:
        if os.path.isdir(path):
            path = os.path.join(path, "__init__.py")

        spec = importlib.util.spec_from_file_location("module", path)
        module = importlib.util.module_from_spec(spec)

        try:
            spec.loader.exec_module(module)
            modules.append(module)
        except Exception as e:
            if debug:
                raise e
            print(e)
            continue

    return modules
