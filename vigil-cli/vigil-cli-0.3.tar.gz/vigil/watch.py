""" Represent a website to be watched."""
# Standard modules
import asyncio
import datetime
import gettext
import logging

# External dependencies
import aiohttp

# Local modules
from vigil.utils.diff import Diff

gettext.install('vigil', 'locale')
log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class Watch:  # pylint: disable=too-many-instance-attributes
    """
    Contains the site to be watched and how often it should be watched.

    Attributes:
        url (str): Url of the site to watch.
        interval (:obj:`timedelta`): How often the site should be watched.
        tolerance (int): Percentage needed to consider the site changed.
        date (:obj:`datetime`): Date of last update.
        content (str): Content of the site.
        diff (str): The changed part of the website.
    """

    def __init__(self, name, url, *, interval=datetime.timedelta(days=1),  # pylint: disable=too-many-arguments
                 tolerance=2, date=None, content=None, diff=None):
        self.name = name
        self.url = url
        self.interval = interval
        self.tolerance = tolerance
        self.date = date
        self.content = content
        self.diff = diff

        if not self.content:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._update())

    @property
    def interval(self):
        """
        int: How often the site should be watched. Must be higher than 0.
        """
        return self.__interval

    @interval.setter
    def interval(self, value):
        if value <= datetime.timedelta(0):
            raise ValueError(_('Interval should be higher than zero.'))
        else:
            self.__interval = value  # pylint: disable=attribute-defined-outside-init

    @property
    def tolerance(self):
        """
        int: Percentage needed to consider the site changed.  Must be
            between 0 and 100.
        """
        return self.__tolerance

    @tolerance.setter
    def tolerance(self, value):
        if not 0 < value <= 100:
            raise ValueError(_('Tolerance must be between 1 and 100 percent.'))
        else:
            self.__tolerance = value  # pylint: disable=attribute-defined-outside-init

    async def _update(self):
        """
        Download the page and save its contents.
        """
        try:
            log.debug('Access page url=%s', self.url)
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as response:
                    self.content = await response.text()
            self.date = datetime.datetime.utcnow()
        except OSError:
            log.warning(_("Cannot reach server url=%s"), self.url)

    async def check(self, force=False):
        """
        Checks if site was updated and returns the difference.

        Args:
            force(bool, optional): Force check even if not enough time passed.
        """
        updated = False

        # Save the old content
        old = self.content

        # Check if enough time passed to check the site for updates
        need_update = datetime.datetime.utcnow() > (self.date + self.interval)
        log.debug('need_update=%s, force=%s', need_update, force)

        if force or need_update:
            log.info('Checking site %s', self.name)
            await self._update()

            # If the difference is big enough, save it in unified diff format
            if self._diff_percent(old, self.content) > self.tolerance:
                diff_ = Diff.compare(old, self.content)
                self.diff = ('{0}:\n{1}'.format(self.name, diff_))
                updated = True

        return updated

    @staticmethod
    def _diff_percent(old, new):
        """
        Check the difference in size of two strings.

        Args:
            old(str): First string to compare.
            new(str): Second string to compare.

        Returns:
            float: Difference in length in percents.
        """
        diff_percent = 100 * abs(len(new) - len(old)) / len(old)
        log.debug('diff_percent=%s', diff_percent)
        return diff_percent

    def as_dict(self):
        """
        Return dictionary representation of Watch.
        """
        as_dict = {'name': self.name,
                   'url': self.url,
                   'interval': self.interval,
                   'tolerance': self.tolerance,
                   'date': self.date,
                   'content': self.content,
                   'diff': self.diff
                   }
        return as_dict

    def __repr__(self):
        as_dict = {'name': self.name,
                   'url': self.url,
                   'interval': self.interval,
                   'tolerance': self.tolerance,
                   'date': self.date,
                   'diff': self.diff
                   }
        return '{0}: {1}'.format(self.__class__, str(as_dict))

    def __str__(self):
        return '{0}: {1}'.format(self.name, self.url)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
