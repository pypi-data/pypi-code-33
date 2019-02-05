import six
import logging
from qtpy import QtWidgets, QtGui, QtCore

from kabaret.app import resources

from .. import event_filters
from .flow_field import FlowField, FormField, ObjectSummary, ObjectActionMenuManager, ObjectActionsMenu


class _MapField(FormField):

    def __init__(self, parent, map_widget):
        self.map_widget = map_widget
        super(_MapField, self).__init__(parent)
        self.setFlags(QtCore.Qt.NoItemFlags)

    def build(self):
        self.setItemWidget(1, self.map_widget)

    def on_touch_event(self, oid):
        pass


class MapFieldTreeItem(QtWidgets.QTreeWidgetItem):

    def __init__(self, parent, oid, row):
        super(MapFieldTreeItem, self).__init__(parent)
        self.oid = oid
        self.update_row(row)

    def update_row(self, row):
        tree = self.treeWidget()
        columns = tree.columns

        style = row.get('_style', {})
        icon = style.get('icon')
        if icon:
            if isinstance(icon, six.string_types):
                icon_ref = ('icons.flow', icon)
            else:
                icon_ref = icon
            try:
                icon = resources.get_icon(icon_ref, tree)
            except resources.NotFoundError as err:
                logging.getLogger('kabaret.ui').debug("WARNING: RESOURCE NOT FOUND: %r" % (err,))
                self.setIcon(0, QtGui.QIcon())
            else:
                self.setIcon(0, icon)

        for i, col in enumerate(columns):
            icon = style.get(col + '_icon')
            if icon:
                if isinstance(icon, six.string_types):
                    icon_ref = ('icons.flow', icon)
                else:
                    icon_ref = icon
                try:
                    icon = resources.get_icon(icon_ref, tree)
                except resources.NotFoundError as err:
                    logging.getLogger('kabaret.ui').debug("WARNING: RESOURCE NOT FOUND: %r" % (err,))
                    # remove any previously set icon
                    self.setIcon(i, QtGui.QIcon())
                else:
                    self.setIcon(i, icon)
            self.setText(i, str(row.get(col, '!')))


