from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import logging

from .base import BaseAction

from cookiecutter.main import cookiecutter

logger = logging.getLogger(__name__)


class Action(BaseAction):
    """Initialize a new stacker project.
    """

    def run(self, url, target, project_name):
        cookiecutter(url, checkout=target, output_dir=project_name)
