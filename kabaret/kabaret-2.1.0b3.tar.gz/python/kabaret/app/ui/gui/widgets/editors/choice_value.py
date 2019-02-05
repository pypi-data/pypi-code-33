
from warnings import warn

from .interface import Editor_Interface

from qtpy import QtWidgets, QtGui, QtCore

class ChoiceValueEditor(QtWidgets.QToolButton, Editor_Interface):
    '''
    This editor lets you choose one items in a choice list.

    Editor Type Names:
        choice
        choices (deprecated)

    Options:
        sorted:     bool (False) - sorts the choices
    '''
    @classmethod
    def can_edit(cls, editor_type_name):
        '''
        Must be implemented to return True if the given editor_type_name
        matches this editor.
        '''
        if editor_type_name in ('choices',):
            warn('Editor Type Name {!r} is deprecated.'.format(editor_type_name))
        return editor_type_name in ('choice', 'choices')  # Flow1 used choices... :/

    def __init__(self, parent, options):
        QtWidgets.QToolButton.__init__(self, parent)
        Editor_Interface.__init__(self, parent)
        self.apply_options(options)

        self.setPopupMode(self.InstantPopup)
        self.setArrowType(QtCore.Qt.NoArrow)
        self._menu = QtWidgets.QMenu(self)
        self.setMenu(self._menu)

        self._current_value = None
        self._sorted = False

    def needs_choices(self):
        '''
        Must be overriden by editor presenting a choice of possible values.
        '''
        return True

    def set_editable(self, b):
        '''
        Must be implemented to prevent editing if b is False.
        Visual cue show also be given to the user.
        '''
        self.setEnabled(b)

    def apply_options(self, options):
        '''
        Must be implemented to configure the editor as
        described by the options dict.
        '''
        pass

    def update(self):
        '''
        Must be implemnented to show the value returned by self.fetch_value()
        Your code should call self._on_updated() at the end.
        '''
        value, choices = self.fetch_value()  # this is because needs_choices() returns True
        self._current_value = value

        if self._sorted:
            choices.sort()

        label = str(value)
        self.setText(label)
        icon = self.get_icon_for(label)
        if icon is not None:
            self.setIcon(icon)
        else:
            self.setIcon(QtGui.QIcon())

        self._menu.clear()

        for choice in choices or []:
            if choice is None:
                label = ''
            else:
                label = str(choice)
            action = self._menu.addAction(
                label, lambda choice=choice: self._on_select(choice))
            icon = self.get_icon_for(label)
            if icon is not None:
                action.setIcon(icon)

        self._on_updated()

    def mousePressEvent(self, *args, **kwargs):
        self.menu().setFixedWidth(self.width() + 50)
        super(ChoiceValueEditor, self).mousePressEvent(*args, **kwargs)

    def _on_select(self, choice):
        self._current_value = choice
        self.apply()

    def get_edited_value(self):
        '''
        Must be implemented to return the value currently displayed.
        '''
        return self._current_value

    def _show_edited(self):
        '''
        Must be implemented to show that the displayed value
        needs to be applied.
        '''
        # This will not happend, the changes are directly applied.
        self.setProperty('edited', True)
        self.setProperty('applying', False)
        self.style().polish(self)
        self.setText('Edited...')

    def _show_applied(self):
        '''
        Must be implemented to show that the displayed value
        as been saved.
        In a clean scenario, applying edits will trigger an update()
        and this state should disapear.
        If you are using the Editor without this kind of round trip,
        you can call update here.
        '''
        self.setProperty('applying', True)
        self.setText('Applying...')

    def _show_clean(self):
        '''
        Must be implemented to show that the displayed value is 
        up to date.
        '''
        self.setProperty('edited', False)
        self.setProperty('applying', False)
        self.style().polish(self)

    def _show_error(self, error_message):
        '''
        Must be implemented to show that the given error occured.
        '''
        self.setProperty('error', True)
        self.style().polish(self)
        msg = '/!\\ ERROR: ' + error_message
        self.setText(msg)
