import os
from os.path import join
from datetime import datetime

from mako.template import Template


here = os.path.abspath(os.path.dirname(__file__))

files = {
    join(here, 'python2-stable.Dockerfile'): dict(
        pip='pip2', image='python:2.7'),
    join(here, 'python3-stable.Dockerfile'): dict(
        pip='pip3', image='python:3.6'),
}


def modification_date(filename):
    mtime = os.path.getmtime(filename)
    return datetime.fromtimestamp(mtime)


def make_file(template, filepath, **kwargs):
    if not os.path.exists(filepath):
        hastomake = True
    else:
        if modification_date(filepath) < modification_date(template):
            hastomake = True
        else:
            hastomake = False

    if hastomake:
        print(template, '->', filepath)
        with open(filepath, 'w') as f:
            template_mako = Template(filename=template)
            f.write(template_mako.render(**kwargs))


def clean():
    for filepath in files:
        if os.path.exists(filepath):
            os.remove(filepath)


if __name__ == '__main__':
    template = join(here, 'template_mako.Dockerfile')
    for filepath, kwargs in files.items():
        make_file(template, filepath, **kwargs)
