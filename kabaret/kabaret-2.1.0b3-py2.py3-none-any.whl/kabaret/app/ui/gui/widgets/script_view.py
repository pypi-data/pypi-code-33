
from __future__ import print_function

from qtpy import QtWidgets


from .view import View


class ScriptView(View):

    @classmethod
    def view_type_name(cls):
        return 'Script'

    def __init__(
        self, session, main_window_manager, parent, oid=None, root_oid=None
    ):
        self._start_oid = oid
        self._root_oid = root_oid
        super(ScriptView, self).__init__(session, main_window_manager, parent)

    def _build(
        self,
        top_parent, top_layout, main_parent, header_parent, header_layout
    ):

        self.add_header_tool('*', '*', 'Duplicate View', self.duplicate_view)

        self.view_menu.setTitle('Script')
        self.view_menu.hide()

        lo = QtWidgets.QVBoxLayout()
        lo.setContentsMargins(0, 0, 0, 0)
        main_parent.setLayout(lo)

        p = (
            r'E:\System\Profiles\dee\Dropbox\CODE\kabaredis\deps\py'
            '\pw_MultiScriptEditor-master\pw_MultiScriptEditor-master'
        )
        import sys
        if p not in sys.path:
            sys.path.append(p)

        try:
            import pw_multiScriptEditor.scriptEditor
        except ImportError:
            w = QtWidgets.QLabel(
                'Could not import pw_multiScriptEditor package :/', main_parent)
        else:
            w = pw_multiScriptEditor.scriptEditor.scriptEditorClass(
                self
            )
        lo.addWidget(w)
        w.show()

    def receive_event(self, event, data):
        pass
