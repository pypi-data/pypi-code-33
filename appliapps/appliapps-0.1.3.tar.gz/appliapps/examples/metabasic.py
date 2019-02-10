#!/usr/bin/env python
"""meta appliapp."""
import os
import logging

from applicake.base.app import BasicApp
from applicake.base.apputils import validation
from applicake.base.apputils import dynrun
from applicake.base.coreutils.arguments import Argument
from applicake.base.coreutils.keys import Keys, KeyHelp


class ExamplesMetaBasic(BasicApp):
    """ examples meta basic."""

    def add_args(self):
        return [
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
        ]

    def run(self, info):
        workdir = os.getcwd()
        dynrun.run('examples.echobasic', info['INPUT'], 'vars.ini', workdir, [])
        dynrun.run('examples.echobasic', 'vars.ini', 'vars.ini', workdir, [])
        dynrun.run('examples.echobasic', 'vars.ini', 'vars.ini', workdir, [])
        dynrun.run('examples.echobasic', 'vars.ini', 'vars.ini', workdir, [])
        return info

    @classmethod
    def validate_run(cls, info, exit_code, out):
        """validate the run."""
        if out:
            logging.debug("out set, not used: %s", out)
        validation.check_exitcode(exit_code)
        return info


if __name__ == "__main__":
    ExamplesMetaBasic.main()