class MapFieldTree(QtWidgets.QTreeWidget):

    def __init__(self, field, parent):
        super(MapFieldTree, self).__init__(parent)
        self.field = field
        self.session = field.session

        self.setRootIsDecorated(False)
        self.setColumnCount(0)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setSortingEnabled(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.setDropIndicatorShown(True)
        self.setProperty("table", True)
        self.columns = []
        self.auto_fit = True
        self.columns_width = None
        self.sort_by = -1
        self.sort_order = _str_to_qt_order('asc')

        self.installEventFilter(self)

    def apply_options(self, ui_config):
        self.sort_by = ui_config.get('sort_by', self.sort_by)
        self.sort_order = _str_to_qt_order(ui_config.get('sort_order', 'asc'))
        self.auto_fit = ui_config.get('auto_fit', self.auto_fit)
        self.columns_width = ui_config.get('columns_width', self.columns_width)
        style = ui_config.get('style', {})
        stylesheet = ""
        if 'header_color' in style:
            stylesheet += \
                'QHeaderView::section {'\
                '   background-color: rgb(%d,%d,%d);'\
                '}' % style.get('header_color')
        if 'background_color' in style:
            stylesheet += \
                'QTreeView[table = "true"] {'\
                '   background-color: rgb(%d,%d,%d);'\
                '}' % style.get('background_color')
        if stylesheet:
            self.setStyleSheet(stylesheet)

    def column_id(self, column_text):
        for i, col in enumerate(self.columns):
            if col.upper() == column_text.upper():
                return i
        return -1

    def set_columns(self, columns):
        self.columns = columns
        self.setHeaderLabels(self.columns)
        self.setColumnCount(len(self.columns))

    def set_items(self, items):
        for oid, row in items:
            MapFieldTreeItem(self, oid, row)

        self.update_column_width()

        if isinstance(self.sort_by, int):
            self.sortItems(self.sort_by, self.sort_order)
        elif isinstance(self.sort_by, str):
            self.sortItems(self.column_id(self.sort_by), self.sort_order)

    def update_column_width(self):
        if self.auto_fit:
            [self.resizeColumnToContents(i) for i, col in enumerate(self.columns)]
        elif self.columns_width:
            for i, width in enumerate(self.columns_width):
                self.setColumnWidth(i, self.width() * width / 100)

    def resizeEvent(self, *args, **kwargs):
        self.update_column_width()
        super(MapFieldTree, self).resizeEvent(*args, **kwargs)

    def mimeData(self, items):
        # print(items)

        mime_data = super(MapFieldTree, self).mimeData(items)
        oids = [item.oid for item in items]
        md = self.session.cmds.Flow.to_mime_data(oids)
        for data_type, data in six.iteritems(md):
            mime_data.setData(data_type, data)

        return mime_data

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction

    def dragEnterEvent(self, event):
        if not event.mouseButtons() & QtCore.Qt.LeftButton:
            event.ignore()
            return
        if self.session.cmds.Flow.can_handle_mime_formats(
            event.mimeData().formats()
        ):
            event.acceptProposedAction()
        else:
            super(MapFieldTree, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if self.session.cmds.Flow.can_handle_mime_formats(
            event.mimeData().formats()
        ):
            event.acceptProposedAction()
        else:
            super(MapFieldTree, self).dragMoveEvent(event)

    def dropMimeData(self, parent, index, mime_data, drop_action):
        md = {}
        for format in mime_data.formats():
            md[format] = mime_data.data(format).data()
        oids, urls = self.session.cmds.Flow.from_mime_data(md)

        if not oids and not urls:
            return False    # let the event propagate up

        connection_targets = self.session.cmds.Flow.get_connection_targets(
            self.field.oid, oids, urls
        )
        if not connection_targets:
            return False    # let the event propagate up

        if len(connection_targets) == 1:
            target_oid, label, icon = connection_targets[0]
            self.session.cmds.Flow.connect(
                target_oid, oids, urls
            )
            return True

        m = QtWidgets.QMenu(self)
        for target_oid, label, icon_name in connection_targets:
            a = m.addAction(label)
            a.triggered.connect(
                lambda
                toggled=None,
                target_oid=target_oid,
                oids=oids,
                urls=urls: self.field.do_connect(
                    target_oid, oids, urls)
            )
            icon = self.field._get_icon(icon_name)
            if icon is not None:
                a.setIcon(icon)
        m.exec_(QtGui.QCursor.pos())

        return True

    def mousePressEvent(self, e):
        super(MapFieldTree, self).mousePressEvent(e)

        if e.button() == QtCore.Qt.RightButton:
            # NB: We set CustomContextMenu only here to prevent the
            # menu to be updated / shown uppon mouseReleaseEvent wich
            # can hapen far from the item
            self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.customContextMenuRequested.emit(e.pos())
            self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
            
    def mouseMoveEvent(self, e):
        if not e.buttons() & QtCore.Qt.LeftButton:
            e.ignore()
            return
        super(MapFieldTree, self).mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        super(MapFieldTree, self).mouseReleaseEvent(e)

    def get_item(self, oid):
        # TODO: see if this is worth optimizing this with a id->item map
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            # print('       ', item.oid)
            if item.oid == oid:
                return item
        return None

    def apply_filter(self, filter):
        it = QtWidgets.QTreeWidgetItemIterator(self)
        col_indexes = range(self.columnCount())
        lfilter = filter.lower()
        if ':' in lfilter:
            col_index, lfilter = lfilter.split(':', 1)
            try:
                col_index = int(col_index)
            except ValueError:
                pass
            else:
                col_indexes = [col_index - 1]

        while it.value():
            item = it.value()
            matched = False
            for c in col_indexes:
                if lfilter in item.text(c).lower():
                    matched = True
                    break
            item.setHidden(not matched)
            it += 1

    def eventFilter(self, *args, **kwargs):
        event = args[1]
        if event.type() == QtCore.QEvent.Wheel:
            event.accept()
            super(MapFieldTree, self).eventFilter(*args, **kwargs)
            if self.verticalScrollBar().isVisible():
                return True
            return False
        return super(MapFieldTree, self).eventFilter(*args, **kwargs)


class MapFieldFilterLineEdit(QtWidgets.QLineEdit):

    def __init__(self, parent, map_tree):
        super(MapFieldFilterLineEdit, self).__init__(parent)
        self.map_tree = map_tree
        self.textEdited.connect(self._on_edit)

        self.setToolTip(
            'Filter list (not case sensitive)\n'
            'Use "1:blah" to match only first column.'
        )

    def _on_edit(self, text):
        self.map_tree.apply_filter(text)

    def dropEvent(self, e):
        md = e.mimeData()
        if md.hasFormat('kabaret/flow_oid'):
            oid = str(md.data('kabaret/flow_oid'))
            e.acceptProposedAction()
            self.setText(oid[0])
        else:
            super(MapFieldFilterLineEdit, self).dropEvent(e)


def _str_to_qt_order(string):
    return QtCore.Qt.AscendingOrder if string.startswith("a") else QtCore.Qt.DescendingOrder


class MapField(FlowField):

    def __init__(self, parent, session, oid, ui_config=None):
        self._mapped_action_manager = None
        self._mapped_action_menu = None
        self._map_tree = None
        self._lock = False
        super(MapField, self).__init__(parent, session, oid, ui_config)

    def goto(self):
        self.treeWidget().goto(self.oid)

    def build_children(self):
        tree = self.treeWidget()

        w = QtWidgets.QWidget(tree)
        resizer = event_filters.MouseResizer(w, self.update_height, horizontal=False)
        resizer.propagate_events = False
        w.installEventFilter(resizer)

        lo = QtWidgets.QVBoxLayout()
        lo.setContentsMargins(2, 2, 2, 2)
        lo.setSpacing(0)
        w.setLayout(lo)

        self._map_tree = MapFieldTree(self, None)
        self._map_tree.itemDoubleClicked.connect(
            self._on_mapped_double_clicked
        )
        self._map_tree.customContextMenuRequested.connect(
            self._on_mapped_context_menu
        )
        self._map_tree.installEventFilter(
            event_filters.IgnoreMouseButton(self._map_tree)
        )
        self._map_tree.viewport().installEventFilter(
            event_filters.IgnoreMouseButton(self._map_tree)
        )

        self._map_tree.apply_options(self.ui_config)

        if self.ui_config.get('show_filter', False):
            fle = MapFieldFilterLineEdit(w, self._map_tree)
            fle.setVisible(True)
            fle.setPlaceholderText("Filter...")
            w.layout().addWidget(fle)

        lo.addWidget(self._map_tree)

        default_height = self.ui_config.get('default_height')
        if default_height:
            w.setFixedHeight(default_height)

        self.addChild(_MapField(self, w))
        self.update_content()

    def activated(self, col):
        if not super(MapField, self).activated(col):
            # It it did not open another window:
            if col == 0:
                self.goto()
            else:
                if not self.isExpanded():
                    self.ensure_children_built()
                    self.setExpanded(True)
                else:
                    self.setExpanded(False)

    def _inspect_touch_event(self, oid):
        if super(MapField, self)._inspect_touch_event(oid):
            return True
        if self._map_tree:
            item = self._map_tree.get_item(oid)
            if item is not None:
                row = self.session.cmds.Flow.get_mapped_row(self.oid, oid)
                item.update_row(row)
                return True
        # print(':/')
        return False

    def update_content(self):
        if self._map_tree:
            self._map_tree.clear()

            self._map_tree.set_columns(self.session.cmds.Flow.get_mapped_columns(self.oid))
            self._map_tree.set_items(self.session.cmds.Flow.get_mapped_rows(self.oid))

    def build(self):
        # self.setTextAlignment(0, QtCore.Qt.AlignCenter|QtCore.Qt.AlignRight)
        self.setFlags(QtCore.Qt.ItemIsEnabled)  # not selectable

        tree = self.treeWidget()

        self._mapped_action_manager = ObjectActionMenuManager(
            self.session, tree.show_action_dialog
        )
        self._mapped_action_menu = QtWidgets.QMenu(tree)

        top_w = QtWidgets.QWidget(tree)
        top_lo = QtWidgets.QHBoxLayout()
        top_lo.setContentsMargins(2, 2, 2, 2)
        top_w.setLayout(top_lo)

        actions_menu = ObjectActionsMenu(
            self.session, top_w, tree.show_action_dialog
        )
        top_lo.addWidget(actions_menu)

        summary = ObjectSummary(self.session, top_w)
        summary.load_summary(self.oid)
        top_lo.addWidget(summary)
        top_lo.addStretch()

        actions_menu.load_actions(self.oid)
        self.setText(0, self._label)
        self.setItemWidget(1, top_w)
        self.show_may_have_children()

    def _on_mapped_double_clicked(self, item, col):
        if not self._lock:  # avoid double goto
            self.treeWidget().goto(item.oid)
            self._lock = True

    def _on_mapped_context_menu(self, point):
        if self._map_tree:
            selected = self._map_tree.selectedItems()
            # double check with itemAt bc there's a thing
            # going on when... whatever... trust me -__-"
            item = self._map_tree.itemAt(point)
            if not item:
                return

            try:
                selected[1]
            except IndexError:
                # fall back to single item when only one is selected:
                selected = None

            if not selected:
                got_actions = self._mapped_action_manager.update_oid_menu(
                    item.oid, self._mapped_action_menu
                )
            else:
                got_actions = self._mapped_action_manager.update_oids_menu(
                    [i.oid for i in selected], self._mapped_action_menu
                )

            if got_actions:
                self._mapped_action_menu.exec_(
                    self._map_tree.viewport().mapToGlobal(point)
                )

    def do_connect(self, target_oid, source_oids, source_urls):
        #print("Connecting", target_oid, source_oids, source_urls)
        self.session.cmds.Flow.connect(
            target_oid, source_oids, source_urls
        )
