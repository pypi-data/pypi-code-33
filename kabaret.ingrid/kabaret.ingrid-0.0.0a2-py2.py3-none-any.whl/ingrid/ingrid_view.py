
from __future__ import print_function

import six
import time
import json
import os

from qtpy import QtWidgets, QtGui, QtCore

try:
    from kabaret.app.ui.gui.widgets.widget_view import DockedView
except ImportError:
    raise RuntimeError('Your kabaret version is too old, for the JobView. Please update !')

from kabaret.app.ui.gui.widgets.flow.flow_field import ObjectActionMenuManager
from kabaret.app.ui.gui.widgets.flow.flow_view import FlowDialogView
from kabaret.app.ui.gui.widgets.editors import editor_factory

from kabaret.app import resources

class GridConfig(object):

    @classmethod
    def collect_grid_configs(cls, session, oid, collected, seen):
        '''
        Adds a list of InGridConfig oids to colleced for each InGrid config 
        found between oid and its root.

        The collected argument must be an empyt list.
        The seen argument must be an empty set.

        '''
        if oid in seen:
            return
        seen.add(oid)

        try:
            config_oids = session.cmds.Flow.call(oid, 'get_ingrid_config_oids', (), {})
        except AttributeError, err:
            pass
        else:
            collected.extend([
                cls(session, config_oid)
                for config_oid in config_oids
            ])

        if '/' in oid[1:]:
            parent_oid = session.cmds.Flow.get_parent_oid(oid, skip_maps=False)
            cls.collect_grid_configs(session, parent_oid, collected, seen)

    def __init__(self, session, config_oid):
        super(GridConfig, self).__init__()
        self.session = session
        self.config_oid = config_oid

    def __eq__(self, other):
        if not type(other) == type(self):
            return False
        return (self.session, self.config_oid) == (other.session, other.config_oid)

    def config_name(self):
        return self.session.cmds.Flow.call(
            self.config_oid,
            'get_config_name', (), {}
        )
        # return self.config_oid.rsplit('/',1)[-1].replace('_', ' ').title()

    def get_related_configs(self):
        related_config_oids = self.session.cmds.Flow.call(
            self.config_oid,
            'get_related_config_oids', (), {}
        )
        return [
            self.__class__(self.session, oid)
            for oid in related_config_oids
        ]

    def rows(self):
        return self.session.cmds.Flow.call(
            self.config_oid,
            'get_rows', (), {}
        )

    def columns(self):
        return self.session.cmds.Flow.call(
            self.config_oid,
            'get_columns', (), {}
        )

    def row_count(self):
        return len(self.rows())

    def column_count(self):
        return len(self.columns())

    def get_cell(self, row, column):
        return self.session.cmds.Flow.call(
            self.config_oid,
            'get_cell', (row, column), {}
        )
    
    def get_actions(self, *row_column_pairs):
        return self.session.cmds.Flow.call(
            self.config_oid,
            'get_actions', row_column_pairs, {}
        )

