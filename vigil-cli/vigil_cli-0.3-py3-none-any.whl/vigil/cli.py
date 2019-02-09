""" Command-line interface for Vigil, depends on plac."""
# Standard modules
import datetime
import gettext

import logging

# External dependencies
import plac
import ruamel.yaml

# Local modules
from vigil import collection
from vigil import watch
from vigil import config

gettext.install('vigil', 'locale')
log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class CLI:
    """
    Command-line interface for Vigil.
    """

    commands = 'check', 'add', 'remove', 'show', 'config', 'quit'

    def __init__(self):
        """
        Initiate collection.
        """
        self.collection = collection.WatchCollection(config.Config())
        self.__doc__ = _('Command-line interface for Vigil.\n')
        self.__doc__ += _('Use help to see the available commands.')

    def __enter__(self):
        # Check if Vigil is configured
        output = self.collection.config['output']
        if output == 'email' and not self.collection.config.email_configured():
            log.warning('Cannot send notifications as email is not configured.'
                        ' For further information, see "vigil config -h" and '
                        'https://radek-sprta.gitlab.io/vigil/')

    @plac.annotations(force=('ignore time interval', 'flag', 'f'))
    def check(self, force):
        """
        Check all watches in the database.
        """
        try:
            self.collection.check(force)
        except ValueError as ex:
            log.error(ex)

        yield 'Check Complete.'

    @plac.annotations(name=_('name of the watched site'),
                      url=_('url of site to watch'),
                      tolerance=(_('percentage to consider site changed'),
                                 'option', 't', int),
                      interval=(_('update interval'), 'option', 'i', int))
    def add(self, name, url, tolerance=2, interval=24):
        """
        Add a site to watch.
        """
        try:
            interval = datetime.timedelta(hours=interval)
            self.collection.add(
                watch.Watch(name, url, interval=interval, tolerance=tolerance))
            yield _('Added {0} ({1}).'.format(name, url))
        except ValueError as ex:
            log.warning(ex)

    @plac.annotations(name=_('name of the watched site'))
    def remove(self, name):
        """
        Remove a watched site.
        """
        try:
            self.collection.remove(name)
            yield _('Removed {0}.'.format(name))
        except ValueError as ex:
            log.warning(ex)

    @plac.annotations(name=_('name of the watched site'),
                      all=(_('show all watched sites'), 'flag', 'a'))
    def show(self, all, name=None):  # pylint: disable=redefined-builtin
        """
        Show details about a watched site.
        'vigil show -a' lists all watched sites.
        """
        if all:
            yield self._get_all()
        elif name:
            try:
                yield self._get_watch(name)
            except KeyError as ex:
                log.warning('No watch identified by "%s".', ex)
        else:
            # Do not translate, emulates plac output
            yield ("usage: vigil show [-h] name\n"
                   "vigil show: error: "
                   "the following arguments are required: name")

    def _get_watch(self, name):
        """
        Show details about a watched site.
        """
        watch_ = self.collection.get(name)
        if watch_:
            url = _('Url: {0}').format(watch_.url)
            date = _('Updated: {0}').format(watch_.date)
            interval = _('Interval: {0}').format(watch_.interval)
            tolerance = _('Tolerance: {0}').format(watch_.tolerance)
            return _('{0}\n{1}\n{2}\n{3}\n{4}').format(name,
                                                       url,
                                                       date,
                                                       tolerance,
                                                       interval)
        return "No such site."

    def _get_all(self):
        """
        Show details about all watched sites.
        """
        result = []
        for watch_ in self.collection.get_all():
            result.append(watch_.__str__())
        return '\n'.join(result)

    @plac.annotations(key=_('config key to change'),
                      value=_('value of the key'),
                      show=(_('show configuration'), 'flag', 's'))
    def config(self, show, key=None, value=None):
        """
        Update configuration.
        'vigil config -s' shows current configuration instead.
        """
        if show:
            yield self._get_config()
        elif key and value:
            yield self._update_config(key, value)
        else:
            # Do not translate, emulates plac output
            yield ("usage: vigil config [-h] [-s] key value\n"
                   "vigil config: error:"
                   "the following arguments are required: key value")

    def _update_config(self, key, new_value):
        """
        Update configuration.
        """
        config_ = self.collection.config
        try:
            if key in config_:
                config_[key] = new_value
            else:
                for value in config_.values():
                    if key in value:
                        value[key] = new_value
            return _('Updated config: {0}={1}'.format(key, new_value))
        except KeyError:
            log.warning(_('No such config option.'))

    def _get_config(self):
        """
        List the configuration.
        """
        result = ['Configuration at {0}:'.format(
            self.collection.config._configpath)]  # pylint: disable=protected-access

        def append_config(dictionary):
            """
            Flatten configuration.
            """
            for key, value in dictionary.items():
                if isinstance(value, ruamel.yaml.comments.CommentedMap):
                    append_config(value)
                else:
                    result.append('{0}: {1}'.format(key, value))

        append_config(self.collection.config)
        return '\n'.join(result)

    def quit(self):  # pylint: disable=no-self-use
        """
        Quit interactive mode.
        """
        raise plac.Interpreter.Exit

    def __missing__(self, name):
        yield _('Command "{0}" does not exist.').format(name)

    def __exit__(self, etype, *args):
        """
        Will be called automatically at the end of the interpreter loop.
        """
        if etype in (None, GeneratorExit):
            print(_('Done.'))
