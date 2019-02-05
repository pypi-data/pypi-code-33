'''

    kabaret.flow2.action

    Defines the Action class, an object on which UI commands can call
    the run() method to execute some code.

    The return value of run() dictates some UI behavior
    (see Action.run() doc).

    Defines the DropAction class, an object used to handle GUI drops
    on the ConnectAction parent.
    (NB: it is not a subclasse of Action and wont show up as a button)

'''

from .object import Object
from .relations import SessionParam, Parent


class Action(Object):

    ICON = 'action'

    # does this action shows in parent's inline GUI ?
    SHOW_IN_PARENT_INLINE = True
    # does this action shows in parent's detailed GUI ?
    SHOW_IN_PARENT_DETAILS = True

    message = SessionParam().ui(editor='label', wrap=True).ui(editable=False, label='')

    @classmethod
    def get_result(
            cls, close=None, refresh=None,
            goto=None, next_action=None
    ):
        '''
        The value returned by run(button) will be inspected by callers to
        decide how they should react.
        This helper class method will generate a result matching its args:
            close: (bool)
                Prevent the action dialog to be closed when set to False
            refresh: (bool)
                Force a reload of the parent page avec dialog close
                (This should not be needed anymore thanks to touch() calls...)
            goto: (oid)
                Force the caller to load the given oid page.
            next_action: (oid)
                Force the dialog to not close but load the ui for the action
                with the given oid.
                This is the way to implement "Wizard Pages"

        '''
        ret = {}
        if close is not None:
            ret['close'] = close and True or False
        if refresh is not None:
            ret['refresh'] = refresh and True or False
        if goto is not None:
            ret['goto'] = goto

        if next_action is not None:
            ret['next_action'] = next_action

        return ret

    def needs_dialog(self):
        '''
        May be overriden by subclasses to return False if the action
        does not need to show a dialog.
        Action without dialog are called with run(button=None), plus the 'goto'
        and 'next_action' fields of the returned value do the same.

        NB: If the action cannot run, it should show a dialog wiht a
        desciption why in self.message
        '''
        return True

    def get_buttons(self):
        '''
        Returns a list of string suitable as the 'button' argument for a
        call to self.run().

        NB: If the action cannot run, you should set a desciption why
        in self.message, return ['Cancel'] and handle that in run().
        This is far better than returning False from needs_dialog() or let
        the run() method decide to do nothing since the user will not have
        a clear feedback showing that nothing happened...
        '''
        return ['Run']

    def run(self, button):
        '''
        The return value should be None or the return value of
        a self.get_result() call.
        GUI will inspect the returned value and act upon it.
        '''
        self.message.set('This is an abstract action and it cannot be used.')
        return self.get_result(close=False)


class ConnectAction(Object):
    '''
    Subclasses will want to overwrite:
        - accept_label: return the label to show in GUI if the objects and urls are
        acceptable, None otherwise.
        - run: to do the job.

    The run method is guaranted to be called only if accept_label did not return None.
    '''

    def accept_label(self, objects, urls):
        return 'Drop %i Oject(s)/File(s) here' % (len(objects) + len(urls),)

    def run(self, objects, urls):
        raise NotImplementedError()


class ChoiceValueSetAction(Action):

    SHOW_IN_PARENT_INLINE = False
    VALUE_TO_SET = None

    _choice_value = Parent()

    def needs_dialog(self):
        return False

    def run(self, button):
        self._choice_value.set(self.VALUE_TO_SET)


class ChoiceValueSelectAction(Action):

    SHOW_IN_PARENT_INLINE = False

    _choice_value = Parent()

    def get_buttons(self):
        return self._choice_value.choices()

    def run(self, button):
        self._choice_value.set(button)
