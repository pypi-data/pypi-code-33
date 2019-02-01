import argparse

from kpc_nifi_utils.common.singleton import singleton


class Args:
    def __init__(self):
        self._parser = ArgumentParserWrapper().get_parser()

    def add(self, *args, **kwargs):
        self._parser.add_argument(*args, **kwargs)
        return self

    def get(self, key):
        args = self._parser.parse_args()
        try:
            return args[key]
        except Exception as e:
            print(e)

    def print_help(self):
        print(self._parser.format_help())


@singleton
class ArgumentParserWrapper:
    def __init__(self):
        self._parser = argparse.ArgumentParser()

    def get_parser(self):
        return self._parser
