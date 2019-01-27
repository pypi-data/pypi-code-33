
import logging
import gspm.utils.path_utils as path_utils
import gspm.utils.asset_utils as asset_utils
import gspm.utils.godot_utils as godot_utils
import os


from argparse import ArgumentParser


def _run(project):
    logging.debug("[update] _run")
    if project.config.assets:
        for asset_name in project.config.assets:
            asset = project.config.assets[asset_name]
            asset.name = asset_name
            if asset.active:
                asset_utils.clean_asset(project, asset)
                asset_utils.pull_asset(project, asset)
                asset_utils.copy_asset(project, asset)


#   install godot
def _godot(project):
    logging.debug("[update] _godot")
    godot_utils.install_godot(project)
    pass


class Update:

    @staticmethod
    def run(project):
        logging.debug("[update] run")
        try:
            _run(project)
        except Exception as e:
            raise Exception(e)

    def add_parser(self, subparser: ArgumentParser):
        logging.debug("[update] add_parser")
        logging.info("adding [update] command")

        cmd = subparser.add_parser("update", help="update the project")
        cmd.set_defaults(func=self.run)

