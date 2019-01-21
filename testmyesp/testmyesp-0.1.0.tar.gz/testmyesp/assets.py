
import logging


logger = logging.getLogger(__name__)


class Asset:
    def __init__(self, job, name, content):
        self.job = job
        self.name = name
        self.content = content

        self.logger = self.job.logger

    def __str__(self):
        return 'asset {}'.format(self.name)
