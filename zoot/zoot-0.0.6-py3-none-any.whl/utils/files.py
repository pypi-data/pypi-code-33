import json, os, sys

from importlib import util

from types import FunctionType, ModuleType
from typing import Dict, List, Callable

def parse_json(path_to_file:str, *defaults:str):

    try:
        with open(path_to_file) as f:
            data = json.load(f)
            for default in defaults:
                if default not in data:
                    raise Exception("{} expected parameter not found in json".format(default))
            return data
    except IOError:
        raise Exception("could not parse json")

def find_files(path:str, *extensions:str) -> Dict[str, str]:
    found_files = {}

    for root, _, files in os.walk(path):

        for file in files:
            if file.endswith(tuple(extensions)):
                found_files[file] = os.path.join(root, file)

    return found_files


def load_modules_ordered(modules:Dict[str, str], order:List[str]) ->List[ModuleType]:

    loaded_modules = []

    for item in order:
         if item in modules:
              loaded_modules.append(load_module(item, modules[item]))
    print("ordered modules: ")
    print(loaded_modules)
    return loaded_modules

def load_modules(modules:Dict[str, str]) -> List[ModuleType]:
    
    loaded_modules = []

    for name, path in modules.items():
        loaded_modules.append(load_module(name, path))

    print("modules: ")
    print(loaded_modules)
    return loaded_modules

def load_module(name:str, path:str) -> ModuleType:

    if name.endswith('.py'):
        file_parts = name.split(".")
        del file_parts[len(file_parts)-1:]
        name = ".".join(file_parts)

    spec = util.spec_from_file_location(name, path)
    module = util.module_from_spec(spec)
    if spec.name not in sys.modules:
        sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module

