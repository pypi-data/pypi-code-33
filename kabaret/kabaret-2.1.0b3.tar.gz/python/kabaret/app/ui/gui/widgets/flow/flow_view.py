import os
import six
from qtpy import QtWidgets, QtCore

from ...icons import flow  # noqa # to be sure flow icons are registered.

#!!from ..view import View
from ..widget_view import DockedView, DialogView

from .. import event_filters

from .flow_form import FlowForm
from .navigator import Navigator
from .navigation_control import (
    NavigationOIDControls,
    NavigationHistoryControls,
    NavigationBar
)
from .script_line import ScriptLine


class FlowPage(QtWidgets.QWidget):

    def __init__(self, parent, view, start_oid, root_oid):
        super(FlowPage, self).__init__(parent)

        self.view = view
        self.session = view.session

        self._navigator = Navigator(
            self.session, root_oid, start_oid
        )
        self._navigator.set_create_view_function(view.create_view)

        self.nav_bar = NavigationBar(self, self._navigator)
        self.nav_ctrl = self.nav_bar.nav_ctrl
        self.nav_oid = self.nav_bar.nav_oid

        self.form = FlowForm(self, self)

        lo = QtWidgets.QVBoxLayout()
        lo.addWidget(self.nav_bar)
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(0)
        self.setLayout(lo)
        lo.addWidget(self.form, 100)

        self._navigator.add_on_current_changed(self.refresh)

        self._source_view_id = None
        # self._dialogs = {}  # oid to dialg widget

        #FIXME: wtf is this ?!? why isn't this in NavigationBar class ?!?
        self.nav_bar.setAttribute(QtCore.Qt.WA_StyledBackground, True)

    def root_oid(self):
        return self._navigator.root_oid()

    def current_oid(self):
        return self._navigator.current_oid()

    def set_source_view_id(self, source_view_id):
        '''
        Used by run_action to find affected vie by stuffs like 'goto' request
        '''
        self._source_view_id = source_view_id

    def open(self, oid):
        self._navigator.goto(oid, new_view=True)

    def goto(self, oid):
        in_new_view = (
            QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier
        )
        self._navigator.goto(oid, in_new_view)

    def goto_connected(self, oid):
        in_new_view = (
            QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier
        )
        self._navigator.goto_parent_of(oid, in_new_view)

    def show_action_dialog(self, action_oid):
        if not self.session.cmds.Flow.action_needs_dialog(action_oid):
            self.run_action(action_oid, None)
            return

        # try:
        #     dialog = self._dialogs[action_oid]
        # except:
        #     pass
        # else:
        #     dialog.show()
        #     dialog.raise_()
        #     dialog.activateWindow()
        #     return

        dialog = FlowDialogView(
            self.session, 
            view_id=None, 
            source_view_id=self.view.view_id(), 
            parent_widget=self.view, 
            start_oid=action_oid, 
            root_oid=action_oid,
            form_config=self.form.config()
        )

        # def on_dialog_close(result, page=self, oid=action_oid):
        #     # dialog = page._dialogs.pop(oid)
        #     dialog.forget_dialog_view()
        #     dialog.deleteLater()
        # dialog.finished.connect(on_dialog_close)

        # self._dialogs[action_oid] = dialog

        dialog.show()

    def run_action(self, action_oid, button):
        # if from_dialog and self._master_page is not None:
        #     self._master_page.run_action(action_oid, button)
        #     return

        # if from_dialog:
        #     dialog = self._dialogs[action_oid]
        #     page = dialog.flow_page
        # else:
        #     dialog = None
        #     page = self

        result = self.session.cmds.Flow.run_action(action_oid, button)
        result = result or {}

        if result.get('refresh', False):
            self.refresh()

        goto_oid = result.get('goto')
        if goto_oid is not None:
            target = result.get('goto_target', self._source_view_id)
            if target is None:
                target = self.view.view_id()
            view_type_name = result.get('goto_target_type', 'Flow')
            view = self.session.find_view(
                view_type_name=view_type_name, 
                view_id=target
            )
            if view is None:
                new_view_id = None
                if target != '_NEW_':
                    new_view_id = target
                view = self.session.add_view(
                    view_type_name=view_type_name, 
                    view_id=new_view_id
                )
            view.goto_request(goto_oid)

        next_oid = result.get('next_action')
        if next_oid is not None:
            self.goto(next_oid)
            return

        if result.get('close', True):
            self.view.on_action_result_close()

    def clear(self):
        self.form.clear()

    def refresh(self):
        oid = self.current_oid()
        view_title = self.session.cmds.Flow.get_source_display(oid)
        self.view.set_view_title(view_title)

        self.clear()

        self.nav_oid.update()
        self.nav_ctrl.update()

        self.form.build_roots(oid)

    def receive_event(self, event, data):
        # print('   --- FlowPage got event', event, data)
        if event == 'flow_touched':
            oid = data['oid']
            root = self.form.invisibleRootItem()
            for i in range(root.childCount()):
                item = root.child(i)
                item.on_touch_event(oid=oid)
            # for oid, dialog in six.iteritems(self._dialogs):
            #     page = dialog.flow_page
            #     page.receive_event(event, data)