class GridItem(QtWidgets.QTableWidgetItem):

    def __init__(self, session, default_align=None):
        super(GridItem, self).__init__()
        self.session = session

        self._default_bg = self.background()

        self._default_align = default_align
        self._cell = None
        self._editor = None

    def _get_icon(self, icon_name, resource_folder='icons.flow'):
        if isinstance(icon_name, six.string_types):
            icon_ref = (resource_folder, icon_name)
        else:
            icon_ref = icon_name
        try:
            icon = resources.get_icon(icon_ref, self.tableWidget())
        except resources.NotFoundError as err:
            self.session.log_debug("WARNING: RESOURCE NOT FOUND: %r" % (err,))
            return None
        return icon

    def _get_icon_for(self, text, resource_folder='icons.status'):
        if text is None:
            return None
        first_word = text.split(' ', 1)[0]
        return self._get_icon(first_word.upper(), resource_folder)

    def set_cell(self, cell):
        self._cell = cell
        text = str(cell.get('display', '???'))
        self.setText(text)

        bg = cell.get('bg')
        if bg is not None:
            self.setBackground(
                QtGui.QBrush(QtGui.QColor(bg))
            )
        else:
            self.setBackground(self._default_bg)

        fg = cell.get('fg')
        if fg is not None:
            self.setForeground(
                QtGui.QBrush(QtGui.QColor(fg))
            )

        icon_ref = cell.get('icon')
        if icon_ref is None:
            icon = self._get_icon_for(text)
        else:
            icon = self._get_icon(icon_ref)
        if icon is not None:
            self.setIcon(icon)

        align = cell.get('align', self._default_align)
        if align == 'left':
            self.setTextAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        elif align == 'right':
            self.setTextAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        elif align == 'center':
            self.setTextAlignment(QtCore.Qt.AlignCenter)

        self.setFlags(
            QtCore.Qt.ItemIsEnabled
            | QtCore.Qt.ItemIsSelectable
        )

    def _get_value_and_choices(self):
        value = self._get_value()
        choices = self.session.cmds.Flow.get_value_choices(self.oid())
        return value, choices

    def _get_value(self):
        return self.session.cmds.Flow.get_value(self.oid())

    def _set_value(self, new_value):
        self.stop_edit()
        self.session.cmds.Flow.set_value(
            self.oid(), new_value
        )

    def start_edit(self):
        if self.oid() is None:
            # no editor w/o oid
            return

        if self._editor is not None:
            return

        ui_config = self._cell.get('ui')
        if ui_config:
            editor_type = ui_config.get('editor_type')
            if editor_type is not None:
                self._editor = editor_factory().create(
                    self.tableWidget(), editor_type, ui_config
                )
                getter = self._get_value
                if self._editor.needs_choices():
                    getter = self._get_value_and_choices
                self._editor.configure(getter, self._set_value, self._get_icon_for)
                self._editor.set_editable(ui_config.get('editable', True))
                self._editor.setToolTip(ui_config.get('tooltip', None))
                self._editor.update()
                self.tableWidget().setCellWidget(
                    self.row(), self.column(), self._editor
                )

    def stop_edit(self):
        if self._editor is None:
            return
        self.tableWidget().removeCellWidget(
            self.row(), self.column()
        )
        #self._editor.deleteLater()
        self._editor = None

    def oid(self):
        return self._cell.get('oid')

    def collect_touched(self, oid, collected):
        if oid == self.oid():
            collected.add(self)

