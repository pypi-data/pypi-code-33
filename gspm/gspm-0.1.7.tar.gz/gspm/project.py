
import io
import logging
import os
import yaml
import dotmap
from configparser import ConfigParser


def load(filename: str):

    logging.debug("[project] load")

    try:
        logging.debug("- looking for config file [{0}]".format(filename))
        if not os.path.exists(filename):
            logging.debug("- unable to locate the project configuration file [{0}]".format(filename))
            raise Exception("gspm Project Configuration File [{0}] was Not Found.".format(filename))

        logging.debug("- found it")

        #   get config file text
        file = io.open(filename)
        text = file.read()

        #   get gspm  settings
        config = _get_config()

        #   replace tokens
        if config:
            tokens = config.items("tokens")
            for token in tokens:
                text = text.replace(token[0], token[1])

        #   create contents
        contents = yaml.load(text)

        #   create project from contents
        project = dotmap.DotMap(contents)

        #   validate the project
        _validate(project)

        #   return the project
        return project

    except Exception as e:
        raise e


def _get_config():

    hf = os.path.abspath(os.path.expanduser("~") + "/.gspm")

    logging.debug('- looking for [.gspm] file in Home folder [{0}]'.format(hf))

    if os.path.exists(hf):
        logging.debug('- found it')
        config = ConfigParser()
        config.read(hf)
        return config

    return

def _validate(project):

    if 'name' not in project:
        raise Exception("Project Configuration is Missing [name] Attribute.")

    #   default_type is git
    if 'default_type' not in project:
        project.default_type = 'git'

    if 'path' not in project:
        project.path = '.'

    if 'godot' not in project:
        raise Exception("Project Configuration is Missing [godot] Attribute")

    # backwards compatibility for old location yoption
    if 'location' in project.godot:
        project.godot.local = project.godot.location

    if 'local' not in project.godot:

        project.godot.location = ""

        if 'arch' not in project.godot:
            project.godot.arch = 32

        if 'mono' not in project.godot:
            project.godot.mono = False

        if 'assets' not in project:
            raise Exception("Project Configuration is Missing [assets] Section")

    #   if there are no assets, ignore
    if not project.assets:
        return

    for asset_name in project.assets:

        asset = project.assets[asset_name]

        if 'location' not in asset:
            raise Exception("Asset [{0}] is Missing its [location] Attribute".format(asset.name))

        if 'type' not in asset:
            asset.type = project.default_type

        asset.name = asset_name

        if 'active' not in asset:
            asset.active = True

        _check_includes(asset)


def _check_includes(asset):

    if 'includes' not in asset:
        asset.includes = []
        inc = dotmap.DotMap()
        inc.dir = "{0}".format(asset.name)
        asset.includes.append(inc)

    for include in asset.includes:
        if 'todir' not in include:
            include.todir = "{0}".format(include.dir)
