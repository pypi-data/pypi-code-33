
import os
import six
import getpass

from qtpy import QtWidgets, QtCore, QtGui

from .widget_view import ToolBarView
from kabaret.app import resources


LAYOUTS = {}

class ClickLabel(QtWidgets.QLabel):

    def __init__(self, on_click, *args, **kwargs):
        super(ClickLabel, self).__init__(*args, **kwargs)
        self._on_click = on_click

    def mousePressEvent(self, event):
        self._on_click()

class SessionToolBar(ToolBarView):

    def __init__(self, *args, **kwargs):
        super(SessionToolBar, self).__init__(*args, **kwargs)

        self.user_label = QtWidgets.QLabel(self)
        self.session_id_label = QtWidgets.QLabel(self)

        stretch = QtWidgets.QWidget(self)
        stretch.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Preferred,
        )

        self.layouts_tb = QtWidgets.QToolButton(self)
        self.layouts_tb.setText('Layouts')
        self.layouts_tb.setPopupMode(self.layouts_tb.InstantPopup)
        self.layouts_tb.setIcon(resources.get_icon(('icons.gui','ui-layout')))
        self.layouts_tb.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.layout_menu = QtWidgets.QMenu(self.layouts_tb)
        self.layout_menu.addAction('TEST')
        self.layouts_tb.setMenu(self.layout_menu)

        self.addWidget(self.user_label)
        self.addSeparator()
        self.addWidget(self.session_id_label)
        self.addSeparator()
        self.addWidget(stretch)
        self.addSeparator()
        self.addWidget(self.layouts_tb)

        self.update_user_label()
        self.update_layout_tb()

    def update_user_label(self):
        label = ' <b><font size=+5>{}</font></b> '.format(
            getpass.getuser(),
        )
        self.user_label.setText(label)

        label=' {}[{}] '.format(
            self.session.session_name(),
            self.session.cmds.Cluster.get_cluster_name(),
        )
        self.session_id_label.setText(label)
        
        self.session_id_label.setToolTip(
            '<b>Session ID:</b> {}<br><b>Connection:</b> {}'.format(
                self.session.session_uid(),
                ' - '.join(self.session.cmds.Cluster.get_connection_info())
            )
        )

    def get_layout_presets(self):
        # Tmp until we have a User actor to store those things
        global LAYOUTS
        return LAYOUTS

    def store_layout_preset(self, name, layout_preset):
        # Tmp until we have a User actor to store those things
        global LAYOUTS
        LAYOUTS[name] = layout_preset

    def update_layout_tb(self):
        tb = self.layouts_tb
        menu = tb.menu()
        menu.clear()

        layout_icon = resources.get_icon(('icons.gui', 'ui-layout'))
        for name, layout in sorted(six.iteritems(self.get_layout_presets())):
            action = QtWidgets.QAction(layout_icon, name, menu)
            action.triggered.connect(lambda l=layout: self._on_set_layout_action(l))
            action.setObjectName('la')
            menu.addAction(action)

        sep = QtWidgets.QAction(menu)
        sep.setSeparator(True)
        sep.setObjectName('sep')
        menu.addAction(sep)
        #
        icon = resources.get_icon(('icons.gui', 'plus-symbol-in-a-rounded-black-square'))
        action = QtWidgets.QAction(icon, 'Store Current Layout', menu)
        action.triggered.connect(self._on_store_current_layout_action)
        action.setObjectName('sa')
        menu.addAction(action)

    def _on_set_layout_action(self, layout):
        # Don't delete us inside an signal handler from us:
        QtCore.QTimer.singleShot(
            100, lambda l=layout, s=self.session:s.set_views_state(l)
        )

    def _on_store_current_layout_action(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle('Save Layout')
        dialog.setLayout(QtWidgets.QVBoxLayout())
        cb = QtWidgets.QComboBox(dialog)
        cb.addItems(['']+self.get_layout_presets().keys())
        cb.setEditable(True)
        dialog.layout().addWidget(cb)
        b = QtWidgets.QPushButton(dialog)
        b.setText('Save Layout')
        b.clicked.connect(dialog.accept)
        dialog.layout().addWidget(b)

        cancel = dialog.exec_() != dialog.Accepted
        name = cb.currentText().strip()
        dialog.deleteLater()
        if cancel or not name:
            return

        self.store_layout_preset(
            name,
            self.session.get_views_state()
        )
        self.update_layout_tb()

    def receive_event(self, event_type, data):
        pass
