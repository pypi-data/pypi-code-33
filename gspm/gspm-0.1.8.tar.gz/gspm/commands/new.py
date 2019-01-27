
import logging
import argparse
import os
import base64
from argparse import ArgumentParser
import gspm.utils.path_utils as path_utils


def _run(project):
    logging.debug("[new] _run")
    #   create project folder
    path_utils.create_path(project.args.name)
    project.project_path = os.path.abspath(project.args.name)
    #   create project.yml
    _create_project(project)
    #   create project.godot
    _create_godot_project(project)
    #   add assets
    _copy_assets(project)


def _create_project(project):
    logging.debug("[new] _create_project")
    yml = '''# gspm project.yml <http://https://gitlab.com/godot-stuff/gs-project-manager/wikis/schema>
name: $project.name$
path: .
version: 0.0.0
default_type: git
godot:
  version: 3.0.6
project:
  url: none
  
assets:
      
pre_install:

post_install:

pre_build:

post_build:
'''
    yml_file = "{0}/project.yml".format(project.project_path)
    yml = yml.replace('$project.name$', project.args.name)
    f = open(yml_file, "w+")
    f.write(yml)
    f.close()


def _create_godot_project(project):
    cfg = '''; godot engine configuration file
config_version=3

[application]

config/name="$project.name$"
config/description="$project.description$"
config/version="0.0.0"
'''
    cfg = cfg.replace('$project.name$', project.args.name)
    desc = project.args.name.replace('-', ' ')
    desc = desc.title()
    cfg = cfg.replace('$project.description$', desc)
    cfg_file = "{0}/project.godot".format(project.project_path)

    f = open(cfg_file, "w+")
    f.write(cfg)
    f.close()

def _copy_assets(project):
    img_str = b'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'
    img_file = "{0}/icon.png".format(project.project_path)
    f = open(img_file, "wb")
    filedata = base64.urlsafe_b64decode(img_str)
    f.write(filedata)
    f.close()


class New:

    @staticmethod
    def run(project):
        logging.debug("[new] run")
        _run(project)

    def add_parser(self, subparser: ArgumentParser):
        logging.debug("[new] add_parser")
        logging.info("adding [new] command")

        cmd = subparser.add_parser("new", help="create a new Godot project")
        cmd.set_defaults(func=self.run)

        cmd.add_argument(
            "-t",
            "--template",
            dest="template",
            help="use a template",
            default="default"
        )

        cmd.add_argument(
            "name",
            help="the name of the new project",
        )

        cmd.add_argument(
            "--ignore-project",
            default=True,
            help=argparse.SUPPRESS
        )
