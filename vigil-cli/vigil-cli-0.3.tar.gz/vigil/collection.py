""" Encompass core functionality of Vigil. Collection handling adding,
    removing and updating sites, running on top of TinyDB."""
# Standard modules
import asyncio
import collections
import gettext
import logging

# External dependencies
import tinydb
import jinja2

# Local modules
from vigil import watch
from vigil import output
from vigil.utils import serialization

gettext.install('vigil', 'locale')
log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class WatchCollection:
    """
    Collection to manipulate the watches.

    Attributes:
        config(:obj:`dic`): Configuration for the collection
        watches(:obj:`dic`): Dictionary holding the watches and by their name.
    """
    __slots__ = ['config', 'db']

    def __init__(self, config):
        self.config = config
        self.db = tinydb.TinyDB(self.config['savepath'],  # pylint: disable=invalid-name
                                create_dirs=True,
                                cls=serialization.DatetimeEncoder,
                                indent=2,
                                sort_keys=True)

    @property
    def templates(self):
        """
        Jinja template environment.
        """
        env = jinja2.Environment(
            loader=jinja2.PackageLoader('vigil', 'templates'),
            autoescape=jinja2.select_autoescape(['html', 'xml']))
        return env

    def check(self, force=False):
        """
        Check if any of the watches were updated and send notification.

        Args:
            force(bool, optional): Check the watches regardless of time passed.
        """
        # Get a list of sites to check
        watches = self.get_all()

        # Use scheduler to check the sites
        tasks = asyncio.wait([w.check(force) for w in watches])
        loop = asyncio.get_event_loop()

        try:
            loop.run_until_complete(tasks)
        except ValueError:
            raise ValueError(_("No sites to watch."))
        else:
            # Updates sites in database
            for watch_ in watches:
                if watch_.diff:
                    self.update(watch_.name, 'content', watch_.content)
                    self.update(watch_.name, 'diff', watch_.diff)
                    log.info(_('Watch updated %s'), watch_.name)
                else:
                    log.debug('Watch not updated name=%s', watch_.name)

                # Update last access time whether the site was updated or not
                self.update(watch_.name, 'date', watch_.date)

            if self.get_updated():
                self.send_notification()

    def add(self, watch_):
        """
        Add watch to collection.

        Args:
            name(str): Name of the watch.
            watch(:obj:`watch`): Watch to be added to collection.
        """
        query = tinydb.Query()

        # Check if the name is already used in the database
        if self.db.contains(query.name == watch_.name):
            raise ValueError(
                _('%s in use. Choose a different name.') % watch_.name)

        # If the database does not contain watch_ with the same url, add it
        if self.db.contains(query.url == watch_.url):
            raise ValueError(
                _('%s is already in the collection.') % watch_.url)

        eid = self.db.insert(watch_.as_dict())
        log.debug('Added watch id=%s name=%s url=%s', eid, watch_.name, watch_.url)

    def remove(self, identifier):
        """
        Remove watch with the given name or url from collection.

        Args:
            identifier(str): Name or url of the watch to be removed.
        """
        watch_ = tinydb.Query()

        # Get the watch with name or url matching the identifier
        to_delete = self.db.get((watch_.name == identifier)
                                | (watch_.url == identifier))

        # If match is found, remove it from the database
        if to_delete:
            eid = self.db.remove(watch_.name == to_delete['name'])
            log.debug('Removed watch id=%s name=%s url=%s',
                      eid, to_delete['name'], to_delete['url'])
        else:
            raise ValueError(_('No watch identified by %s'), identifier)

    def update(self, name, key, value):
        """
        Update key of watch of given name to new value.
        """
        watch_ = tinydb.Query()
        eid = self.db.update({key: value}, watch_.name == name)
        log.debug('Updated value id=%s name=%s key=%s', eid, name, key)

    def get(self, identifier):
        """
        Return watch matching the name or url.

        Args:
            identifier(str): Name or url to match against.
        """
        watch_ = tinydb.Query()
        attributes = self.db.get((watch_.name == identifier)
                                 | (watch_.url == identifier))

        # Convert dict into Watch item
        try:
            return watch.Watch(**serialization.deserialize(attributes))
        except TypeError:
            log.debug('No watch found identifier=%s', identifier)
            return None

    def get_all(self):
        """
        Returns all watches in database.
        """
        watches = self.db.all()
        result = []
        for watch_ in watches:
            result.append(watch.Watch(**serialization.deserialize(watch_)))
        return result

    def get_updated(self):
        """
        Returns all watches in database.
        """
        watch_query = tinydb.Query()
        watches = self.db.search(watch_query.diff != None)  # pylint: disable=singleton-comparison
        result = []

        for watch_ in watches:
            result.append(watch.Watch(**serialization.deserialize(watch_)))
        return result

    def seen_all(self):
        """
        Mark all watches as seen.
        """
        for watch_ in self.get_updated():
            self.update(watch_.name, 'diff', None)
            log.debug('Marked as seen url=%s', watch_.url)

    def send_notification(self):
        """
        Send notification through given channel.
        """
        outputs = self._get_outputs()
        updates = self.get_updated()
        success = False
        Update = collections.namedtuple(  # pylint: disable=invalid-name
            'Update', ['url', 'diff'])

        for output_ in outputs:
            content = ''
            template_name = '{}.j2'.format(output_.__name__)
            template = self.templates.get_template(template_name)

            # Check if we should send full diffs or only urls
            log.debug('send_diff=%s', self.config['send_diff'])
            log.debug('Output does not allow sending diffs output=%s',
                      output_.only_url)
            if self.config['send_diff'] and not output_.only_url:
                content = [Update(w.url, w.diff) for w in updates]
            else:
                content = [Update(w.url, "") for w in updates]

            if content:
                log.info(_('Sending email'))
                # Send notification either aggregate or separately
                if self.config['send_aggregate']:
                    body = template.render(content=content)
                    success = output_(_('Vigil: Site Updated'),
                                      body, self.config).send()
                else:
                    for item in content:
                        item = [item]
                        body = template.render(content=item)
                        success = output_(_('Vigil: Site Updated'),
                                          body, self.config).send()

        # Mark sites watched
        if success:
            self.seen_all()

    def _get_outputs(self):
        """
        Get output channels for notifications.

        Return:
            list: All output channels defined for in configuration.
        """
        outputs = []
        config = self.config['output']

        if isinstance(config, str):
            # Only one defined output
            outputs.append(output.outputs()[config])
        else:
            # Multiple outputs
            outputs = [output.outputs()[o] for o in self.config['output']]
        return outputs
