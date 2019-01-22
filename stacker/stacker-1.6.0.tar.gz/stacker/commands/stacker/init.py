"""Initialize scaffolding for a new stacker project."""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from .base import BaseCommand
from ...actions import init

DEFAULT_REPO = "https://github.com/cloudtools/stacker_cookiecutter.git"


class Init(BaseCommand):

    name = "init"
    description = __doc__

    def add_arguments(self, parser):
        super(Init, self).add_arguments(parser)
        parser.add_argument(
            "--url", type=str, default=DEFAULT_REPO,
            help="Used to define an alternative url than the default: "
                 "%(default)s"
        )
        parser.add_argument(
            "--target", type=str,
            default=None,
            help="Used to define the branch, tag or commit ID to use. "
                 "Default: master"
        )
        parser.add_argument(
            "project_name", type=str,
            help="Defines the name of the directory/project to initialize."
        )

    def run(self, options, **kwargs):
        super(Init, self).run(options, **kwargs)
        action = init.Action(options.context,
                             provider_builder=options.provider_builder)

        action.execute(
            url=options.url,
            target=options.target,
            project_name=options.project_name
        )
