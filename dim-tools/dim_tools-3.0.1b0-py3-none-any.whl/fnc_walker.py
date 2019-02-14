# -*- coding: utf-8 -*-
from os import listdir


def main(my_path='.', extension=None):
    if extension:
        return [f for f in listdir(my_path) if f.split('.')[-1] in extension]
    else:
        return [f for f in listdir(my_path)]
