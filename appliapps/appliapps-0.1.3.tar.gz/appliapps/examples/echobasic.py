#!/usr/bin/env python
"""example/echobasic - an appliapp example."""

from applicake.base import BasicApp
from applicake.base.coreutils import Argument
from applicake.base.coreutils import Keys, KeyHelp


class EchoBasic(BasicApp):
    """ example for a BasicApp,§ prints COMMENT to stdout """

    def add_args(self):
        return [
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument("COMMENT", "String to be displayed")
        ]

    def run(self, info):
        print(info["COMMENT"])
        return info


if __name__ == "__main__":
    EchoBasic.main()
