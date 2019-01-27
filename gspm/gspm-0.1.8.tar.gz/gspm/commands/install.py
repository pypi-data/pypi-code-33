
import logging
import gspm.utils.path_utils as path_utils
import gspm.utils.asset_utils as asset_utils
import gspm.utils.godot_utils as godot_utils
import os

from argparse import ArgumentParser


def _install(project):
    logging.debug("[install] _install")
    assets = project.args.assets
    logging.debug("- there are [{0}] assets specified".format(len(assets)))
    if len(assets) == 0:
        if not project.args.assets_only:
            logging.debug("- installing project assets")
            _setup(project)
            _pre_install(project)
            _godot(project)
            _assets(project)
            _post_install(project)
    else:
        logging.debug("- installing assets only")
        _assets(project)


def _setup(project):

    logging.debug("[install] _setup")

    #   create the repo
    logging.debug("- checking for existing repository at [{0}]".format(project.repository_path))
    if not os.path.exists(project.repository_path):
        path_utils.create_path(project.repository_path)
        logging.debug("- new repository created at [{0}]".format(project.repository_path))
    else:
        logging.debug("- repository already exists, skipping")


def _main(project):
    logging.debug("[install] _main")
    logging.log(99, 'Installing Project [{0}]'.format(project.config.name))
    asset_utils.pull_asset(project, project.config.main)


def _assets(project):
    logging.debug("[install] _assets")
    if project.config.assets:
        for asset_name in project.config.assets:
            asset = project.config.assets[asset_name]
            asset.name = asset_name
            if asset.active:
                asset_utils.clean_asset(project, asset)
                asset_utils.pull_asset(project, asset)
                asset_utils.copy_asset(project, asset)


def _pre_install(project):
    logging.debug("[install] _pre_install")
    pass


def _post_install(project):
    logging.debug("[install] _post_install")
    pass


#   install godot
def _godot(project):
    logging.debug("[install] _godot")
    godot_utils.install_godot(project)
    pass


class Install:

    @staticmethod
    def run(project):
        logging.debug("[install] run")
        try:
            _install(project)
        except Exception as e:
            raise Exception(e)

    def add_parser(self, subparser: ArgumentParser):
        logging.debug("[install] add_parser")
        logging.info("adding [install] command")

        cmd = subparser.add_parser("install", help="install the project files")
        cmd.set_defaults(func=self.run)

        cmd.add_argument("assets", action="store", nargs="*", help="asset(s)")

        cmd.add_argument(
            "-a",
            "--assets",
            dest="assets_only",
            action="store_true",
            help="install assets(s) only",
            default=False
        )

