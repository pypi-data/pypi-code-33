import os
import json
import requests
import subprocess

from six import StringIO
from six.moves import configparser
import yaml
import toml

from tpyl import utils


def parse_context(file_path):
    if utils.is_url(file_path):
        return parse_url(file_path)
    elif file_path.endswith('.env'):
        return parse_env(file_path)
    elif file_path.endswith('.ini'):
        return parse_ini(file_path)
    elif file_path.endswith('.json'):
        return parse_json(file_path)
    elif file_path.endswith('.toml'):
        return parse_toml(file_path)
    elif file_path.endswith('.yaml') or file_path.endswith('.yml'):
        return parse_yaml(file_path)
    return parse_auto(file_path)


def parse_auto(file_path):
    ctx = {}
    for parser, exceptions in [
        [parse_json, (ValueError, )],
        [parse_yaml, (yaml.YAMLError, )],
        [parse_toml, (toml.TomlDecodeError, )],
        [parse_ini, (configparser.MissingSectionHeaderError, )],
        [parse_exec, (ValueError, )],
        [parse_env, (ValueError, )],
    ]:
        is_valid, ctx = check_context(file_path, parser, exceptions)
        if is_valid:
            break
    return ctx


def check_context(file_path, parser, exceptions=None):
    exceptions = exceptions or (ValueError,)
    try:
        ctx = parser(file_path)
        if is_valid_context(ctx):
            return True, ctx
    except exceptions:
        pass
    return False, None


def is_valid_context(ctx):
    return ctx and isinstance(ctx, dict)


def parse_file(fp, parser):
    if utils.is_string(fp):
        with open(fp, 'r') as f:
            return parser(f)
    fp.seek(0)
    return parser(fp)


def parse_exec(file_path):
    if not utils.is_string(file_path):
        return
    if not utils.is_executable(file_path):
        return
    cmd = os.path.join(os.getcwd(), file_path)
    output = subprocess.check_output(cmd)
    io = StringIO(output.decode('utf-8'))
    ctx = parse_auto(io)
    return ctx


def parse_env(file_path):
    def parser(fp):
        ctx = {}
        for line in fp:
            if not line.strip():
                continue
            key, value = split_var(line)
            ctx[key] = (value or '').strip() or None
        return ctx
    return parse_file(file_path, parser)


def parse_ini(file_path):
    def parser(fp):
        config = configparser.ConfigParser()
        config.readfp(fp)
        defaults = config.defaults()
        # Return None if the parsed file is emtpy
        if dict(defaults) == {} and config.sections() == []:
            return {}
        default_section = getattr(config, 'default_section', 'DEFAULT')
        ctx = {
            default_section: config.defaults(),
        }
        sections = config._sections
        for s in sections:
            ctx[s] = sections[s]
        return ctx
    return parse_file(file_path, parser)


def parse_json(file_path):
    return parse_file(file_path, json.load)


def parse_yaml(file_path):
    return parse_file(file_path, yaml.load)


def parse_toml(file_path):
    return parse_file(file_path, toml.load)


def parse_url(url):
    response = requests.get(url)
    response.raise_for_status()
    io = StringIO(response.text)
    ctx = parse_auto(io)
    return ctx


def split_var(variable):
    key, value = None, None
    try:
        key, value = variable.split('=', 1)
    except ValueError:
        key = variable
    if isinstance(value, str):
        value = value.strip()
    key = (key or '').strip('\n')
    return key, value
