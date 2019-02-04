from typing import Dict, List, Callable

from zoot.utils import files

import argparse

class Environment():

    def __init__(self, parse_json:bool=True, on_post_build:Callable[[Dict[str, any]], None]=None, *required_args:str, **optional_args:str):
        self.parse_json = parse_json
        self.required_args = []
        self.optional_args = {}
        self.on_post_build = on_post_build

        if required_args:
            for arg in required_args:
                self.required_args.append(arg)
        
        if optional_args:
            for arg, default in optional_args.items():
                self.optional_args[arg] = default
            
    def build(self):

        parser = argparse.ArgumentParser()

        if self.parse_json:

            parser.add_argument("json")
            args, _ = parser.parse_known_args()
            data = files.parse_json(args.json, *self.required_args)

            if self.on_post_build:
                self.on_post_build(data)
                return

        for arg in self.required_args:
            parser.add_argument("--{}".format(arg), required=True)

        for arg in self.optional_args.keys():
            parser.add_argument("--{}".format(args))
        args, _ = parser.parse_known_args()

        arguments = {}

        for arg in self.required_args:
            if hasattr(args, arg):
                arguments[arg] = getattr(args, arg)
            else:
                raise Exception('"{}" argument not found!'.format(arg))

        if self.on_post_build:
            self.on_post_build(arguments)


