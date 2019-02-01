import argparse

from kpc_nifi_utils.common.singleton import singleton


class Args:
    def __init__(self):
        self._wrapper = ArgumentParserWrapper()

    def add(self, *args, **kwargs):
        if self._wrapper.is_parse():
            raise ValueError("Can not add args config when parser is already initiate")

        self._wrapper.get_parser().add_argument(*args, **kwargs)
        return self

    def get(self, key):
        if not self._wrapper.is_parse():
            raise ValueError("Can not get args value because parser not initiate, calling parse() and then try again")

        try:
            return self._wrapper.get_args()[key]
        except Exception as e:
            print(e)

    def print_help(self):
        print(self._wrapper.get_parser().format_help())


@singleton
class ArgumentParserWrapper:
    def __init__(self):
        self._args = None
        self._parser = argparse.ArgumentParser()
        self._is_parse = False

    def get_parser(self):
        return self._parser

    def get_args(self):
        return self._args

    def parse(self):
        self._args = self._parser.parse_args()
        self._is_parse = True
        return self

    def is_parse(self):
        return self._is_parse