class Grid(QtWidgets.QTableWidget):

    def __init__(self, parent, view, session):
        super(Grid, self).__init__(parent)
        self.view = view
        self.setAcceptDrops(True)
        
        self.session = session

        self._mapped_action_manager = ObjectActionMenuManager(
            self.session, self.show_action_dialog
        )
        self._mapped_action_menu = QtWidgets.QMenu(self)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(
            self._on_context_menu
        )

        hh = self.horizontalHeader()
        hh.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        hh.customContextMenuRequested.connect(self._on_hh_context_menu)
        
        vh = self.verticalHeader()
        vh.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        vh.customContextMenuRequested.connect(self._on_vh_context_menu)

        self.cellDoubleClicked.connect(self._on_cell_dbl_clicked)
        self.currentCellChanged.connect(self._on_current_cell_changed)

    def _on_cell_dbl_clicked(self, row, column):
        item = self.item(row, column)
        if item is not None:
            item.start_edit()

    def _on_current_cell_changed(self, row, column, prev_row, prev_column):
        item = self.item(prev_row, prev_column)
        if item is not None:
            item.stop_edit()

    def collect_touched(self, oid):
        collected = set()

        column_count = self.horizontalHeader().count()
        row_count = self.verticalHeader().count()

        for i in range(column_count):
            item = self.horizontalHeaderItem(i)
            item.collect_touched(oid, collected)

        for i in range(row_count):
            item = self.verticalHeaderItem(i)
            item.collect_touched(oid, collected)

        for r in range(row_count):
            for c in range(column_count):
                item = self.item(r, c)
                if item not in collected:
                    item.collect_touched(oid, collected)

        return collected

    def dropEvent(self, event):
        self.view.on_grid_drop_event(event)

    def load_config(self, config):
        self.clear()
        if config is None:
            return

        self.setRowCount(config.row_count())
        self.setColumnCount(config.column_count())

        col_header_set = False
        for row, row_cell in enumerate(config.rows()):
            item = GridItem(self.session, default_align='right')
            self.setVerticalHeaderItem(row, item)
            item.set_cell(row_cell)

            for column, column_cell in enumerate(config.columns()):
                if not col_header_set:
                    item = GridItem(self.session, default_align='center')
                    self.setHorizontalHeaderItem(column, item)
                    item.set_cell(column_cell)

                cell = config.get_cell(row, column)
                item = GridItem(self.session, default_align='center')
                self.setItem(row, column, item)
                item.set_cell(cell)

            col_header_set = True

    def _on_hh_context_menu(self, point):
        header = self.horizontalHeader()
        i = header.logicalIndexAt(point)
        item = self.horizontalHeaderItem(i)
        oid = item.oid()
        if not oid:
            return

        self._mapped_action_manager.update_oid_menu(
            oid, self._mapped_action_menu
        )
        self._mapped_action_menu.addSeparator()
        self._mapped_action_menu.addAction(
            'Open', lambda oid=oid: self.do_action_result({'goto':oid})
        )
        self._mapped_action_menu.popup(
            header.mapToGlobal(point)
        )

    def _on_vh_context_menu(self, point):
        header = self.verticalHeader()
        i = header.logicalIndexAt(point)
        item = self.verticalHeaderItem(i)
        oid = item.oid()
        if not oid:
            return

        self._mapped_action_manager.update_oid_menu(
            oid, self._mapped_action_menu
        )
        self._mapped_action_menu.addSeparator()
        self._mapped_action_menu.addAction(
            'Open', lambda oid=oid: self.do_action_result({'goto':oid})
        )
        self._mapped_action_menu.popup(
            header.mapToGlobal(point)
        )
        
    def _on_context_menu(self, point):
        selected = self.selectedItems()
        if not selected:
            item = self.itemAt(point)
            if not item:
                return
            selected = [item]

        oids = [ i.oid() for i in selected ]
        oids = [ oid for oid in oids if oid is not None ]
        if not oids:
            return
        
        try:
            oids[1]
        except:
            got_actions = self._mapped_action_manager.update_oid_menu(
                oids[0], self._mapped_action_menu
            )
            self._mapped_action_menu.addSeparator()
            self._mapped_action_menu.addAction(
                'Open', lambda oid=oids[0]: self.do_action_result({'goto': oid})
            )
            if len(selected) == 1:
                row = selected[0].row()
                column = selected[0].column()
                action_labels_and_oids = self.view.config.get_actions((row, column))
                if action_labels_and_oids:
                    self._mapped_action_menu.addSeparator()
                    for label, action_oid in action_labels_and_oids:
                        self._mapped_action_menu.addAction(
                            label, lambda oid=action_oid: self.show_action_dialog(oid)
                        )

        else:
            got_actions = self._mapped_action_manager.update_oids_menu(
                oids, self._mapped_action_menu
            )

        if got_actions:
            self._mapped_action_menu.popup(
                self.viewport().mapToGlobal(point)
            )

    # This func name is needed by actions created by self._mapped_action_manager
    def show_action_dialog(self, action_oid):
        if not self.session.cmds.Flow.action_needs_dialog(action_oid):
            self.run_action(action_oid, None)
            return

        dialog = FlowDialogView(
            self.session, 
            view_id=None, 
            source_view_id=self.view.view_id(), 
            parent_widget=self.view, 
            start_oid=action_oid, 
            root_oid=action_oid,
            form_config={},#self.form.config()
        )

        dialog.show()

    # This func name is needed by actions created by self._mapped_action_manager
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
        self.do_action_result(result)

    def do_action_result(self, result):
        if result.get('refresh', False):
            self.refresh()

        goto_oid = result.get('goto')
        if goto_oid is not None:
            target = result.get('goto_target', self.view.view_id())
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

        # NB: no support for 'next_action', but we dont
        # warn about it since actions may define it just 
        # in case they have a dialog
        #next_oid = result.get('next_action')

