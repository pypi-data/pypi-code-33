import argparse
from typing import Optional


class Config(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser()

    def get(self, key: str) -> Optional[str]:
        return getattr(self.parser.parse_args(), key)

    def set_argument(self, *name_or_flags, **kwargs) -> None:
        self.parser.add_argument(*name_or_flags, **kwargs)
