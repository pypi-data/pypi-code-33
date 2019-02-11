import os

from jinja2 import Environment, FileSystemLoader
from missinglink.crypto import Asymmetric

cur_path = os.path.dirname(os.path.abspath(__file__))
env = Environment(loader=FileSystemLoader(cur_path))


def render(name, **kwargs):
    template = env.get_template(name)
    result = template.render(**kwargs)
    return result


def build_user_command(**kwargs):
    return Asymmetric.bytes_to_b64str(render('machine_bootstrap.sh.jinja2', **kwargs))


def build_root_command(**kwargs):
    return Asymmetric.bytes_to_b64str(render('root_bootstrap.sh.jinja2', **kwargs))
