from .interface import Editor_Interface

from qtpy import QtWidgets, QtCore

from ..event_filters import IgnoreMouseButton


class TextAreaEditor(QtWidgets.QWidget, Editor_Interface):
    '''
    This editor lets you enter multiline text value.

    Editor Type Names:
        textarea

    Options:
        html:       bool (True)  - Automatically show html as rich text
    '''

    @classmethod
    def can_edit(cls, editor_type_name):
        '''
        Must be implemented to return True if the given editor_type_name
        matches this editor.
        '''
        return editor_type_name in ('textarea',)

    def __init__(self, parent, options):
        QtWidgets.QWidget.__init__(self, parent)
        Editor_Interface.__init__(self, parent)

        # :'( we should not assume parent has this, but I've been looking for
        # another way to have the text edit not too big for more time that I should :'(
        # parent.setFixedHeight(100)
        self.default_height = 100

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(1, 2, 1, 2)
        self.layout().setSpacing(1)

        self._te = QtWidgets.QTextEdit(self)
        self._te.viewport().installEventFilter(IgnoreMouseButton(self._te))

        self._apply_button = QtWidgets.QToolButton(self)
        self._apply_button.setText('Apply')
        self._apply_button.clicked.connect(self._apply_edit)
        self._apply_button.setEnabled(False)

        self.layout().addWidget(self._te)
        self.layout().addWidget(self._apply_button, alignment=QtCore.Qt.AlignRight)

        self.apply_options(options)

    def sizeHint(self):
        return QtCore.QSize(self.default_height,100)

    def set_editable(self, b):
        '''
        Must be implemented to prevent editing if b is False.
        Visual cue should also be given to the user.
        '''
        self._te.setReadOnly(not b)
        self._apply_button.setVisible(b)
        if b:
            self._te.textChanged.connect(self._show_edited)

    def apply_options(self, options):
        '''
        Must be implemented to configure the editor as
        described by the options dict.
        '''
        self._te.setAcceptRichText(options.get('html', False))

    def _apply_edit(self):
        self.apply()

    def update(self):
        '''
        Must be implemnented to show the value returned by self.fetch_value()
        Your code should call self._on_updated() at the end.
        '''
        txt = str(self.fetch_value() or '')
        if not self._te.acceptRichText():
            self._te.setPlainText(txt)
        else:
            self._te.setHtml(txt)
        self._on_updated()

    def get_edited_value(self):
        '''
        Must be implemented to return the value currently displayed.
        '''
        value = self._te.toPlainText()
        return value

    def _show_edited(self):
        '''
        Must be implemented to show that the displayed value
        needs to be applied.
        '''
        self._apply_button.setEnabled(True)
        self._te.setProperty('edited', True)
        self._te.setProperty('applying', False)
        self.style().unpolish(self._te)
        self.style().polish(self._te)

    def _show_applied(self):
        '''
        Must be implemented to show that the displayed value
        as been saved.
        In a clean scenario, applying edits will trigger an update()
        and this state should disapear.
        If you are using the Editor without this kind of round trip,
        you can call update here.
        '''
        self._apply_button.setEnabled(False)
        self._te.setProperty('edited', False)
        self._te.setProperty('applying', True)
        self.style().unpolish(self._te)
        self.style().polish(self._te)

    def _show_clean(self):
        '''
        Must be implemented to show that the displayed value is
        up to date.
        '''
        self._apply_button.setEnabled(False)
        self._te.setProperty('edited', False)
        self._te.setProperty('applying', False)
        self.style().unpolish(self._te)
        self.style().polish(self._te)

    def _show_error(self, error_message):
        '''
        Must be implemented to show that the given error occured.
        '''
        self._apply_button.setEnabled(False)
        self._te.setProperty('error', True)
        self.style().unpolish(self._te)
        self.style().polish(self._te)
        self.setToolTip('!!!\nERROR: %s' % (error_message,))