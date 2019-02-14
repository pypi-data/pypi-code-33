# -*- coding: utf-8 -*-
from os import makedirs
from os.path import exists as dir_exists


def main(path):
    if not dir_exists(path):
        makedirs(path)
