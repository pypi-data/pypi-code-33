
import six

from qtpy import QtWidgets, QtGui, QtCore


QWidgetType = type(QtWidgets.QWidget)


class ViewType(QWidgetType):

    def __new__(cls, class_name, bases, class_dict):
        class_dict['_VIEWS'] = []
        return super(ViewType, cls).__new__(cls, class_name, bases, class_dict)


# six.with_metaclass does not play well with PySide's shiboken.
if six.PY2:
    class _BaseView(QtWidgets.QWidget):
        __metaclass__ = ViewType

else:
    class _BaseView(six.with_metaclass(ViewType, QtWidgets.QWidget)):
        pass


class View(_BaseView):

    _VIEWS = []  # will be reset to [] for all view types by the metaclass

    @classmethod
    def view_type_name(cls):
        return cls.__name__

    def __init__(self, session, main_window_manager, parent):
        super(View, self).__init__(parent)

        self.__class__._VIEWS.append(self)

        self.session = session
        self._main_window_manager = main_window_manager

        self._view_title = self.view_type_name()
        self._on_view_title_change = None

        # Menu
        self.menubar = QtWidgets.QMenuBar(self)
        self.view_menu = self.menubar.addMenu(self.view_title())

        # Tools
        self._header_tools = {}
        self._header_tools_layout = QtWidgets.QHBoxLayout()

        content_widget = QtWidgets.QWidget(self)

        lo = QtWidgets.QVBoxLayout()
        lo.setContentsMargins(0, 0, 0, 0)
        lo.setSpacing(0)
        self.setLayout(lo)

        hlo = QtWidgets.QHBoxLayout()
        hlo.setContentsMargins(0, 0, 0, 0)
        hlo.addWidget(self.menubar)
        header_widgets_layout = QtWidgets.QHBoxLayout()
        hlo.addStretch()
        hlo.addLayout(header_widgets_layout, 100)
        hlo.addLayout(self._header_tools_layout)
        lo.addLayout(hlo)
        top_layout = QtWidgets.QHBoxLayout()
        lo.addLayout(top_layout)
        lo.addWidget(content_widget, 100)
        self._build(
            self, top_layout, content_widget,
            self, header_widgets_layout
        )

        self._update_menus()

    def _create_scrolled_area(self, parent):
        scroll_area = QtWidgets.QScrollArea(parent)
        scroll_area.setWidgetResizable(True)

        content_widget = QtWidgets.QWidget(parent)
        scroll_area.setWidget(content_widget)

        return scroll_area, content_widget

    def _build(
            self,
            top_parent, top_layout,
            main_parent,
            header_parent, header_layout
    ):
        '''
        Subclasses must override this to build their widgets.
        '''
        pass

    def duplicate_view(self, *extra_args, **extra_kwargs):
        dock = self.dock_widget()

        area = dock.dock_area()
        area = {
            QtCore.Qt.LeftDockWidgetArea: QtCore.Qt.RightDockWidgetArea,
            QtCore.Qt.RightDockWidgetArea: QtCore.Qt.BottomDockWidgetArea,
            QtCore.Qt.BottomDockWidgetArea: QtCore.Qt.LeftDockWidgetArea,
            QtCore.Qt.TopDockWidgetArea: QtCore.Qt.LeftDockWidgetArea,
        }[area]

        return self._main_window_manager.add_view(
            self.view_type_name(),
            area=area,
            *extra_args, **extra_kwargs
        )

    def set_on_view_title_change(self, f):
        self._on_view_title_change = f

    def set_view_title(self, title):
        self._view_title = title
        if self._on_view_title_change is not None:
            self._on_view_title_change()

    def view_title(self):
        return self._view_title

    def add_header_tool(self, tool_id, label, tooltip, f):
        def pyside_and_pyqt_handler(checked=None, f=f):
            f()
        b = QtWidgets.QToolButton(self)
        b.setProperty('no_border', True)
        self._header_tools[tool_id] = b
        b.setText(label)
        b.clicked.connect(pyside_and_pyqt_handler)
        b.setToolTip(tooltip)
        self._header_tools_layout.addWidget(b)
        return b

    def remove_header_tool(self, tool_id):
        self._header_tools[tool_id].deleteLater()

    def _update_menus(self):
        pass

    def dock_widget(self):
        return self.parentWidget()

    def delete_on_close(self):
        '''
        If returns True, the view will be deleted when its dock is closed.

        Default is to return True unless this is the last instance of this view type.
        '''
        try:
            self.__class__._VIEWS[1]
        except IndexError:
            return False
        return True

    def about_to_delete(self):
        '''
        Called if delete_on_close() returned True and the view is about to be deleted.
        Subclasses may override this to do some cleanup or cancel some pending commands but
        MUST call the base implementation
        '''
        self.__class__._VIEWS.remove(self)

    def on_hide(self):
        '''
        Called when the view's dock is hidden.
        Beware that consecutive hide/show happens when floating a view...
        '''
        pass

    def on_show(self):
        '''
        Called when the view's dock is shown.
        Beware that consecutive hide/show happens when floating a view...
        '''
        pass

    def receive_event(self, event, data):
        raise NotImplementedError()
