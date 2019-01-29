# -*- coding: utf-8 -*-
import argparse


class ArgsUtil:
    def __init__(self, description='parser desc'):
        self.parser = argparse.ArgumentParser(description=description)

    def setArg(self, name, type, required=True, help="say some help", default=""):
        if type == bool:
            type = ArgsUtil.bool_handle
        self.parser.add_argument(name, type=type, required=required, help=help, default=default)
        return self

    def get(self):
        return self.parser.parse_args()

    @staticmethod
    def bool_handle(v):
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')
