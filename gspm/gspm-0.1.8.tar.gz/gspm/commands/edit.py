
import logging
import argparse

from argparse import ArgumentParser
import gspm.utils.godot_utils as godot_utils


def _edit(project):
    godot_utils.edit_godot(project)


class Edit:

    @staticmethod
    def run(project):
        logging.debug("[Edit] run")
        _edit(project)
        pass

    def add_parser(self, subparser: ArgumentParser):
        logging.debug("[Edit] add_parser")
        logging.info("adding [edit] command")

        cmd = subparser.add_parser("edit", help="open project wih the Godot editor")
        cmd.set_defaults(func=self.run)