class FlowDialogView(DialogView):

    def __init__(self, session, view_id, parent_widget, source_view_id, start_oid, root_oid, form_config):
        super(FlowDialogView, self).__init__(session, view_id, parent_widget)

        self.setWindowTitle(root_oid)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.flow_page = FlowPage(self, self, start_oid, root_oid)
        self.flow_page.set_source_view_id(source_view_id)
        self.flow_page.form.configure(**form_config)

        self.layout().addWidget(self.flow_page)

        sg = QtWidgets.QSizeGrip(self)
        sg.setMinimumSize(5,5)
        self.layout().addWidget(sg, 0, QtCore.Qt.AlignRight)

        self.installEventFilter(event_filters.EatEnterKeys())
        self.flow_page.form.viewport().installEventFilter(
            event_filters.MouseResizer(self)
        )        

    def goto_request(self, oid):
        self.flow_page.goto(oid)

    def create_view(self, oid=None):
        # Needed as being the view of a FlowPage()
        pass

    def fitSize(self):
        self.flow_page.form.fitSize()
        self.flow_page.adjustSize()
        self.adjustSize()

    def show(self):
        super(FlowDialogView, self).show()
        self.flow_page.refresh()
        self.fitSize()

    def receive_event(self, event, data):
        # print('   --- FlowDialogView got event', event, data)
        if event == 'flow_touched':
            self.flow_page.receive_event(event, data)

    def on_action_result_close(self):
        self.accept()

# class XX_FlowDialog(QtWidgets.QDialog):

#     def __init__(self, master_page, parent, view, start_oid, root_oid):
#         super(FlowDialog, self).__init__(parent)

#         self.setWindowTitle(root_oid)

#         self.setLayout(QtWidgets.QVBoxLayout())
#         self.layout().setContentsMargins(0, 0, 0, 0)

#         self.flow_page = FlowPage(self, view, start_oid, root_oid)
#         self.flow_page.set_master_page(master_page)
#         self.flow_page.form.configure(**master_page.form.config())

#         self.layout().addWidget(self.flow_page)

#         sg = QtWidgets.QSizeGrip(self)
#         sg.setMinimumSize(5,5)
#         self.layout().addWidget(sg, 0, QtCore.Qt.AlignRight)

#         self.installEventFilter(event_filters.EatEnterKeys())
#         self.flow_page.form.viewport().installEventFilter(
#             event_filters.MouseResizer(self)
#         )

#         self.setProperty("dialog", True)

#     def fitSize(self):
#         self.flow_page.form.fitSize()
#         self.flow_page.adjustSize()
#         self.adjustSize()

#     def show(self):
#         super(FlowDialog, self).show()
#         self.flow_page.refresh()
#         self.fitSize()

