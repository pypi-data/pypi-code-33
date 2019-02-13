#!/usr/bin/python
# -*- coding: UTF-8 -*-
import getopt
import sys


class OptDict(dict):
    __opt_dict = {}
    __description_dict = {}
    __input_options = []

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def __getitem__(self, key):
        if isinstance(key, tuple):
            tuple_key = key
        else:
            tuple_key = (key, )
        for exists_tuple_key in self.keys():
            is_exists = True
            for to_get_key in tuple_key:
                if to_get_key in exists_tuple_key:
                    continue
                else:
                    is_exists = False
                    break
            if is_exists:
                return super().get(exists_tuple_key)
        raise KeyError(key)

    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            to_insert_tuple_key = key
        else:
            to_insert_tuple_key = (key, )

        # value -> (expected value, usage_description)
        usage_description = ""
        if isinstance(value, tuple):
            usage_description = value[1]
            value = value[0]
        # add all description even it's empty
        self.__description_dict[to_insert_tuple_key] = usage_description
        # if key in it, update
        for exists_tuple_key in self.keys():
            is_exists = True
            for to_insert_key in to_insert_tuple_key:
                if to_insert_key in exists_tuple_key:
                    continue
                else:
                    is_exists = False
                    break
            if is_exists:
                super().__setitem__(exists_tuple_key, value)
                return

        super().__setitem__(to_insert_tuple_key, value)

    def get(self, key, default_value=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default_value

    def print_usage_description(self):
        for k, v in self.__description_dict.items():
            print(v)

    def set_input_option(self, key: tuple):
        print(key)
        if key in self.keys():
            self.__input_options.append(key)
            return
        raise "{} is not in {}".format(key, self.keys())
        # is_exists = True
        # for to_get_key in tuple_key:
        #     if to_get_key in exists_tuple_key:
        #         continue
        #     else:
        #         is_exists = False
        #         break
        # if is_exists:
        #     return super().get(exists_tuple_key)

    def get_input_option(self):
        return self.__input_options


def get_opts(self):
    shortopts = ""
    longopts = []
    for k, v in self.items():
        print(k)
        if isinstance(v, bool):
            for arg_name in k:
                if len(arg_name) == 1:
                    shortopts += arg_name
                else:
                    longopts.append(arg_name)
        else:
            for arg_name in k:
                if len(arg_name) == 1:
                    shortopts += arg_name + ":"
                else:
                    longopts.append(arg_name + "=")
    return shortopts, longopts


def get_option(argv, opt_dict: OptDict):
    # Notice:
    #       if value is bool, it's mean to the argument name did't need value
    #       otherwise, mean to need value that use give
    # opt_dict = {}
    # opt_dict[('h', 'help')] = False
    # opt_dict[('i', 'ifile')] = None
    # opt_dict[('o', 'ofile')] = None
    shortopts = ""
    longopts = []

    for k, v in opt_dict.items():
        if isinstance(v, bool):
            for arg_name in k:
                if len(arg_name) == 1:
                    shortopts += arg_name
                else:
                    longopts.append(arg_name)
        else:
            for arg_name in k:
                if len(arg_name) == 1:
                    shortopts += arg_name + ":"
                else:
                    longopts.append(arg_name + "=")
    try:
        opts, args = getopt.getopt(argv, shortopts, longopts)
    except getopt.GetoptError as e:
        print("get option error" + e.msg)
        sys.exit(2)
    for opt_name, opt_value in opts:
        if opt_name.startswith('--'):
            opt_name = opt_name[2:]
        if opt_name.startswith('-'):
            opt_name = opt_name[1:]
        for arg_name in opt_dict.keys():
            if opt_name in arg_name:
                if isinstance(opt_dict[arg_name], bool):
                    opt_value = True if opt_value == '' else opt_value
                opt_dict[arg_name] = opt_value
                opt_dict.set_input_option(arg_name)
                break
    return args
