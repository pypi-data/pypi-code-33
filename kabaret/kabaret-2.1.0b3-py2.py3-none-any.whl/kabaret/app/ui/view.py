'''
    This module defines the ViewMixin which must be used by all "View", ui or gui...
'''

import six

import uuid

class ViewMixin(object):

    @classmethod
    def view_type_name(cls):
        return cls.__name__

    def __init__(self, session, view_id=None):
        object.__init__(self)

        self.session = session
        self._view_id = view_id or str(uuid.uuid4())

        self._view_title = self.view_type_name()
        self._on_view_title_change_callback = None

        self.session.declare_view(self)

    def delete_view(self):
        self.session.forget_view(self)

    def view_id(self):
        return self._view_id

    def set_on_view_title_change(self, f):
        self._on_view_title_change_callback = f

    def set_view_title(self, title):
        self._view_title = title
        if self._on_view_title_change_callback is not None:
            self._on_view_title_change_callback()

    def view_title(self):
        return self._view_title

    def get_view_state(self):
        '''
        Subclass must override this and return a value
        suitable for set_view_stat(state) in order to support
        session managed state.

        Default value is to return {} which tells the system
        to restore the view with its default state.

        To exclude the view from being restored, you must
        override this method and return None
        '''
        return {}

    def set_view_state(self, state):
        '''
        Subclass must override this and use the state value
        returned by get_view_stat(state) in order to support
        session managed state.
        '''
        return 

    def receive_event(self, event, data):
        raise NotImplementedError()

    def goto_requested(self, requested):
        '''
        This is called when someting (another view, most probably)
        wants to alter this view's content.
        Subclass must implement their specific behavior.
        '''
        raise NotImplementedError()