class FlowView(DockedView):

    @classmethod
    def view_type_name(cls):
        return 'Flow'

    def __init__(self, session, view_id=None, hidden=False, area=None, oid=None, root_oid=None):
        self._start_oid = oid
        self._root_oid = root_oid
        self.dev_menu = None
        self.script_line = None
        self.flow_page = None
        super(FlowView, self).__init__(session, view_id, hidden=hidden, area=area)

    def build_top(self, top_parent, top_layout, header_parent, header_layout):
        self.add_header_tool('*', '*', 'Duplicate View', self.create_view)

        self.view_menu.setTitle('Options')
        a = self.view_menu.addAction('Show Hidden Relations')
        a.setCheckable(True)
        a.setChecked(False)
        a.toggled.connect(self.set_show_hidden_relations)

        a = self.view_menu.addAction('Show References')
        a.setCheckable(True)
        a.setChecked(False)
        a.toggled.connect(self.set_show_references_relations)

        self.view_menu.addAction('Create New View')
        self.view_menu.addSeparator()
        self.view_menu.addAction(
            'Activate DEV Tools',
            self._activate_dev_tools
        )

        self.script_line = ScriptLine(top_parent, self)
        self.script_line.hide()
        top_layout.addWidget(self.script_line, 100)

    def build_page(self, main_parent):
        self.flow_page = FlowPage(
            main_parent, self, self._start_oid, self._root_oid
        )

        lo = QtWidgets.QVBoxLayout()
        lo.setContentsMargins(0, 0, 0, 0)
        lo.addWidget(self.flow_page)
        self.flow_page.show()

        main_parent.setLayout(lo)
        self.flow_page.refresh()

    def _build(self, top_parent, top_layout, main_parent, header_parent, header_layout):
        self.build_top(top_parent, top_layout, header_parent, header_layout)
        self.build_page(main_parent)

    def get_view_state(self):
        self.setObjectName(self.view_id())
        self.dock_widget().setObjectName(self.view_id())
        
        return dict(
            oid=self.flow_page.current_oid(),
            root_oid=self._root_oid,
            form_config=self.flow_page.form.config()
        )

    def set_view_state(self, state):
        oid = state.get('oid', self.flow_page.current_oid())
        root_oid = state.get('root_oid', self._root_oid)
        form_config = state.get('form_config')

        if form_config is not None:
            self.flow_page.form.configure(**form_config)

        self._start_oid = oid
        self._root_oid = root_oid
        self.flow_page._navigator._root_oid = root_oid # ugly !!! add a public api for that !
        self.flow_page.goto(oid)

    def set_show_references_relations(self, b):
        self.flow_page.form.configure(show_references_relation=b)

    def set_show_hidden_relations(self, b):
        self.flow_page.form.configure(show_hidden_relations=b)

    def set_show_protected_relations(self, b):
        self.flow_page.form.configure(show_protected_relations=b)

    def set_group_relations(self, b):
        self.flow_page.form.configure(group_relations=b)

    def toggle_script_line(self):
        self.script_line.setVisible(not self.script_line.isVisible())

    def reload_projects(self):
        self.session.cmds.Flow.reload_project(self.flow_page.current_oid())
        self.flow_page.refresh()

    def _activate_dev_tools(self):
        if self.dev_menu is not None:
            return
        self.dev_menu = self.menubar.addMenu('[DEV]')

        self.dev_menu.addAction('Toggle Script Line', self.toggle_script_line)

        a = self.view_menu.addAction('Group Relations')
        a.setCheckable(True)
        a.setChecked(True)
        a.toggled.connect(self.set_group_relations)

        a = self.dev_menu.addAction('Show Protected Relations')
        a.setCheckable(True)
        a.setChecked(False)
        a.toggled.connect(self.set_show_protected_relations)

        self.dev_menu.addSeparator()

        self.dev_menu.addAction('Reload Projects Definition', self.reload_projects)

        self.toggle_script_line()

    def create_view(self, oid=None):
        if oid is None:
            oid = self.flow_page.current_oid()
        self.duplicate_view(oid=oid)

    def receive_event(self, event, data):
        # print('   --- FlowView got event', event, data)
        if event == 'flow_touched':
            self.flow_page.receive_event(event, data)

    def on_action_result_close(self):
        '''
        This is called when an action show in self.flow_page is run and its result
        requests closing the containing view.
        This has meaning only for a DialogView so nothing is done here.
        '''
        pass

    def goto_request(self, oid):
        self.flow_page.goto(oid)

class FlowContextView(FlowView):

    @classmethod
    def get_context_oid(cls):
        return os.environ.get('KABARET_CONTEXT_OID')

    @classmethod
    def view_type_name(cls):
        return 'Context'

    #def __init__(self, session, view_id=None, hidden=False, area=None, oid=None, root_oid=None):

    def __init__(
        self, session, view_id=None, hidden=False, area=None,
    ):
        self._context_oid = self.get_context_oid()
        super(FlowContextView, self).__init__(
            session, view_id=view_id, hidden=hidden, area=area,
            oid=self._context_oid, root_oid=self._context_oid
        )

        self.set_view_title("Kabaret Context")

    def create_view(self, oid=None):
        if oid is None:
            oid = self.get_context_oid()
        self.duplicate_view(oid=oid)