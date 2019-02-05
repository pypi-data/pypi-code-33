import sys, os
import logging
import platform
import getpass
import traceback
import argparse

import six

from .actors.cluster import Cluster
from .actors.flow import Flow


class SessionCmds(object):

    def __init__(self):
        super(SessionCmds, self).__init__()

class KabaretSession(object):

    @staticmethod
    def parse_command_line_args(args):
        '''
        Returns host, port, cluster_name found in the given args.
        If -h is found or if parsing fails, a ValueError is raised with 
        usage description.
        '''
        parser = argparse.ArgumentParser(
            description='Kabaret Session Arguments'
        )

        parser.add_argument(
            '-S', '--session', default='kabaret', dest='session_name', help='Session Name'
        )

        parser.add_argument(
            '-H', '--host', default='localhost', help='Cluster Host address'
        )
        parser.add_argument(
            '-P', '--port', default='6379', help='Cluster Port number'
        )
        parser.add_argument(
            '-C', '--cluster', default='DEFAULT_CLUSTER', dest='cluster_name', help='Cluster Name'
        )
        parser.add_argument(
            '-D', '--db', default='1', dest='db', help='Database Index'
        )
        parser.add_argument(
            '-p', '--password', default=None, dest='password', help='Database Password'
        )
        parser.add_argument(
            '-d', '--debug', default=False, action='store_const', const=True, dest='debug', help='Debug Mode'
        )

        values, remaining_args = parser.parse_known_args(args)
        return (
            values.session_name,
            values.host, values.port, values.cluster_name,
            values.db, values.password, values.debug, remaining_args
        )

    def __init__(self, session_name=None, debug=False):
        super(KabaretSession, self).__init__()
        self._session_name = session_name or self.__class__.__name__

        self._ticked = []
        self._actors = {}
        self.cmds = SessionCmds()
        self.debug_mode = debug

        # View Management
        self._view_types = {}
        self._views = {}

        self.log_formatter = logging.Formatter("%(name)s -- %(asctime)s -- %(levelname)s: %(message)s")
        self.stream_formatter = logging.Formatter("%(name)s - %(levelname)s: %(message)s")
        self.logger = logging.getLogger('kabaret')
        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        self.default_log_handler = logging.StreamHandler(sys.stdout)
        self.default_log_handler.setFormatter(self.stream_formatter)
        self.logger.addHandler(self.default_log_handler)

        self._cluster_actor = Cluster(self)     # this one is mandatory.
        self._create_actors()

    def add_log_file(self, filename, level=logging.INFO, mode="a", format=None, encoding="utf-8"):
        """
        Add a log file which will store all logging message with the given level
        :param filename
        :param level
        :param mode: "a" for appending or "w" for cleaning file before writing
        :param encoding
        :param format of the recording message, if None the default formatter is used
        :return: the created handler
        """
        handler = logging.FileHandler(filename, mode, encoding)
        if format:
            formatter = logging.Formatter(format)
        else:
            formatter = self.log_formatter
        handler.setFormatter(formatter)
        handler.setLevel(level)
        self.logger.addHandler(handler)
        return handler

    def add_log_stream(self, level=logging.INFO, stream=None):
        handler = logging.StreamHandler(stream)
        if format:
            formatter = logging.Formatter(format)
        else:
            formatter = self.log_formatter
        handler.setFormatter(formatter)
        handler.setLevel(level)
        self.logger.addHandler(handler)
        return handler

    def is_gui(self):
        return False

    def add_ticked(self, callable):
        '''
        Register a callable with no args to be called periodically.
        '''
        try:
            self._ticked.remove(callable)
        except ValueError:
            pass
        self._ticked.append(callable)

    def tick(self):
        for ticked in self._ticked:
            try:
                ticked()
            except Exception as err:
                message = '\n'.join((
                    "------------------ TRACE BEGIN ----------------",
                    traceback.format_exc(),
                    "------------------ TRACE END ------------------"
                ))
                self.log_error(
                    'Error while ticking: %s',
                    message
                )

    def _create_actors(self):
        '''
        Instanciate the session actors.
        Subclasses can override this to install customs actors or
        replace default ones.
        '''
        Flow(self)

    def session_name(self):
        return self._session_name

    def session_uid(self):
        return '%s:%s-%r@%s' % (
            getpass.getuser(),
            self._session_name,
            os.getpid(),
            platform.node(),
        )

    def _register_actor(self, actor):
        actor_name = actor.actor_name
        self.log(
            self._session_name,
            'Registering',
            repr(actor_name), 'Actor from', actor.__module__
        )
        self._actors[actor_name] = actor
        setattr(self.cmds, actor_name, actor.cmds)

    def get_actor_names(self):
        return sorted(self._actors.keys())

    def get_actor(self, actor_name):
        return self._actors[actor_name]

    #
    #       VIEW MANAGEMENT
    #
    def register_view_types(self):
        '''
        Subclasses can register view types and create defaults view here.
        Use:
            type_name = self.register_view_type(MyViewType)
        to register a view type.
        
        And optionally:
            view = self.add_view(type_name)
        to create a default view.
        '''
        pass

    def register_view_type(self, ViewType):
        view_type_name = ViewType.view_type_name()
        self._view_types[view_type_name] = ViewType
        return view_type_name

    def declare_view(self, view):
        '''
        This must be called by view instances uppon creation
        '''
        self._views[view.view_id()] = view

    def forget_view(self, view):
        '''
        This must be called by view instances uppon desctruction
        '''
        self._views.pop(view.view_id())

    def add_view(self, view_type_name, view_id=None, *view_args, **view_kwargs):
        try:
            ViewType = self._view_types[view_type_name]
        except KeyError:
            raise ValueError('Unknown view type %r (known view types are: %r)' %
                             (view_type_name, self._view_types.keys()))

        view = ViewType(self, view_id, *view_args, **view_kwargs)
        return view

    def view_type_count(self, view_type_name):
        return len([
            v for v in self._views.values()
            if v.view_type_name() == view_type_name
        ])

    def find_view(self, view_type_name=None, view_id=None, create=False, *args, **kwargs):
        '''
        Returns the first view with the specified view_type_name and/or the specified view_id.
        The view_id may be None to match any view_id.

        If create is True and no existsing view in found, create one in the given area
        using view_id, *args and **kwargs.

        If create is False, None is returned.
        '''
        if view_type_name is not None:
            try:
                self._view_types[view_type_name]
            except KeyError:
                raise ValueError(
                    'Find View: Unknown view type %r' % (
                        view_type_name,
                    )
                )

        for this_view_id, view in self._views.items():
            if view_type_name is not None and view.view_type_name() != view_type_name:
                continue
            if view_id is None or this_view_id == view_id:
                return view

        if create:
            return self.add_view(view_type_name, view_id, *args, **kwargs)

        return None

    def _get_layout_state(self):
        '''
        Subclasses with GUI must override this to return a state valid
        for self._set_layout_state(state)
        '''
        return None

    def _set_layout_state(self, state):
        '''
        Subclasses with GUI must implement this to restore the GUI
        state.

        The state argument is the return value of a call to 
        self._get_layout_state()
        '''
        raise NotImplementedError()

    def get_views_state(self):
        views = []
        for view_id, view in six.iteritems(self._views):
            view_state = view.get_view_state()
            if view_state is not None:
                views.append((
                    view.view_type_name(), 
                    view.view_id(),
                    view_state
                ))
            
        layout = self._get_layout_state()
        state = dict(views=views, layout=layout)
        return state

    def set_views_state(self, state):
        for view in self._views.values():
            view.delete_view()
        self._views.clear()

        from qtpy import QtWidgets
        QtWidgets.QApplication.processEvents()

        views = state.get('views', [])
        view_ids = []
        for view_type_name, view_id, view_state in views:
            view_ids.append(view_id)
            view = self.add_view(view_type_name, view_id)
            view.set_view_state(view_state)

        layout = state.get('layout')
        if layout is not None:
            self._set_layout_state(layout)

    #
    #       LOGGING
    #
    def log(self, context, *words):
        self._log(logging.INFO, ' '.join([str(i) for i in words]), extra={'context': context})

    def log_info(self, message, *args, **kwargs):
        self._log(logging.INFO, message, *args, **kwargs)

    def log_debug(self, message, *args, **kwargs):
        self._log(logging.DEBUG, message, *args, **kwargs)

    def log_error(self, message, *args, **kwargs):
        self._log(logging.ERROR, message, *args, **kwargs)

    def log_warning(self, message, *args, **kwargs):
        self._log(logging.WARNING, message, *args, **kwargs)

    def log_critical(self, message, *args, **kwargs):
        self._log(logging.CRITICAL, message, *args, **kwargs)

    def _log(self, level, message, *args, **kwargs):
        extra = {'user': self.session_uid().split(':')[0]}
        if 'extra' in kwargs:
            extra.update(kwargs['extra'])
            kwargs.pop('extra')
        self.logger.log(level, message, *args, extra=extra, **kwargs)

    def close(self):
        for actor in self._actors.values():
            actor.die()

    def _on_cluster_connected(self):
        for actor in self._actors.values():
            actor.on_session_connected()

    def channels_subscribe(self, **channels_callbacks):
        '''
        Register some handlers for the given channels.
        The handlers will be called with one arg, the message.
        The message is a dict like:
            {
                'channel': channel_name',
                'type': subscription_type  # 'subscribe' or 'psubscribe'
                'data': message_data,

            }
        Beware that if a string was sent as data, message_data will be the 
        byte encoded string. You need to decode it with:
            message_data.decode('utf8')
        Returns a callable w/o arg that will unregister those handlers.
        '''
        # WARNING: should'nt we use cmds only on actors ?!?
        # -> No, this it not to be used by the client code (cli, ui, gui...),
        # Only the Actors can subscibe callbacks (server side code), so there
        # is no cmd for that.
        return self._cluster_actor.channels_subscribe(**channels_callbacks)

    def broadcast(self, *words):
        # FIXME: Clarify if this should use the Cluster cmd or not. If clients
        # (cli, gui, ...) have a need for the command, etc...
        self._cluster_actor.broadcast(*words)

    def publish(self, **channels_messages):
        # FIXME: Clarify if this should use the Cluster cmd or not. If clients
        # (cli, gui, ...) have a need for the command, etc...
        self._cluster_actor.publish(**channels_messages)

    def dispatch_event(self, event_type, **data):
        '''
        Sends an event to all views.
        '''
        #self.log('Event', event_type, data)
        for view_id, view in six.iteritems(self._views):
            view.receive_event(event_type, data)