class InGridView(DockedView):

    @classmethod
    def view_type_name(cls):
        return 'InGrid'

    def __init__(self, session, view_id=None, hidden=False, area=None, config_oid=None):
        super(InGridView, self).__init__(session, view_id, hidden=hidden, area=area)
        if config_oid is not None:
            self.load_config(
                GridConfig(self.session, config_oid)
            )

    def _build(self, top_parent, top_layout, main_parent, header_parent, header_layout):
        self.add_header_tool('*', '*', 'Duplicate View', self.duplicate_view)

        self.config = None

        self._related_layout = QtWidgets.QHBoxLayout()
        self._grid = Grid(main_parent, self, self.session)

        lo = QtWidgets.QVBoxLayout()
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(0)
        lo.addLayout(self._related_layout)
        lo.addWidget(self._grid)

        main_parent.setLayout(lo)

        self.view_menu.setTitle('InGrid')

        a = self.view_menu.addAction('Refresh', self.refresh)
        self.view_menu.addSeparator()
        a = self.view_menu.addAction('Blah')

    def duplicate_view(self):
        config_oid = None
        if self.config:
            config_oid = self.config.config_oid
        super(InGridView, self).duplicate_view(config_oid=config_oid)

    def on_grid_drop_event(self, event):
        mime_data = event.mimeData()
        md = {}
        for format in mime_data.formats():
            md[format] = mime_data.data(format).data()
        oids, urls = self.session.cmds.Flow.from_mime_data(md)

        if oids:
            self.show_select_config_menu(oids)

    def show_select_config_menu(self, oids):
        configs = []
        seen = set([])
        for oid in oids:
            GridConfig.collect_grid_configs(self.session, oid, configs, seen)

        menu = QtWidgets.QMenu(self)
        if configs:
            for config in configs:
                menu.addAction(
                    config.config_name(), 
                    lambda config=config: self.load_config(config)
                )
        else:
            menu.addAction('No InGrid Config found here :/')
        menu.popup(QtGui.QCursor.pos())

    def load_config(self, config):
        if config is not None:
            self.set_view_title(config.config_name())
        else:
            self.set_view_title('InGrid')
        self.config = config
        self.refresh()

    def refresh(self):
        self.refresh_related()
        self._grid.load_config(self.config)

    def refresh_related(self):
        item = self._related_layout.takeAt(0)
        while item:
            item.widget().deleteLater()
            item = self._related_layout.takeAt(0)

        if self.config is None:
            return

        for config in self.config.get_related_configs():
            b = QtWidgets.QPushButton(self)
            b.setText(config.config_name())
            b.clicked.connect(lambda config=config: self.load_config(config))
            self._related_layout.addWidget(b)

    def on_show(self):
        # this is called way to often to brutally refresh, so:
        #self.refresh()
        pass
        
    def receive_event(self, event, data):
        if not self.isVisible() or self.config is None:
            return

        if event == 'flow_touched':
            oid = data['oid']
            items = self._grid.collect_touched(oid)
            for item in items:
                row = item.row()
                column = item.column()
                if -1 in (row, column):
                    # this is a header item
                    #FIXME: use a specific update mecanisme for header items !
                    continue
                cell = self.config.get_cell(item.row(), item.column())
                item.set_cell(cell)

    def goto_request(self, ingrid_config_oid):
        if ingrid_config_oid is not None:
            self.load_config(
                GridConfig(self.session, ingrid_config_oid)
            )
        else:
            self.load_config(None)
        # config = GridConfig(self.session, ingrid_config_oid)
        # configs = []
        # seen = set()
        # GridConfig.collect_grid_configs(self.session, oid, configs, seen)
        # if not configs:
        #     self.set_view_title('No InGrid Config found for '+oid)
        #     self.config = None
        # else:
        #     self.config = configs[0]
        #     self.set_view_title(self.config.config_name())
        # self.refresh()
