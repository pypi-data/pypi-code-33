import six
from qtpy import QtWidgets, QtGui, QtCore
import qtpy

from kabaret.app import resources
from ..flow_layout import FlowLayout


class NavigationButton(QtWidgets.QToolButton):

    def __init__(self, name, oid, nav_widget):
        super(NavigationButton, self).__init__(nav_widget)
        self.name = name
        self.oid = oid
        self.nav_widget = nav_widget

        self.setFont(self.nav_widget.bt_font)
        self.setProperty('tight_layout', True)
        self.setProperty('hide_arrow', True)
        self.setProperty('no_border', True)
        self.setProperty('square', True)
        self.setArrowType(QtCore.Qt.NoArrow)
        # self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        self.setText('/%s' % (self.name,))

        self.clicked.connect(self._goto)

        self._menu = QtWidgets.QMenu(self)

    def _goto_oid(self, oid):
        self.nav_widget._goto(oid)

    def _goto(self, b=None):
        self.nav_widget._goto(self.oid)

    def _show_navigables_menu(self, full_oid):
        self._menu.clear()

        m = self._menu

        m.addAction('Loading...')
        # self.setMenu(m)
        # self.showMenu()
        m.popup(QtGui.QCursor.pos())

        session = self.nav_widget._navigator.session
        try:
            navigatable_entries = session.cmds.Flow.get_navigable_oids(
                self.oid, full_oid
            )
        except Exception as err:
            m.clear()
            m.addAction('ERROR: ' + str(err))
            raise

        m.clear()
        i = 0
        for entry in navigatable_entries:
            i += 1
            if not i % 20:
                m = m.addMenu('More...')
            if entry is None:
                m.addSeparator()
            else:
                label, oid = entry
                if oid == self.oid:
                    label = '<%s>' % (label,)
                m.addAction(
                    label, lambda oid=oid: self._goto_oid(oid)
                )

        # self.setMenu(None)
        # m.deleteLater()
        # return m

    def mousePressEvent(self, e):
        if e.button() == QtCore.Qt.RightButton:
            self._show_navigables_menu(self.nav_widget.current_oid())
        return super(NavigationButton, self).mousePressEvent(e)

    def mouseMoveEvent(self, e):
        if not e.buttons() & QtCore.Qt.LeftButton:
            return

        oids = [self.oid]
        mime_data = QtCore.QMimeData()
        md = self.nav_widget._navigator.session.cmds.Flow.to_mime_data(oids)
        for data_type, data in six.iteritems(md):
            mime_data.setData(data_type, data)

        if qtpy.API_NAME == 'PyQt5':
            pixmap = self.grab()
        else:
            pixmap = QtGui.QPixmap.grabWidget(self)

        # below makes the pixmap half transparent
        painter = QtGui.QPainter(pixmap)
        painter.setCompositionMode(painter.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), QtGui.QColor(0, 0, 0, 127))
        painter.end()

        # make a QDrag
        drag = QtGui.QDrag(self)
        # put our MimeData
        drag.setMimeData(mime_data)
        # set its Pixmap
        drag.setPixmap(pixmap)
        # shift the Pixmap so that it coincides with the cursor position
        drag.setHotSpot(e.pos())

        # start the drag operation
        # exec_ will return the accepted action from dropEvent
        drag_result = drag.exec_(QtCore.Qt.CopyAction)


class NavigationOIDControls(QtWidgets.QWidget):

    def __init__(self, parent, navigator):
        super(NavigationOIDControls, self).__init__(parent)

        self._navigator = navigator

        self.bt_font = self.font()
        self.bt_font.setPointSize(self.bt_font.pointSize() * 1.3)

        self._flow_lo = FlowLayout()
        self.setLayout(self._flow_lo)
        self._flow_lo.setContentsMargins(2, 0, 2, 0)
        self._flow_lo.setSpacing(0)

    def update(self):
        self._flow_lo.clear()

        label_to_oid = self._navigator.split_current_oid()
        for label, goto_oid in label_to_oid:
            tb = NavigationButton(label, goto_oid, self)
            tb.adjustSize()
            self._flow_lo.addWidget(tb)

    def _goto_home(self):
        self._navigator.goto_root()

    def _goto(self, oid):
        in_new_view = (
            QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier
        )
        self._navigator.goto(oid, in_new_view)

    def current_oid(self):
        return self._navigator.current_oid()


