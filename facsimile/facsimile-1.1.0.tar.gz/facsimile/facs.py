#!/bin/env python

import os
import sys

import facsimile
import facsimile.base
from facsimile import cli
from facsimile import codec


def find_initial():
    check_dirs = [
        '.',
        os.path.join('facsimile'),
        os.path.join('config', 'facsimile'),
        # ~/.facsimile/facsimile.yml
        ]

    for each in check_dirs:
        if os.path.exists(each):
            data = codec.load_datafile('facsimile', each, default=None)
            if data:
                return data

    return {}


def get_cls(project_name, project_data):
    """
    gets class from name and data, sets base level attrs
    defaults to facsimile.base.Facsimile
    """
    if project_name:
        cls = getattr(facsimile.base, project_data.get('class', 'Facsimile'))
        cls.name = project_name
    else:
        cls = facsimile.base.Facsimile
    return cls

def main(argv=sys.argv[1:], run=True):
    usage = "usage: %prog [options] <project name> <release environment> [<version>]"

    # assume first arg without - is package name
    (project_name, argv) = cli.pop_first_arg(argv)
    data = find_initial()
    project_data = data.get('facsimile', {}).get('components', {}).get(project_name, {})

    cls = get_cls(project_name, project_data)

    (status, options) = cli.parse_options(cls, argv, usage)
    if status:
        return status

    # merge options dict over data dict
    inst = cli.instantiate(cls, options)

    attrs = ('repo', 'src_dir')
    for attr in attrs:
        value = project_data.get(attr, None)
        if value:
            setattr(inst, attr, value)

    info = cli.check_info(options, inst)

    if run and not info:
        inst.run()

    return 0