class NavigationHistoryControls(QtWidgets.QWidget):

    def __init__(self, parent, navigator):
        super(NavigationHistoryControls, self).__init__(parent)

        self._navigator = navigator

        self.prev_bt = QtWidgets.QToolButton(self)
        self.prev_bt.setProperty('no_border', True)
        self.prev_bt.setText('<')
        self.prev_bt.setIcon(resources.get_icon(
            ('icons.gui', 'chevron-sign-left'),
            disabled_ref=('icons.gui', 'chevron-sign-left-disabled')
        ))
        self.prev_bt.clicked.connect(self._on_prev_bt)

        self.up_bt = QtWidgets.QToolButton(self)
        self.up_bt.setProperty('no_border', True)
        self.up_bt.setText('/\\')
        self.up_bt.setIcon(resources.get_icon(
            ('icons.gui', 'chevron-sign-up'),
            disabled_ref=('icons.gui', 'chevron-sign-up-disabled')
        ))
        self.up_bt.clicked.connect(self._on_up_bt)

        self.next_bt = QtWidgets.QToolButton(self)
        self.next_bt.setProperty('no_border', True)
        self.next_bt.setText('>')
        self.next_bt.setIcon(resources.get_icon(
            ('icons.gui', 'chevron-sign-to-right'),
            disabled_ref=('icons.gui', 'chevron-sign-to-right-disabled')
        ))
        self.next_bt.clicked.connect(self._on_next_bt)

        self.home_bt = QtWidgets.QToolButton(self)
        self.home_bt.setProperty('no_border', True)
        self.home_bt.setText('/')
        self.home_bt.setIcon(resources.get_icon(
            ('icons.gui', 'home'),
            disabled_ref=('icons.gui', 'home-outline')
        ))
        self.home_bt.clicked.connect(self._goto_home)

        bt_lo = QtWidgets.QHBoxLayout()
        bt_lo.setContentsMargins(12, 0, 12, 0)
        bt_lo.setSpacing(0)
        bt_lo.addWidget(self.prev_bt)
        bt_lo.addWidget(self.up_bt)
        bt_lo.addWidget(self.next_bt)
        bt_lo.addWidget(self.home_bt)

        self.setLayout(bt_lo)

    def _goto_home(self):
        self._navigator.goto_root()

    def _on_prev_bt(self):
        # TODO: handle optional new view
        self._navigator.goto_prev()

    def _on_up_bt(self):
        # TODO: handle optional new view
        self._navigator.goto_parent()

    def _on_next_bt(self):
        # TODO: handle optional new view
        self._navigator.goto_next()

    def update(self):
        self.prev_bt.setEnabled(self._navigator.has_prev())
        self.up_bt.setEnabled(self._navigator.has_parent())
        self.next_bt.setEnabled(self._navigator.has_next())
        self.home_bt.setEnabled(self._navigator.current_oid is not None and self._navigator.current_oid() != '/Home')


class NavigationBar(QtWidgets.QWidget):

    def __init__(self, parent, navigator):
        super(NavigationBar, self).__init__(parent)
        layout = QtWidgets.QHBoxLayout(self)
        self.nav_ctrl = NavigationHistoryControls(self, navigator)
        self.nav_oid = NavigationOIDControls(self, navigator)
        layout.addWidget(self.nav_ctrl, 10, alignment=QtCore.Qt.AlignVCenter)
        layout.addWidget(self.nav_oid, 90, alignment=QtCore.Qt.AlignVCenter)
        self.setLayout(layout)
