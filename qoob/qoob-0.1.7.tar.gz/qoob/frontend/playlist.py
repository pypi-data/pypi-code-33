#!/usr/bin/python3
import os
from PyQt5 import QtGui, QtWidgets, QtCore

try:
    import qoob.backend.tools as tools
    import qoob.backend.parser as parser
except ImportError:
    import backend.tools as tools
    import backend.parser as parser

LOCAL_DIR = os.path.dirname(os.path.realpath(__file__)) + "/"
DB_DIR = os.path.expanduser("~/.config/qoob/")
DEFAULT = \
{
    "sort enabled": False,
    "sort order": QtCore.Qt.AscendingOrder,
    "sort column": 0,
    "column width": {0: 200, 1:200, 2:80, 4:80},
    "current": "",
    "files": []
}


class Menu(QtWidgets.QMenu):
    action = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.preferences = parent.preferences
        self.icon = parent.icon
        self.aboutToShow.connect(self._refresh)

    def _refresh(self):
        self.clear()
        if self.parent.copied:
            self.addAction(self.icon["paste"], "Paste selection", lambda: self.action.emit("paste"))

        if self.parent.tabWidget.current.selectedItems():
            self.addAction(self.icon["cut"], "Cut selection", lambda: self.action.emit("cut"))
            self.addAction(self.icon["copy"], "Copy selection", lambda: self.action.emit("copy"))
            if self.preferences.get("general", "file manager"):
                self.addAction(self.icon["folder"], "Browse song folder", lambda: self.action.emit("browse"))
            self.addSeparator()
            self.addAction(self.icon["remove"], "Delete from playlist", lambda: self.action.emit("delete from playlist"))
            self.addAction(self.icon["delete"], "Delete from disk", lambda: self.action.emit("delete prompt"))


class SortBox(QtWidgets.QCheckBox):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setText("Enable sorting")
        self.clicked.connect(self._toggle)
        if parent.preferences.get("viewer", "sort by default"):
            self.setChecked(True)

    def _toggle(self):
        self.parent.tabWidget.current.setSortingEnabled(self.isChecked())


class Tabs(QtWidgets.QTabWidget):
    keyEvent = QtCore.pyqtSignal(object, int)
    clearTabPlaylist = QtCore.pyqtSignal(str)
    changed = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.preferences = parent.preferences

        self.setDocumentMode(True)
        self.setTabsClosable(True)
        self.setMovable(True)

        self.tab1 = QtWidgets.QWidget()
        self.tab2 = QtWidgets.QWidget()
        self.addTab(self.tab1, "Library viewer")
        self.addTab(self.tab2, "")

        self.setTabEnabled(1, False)
        self.dummyButton = QtWidgets.QPushButton()
        self.dummyButton.setFixedSize(0, 0)
        self.newButton = QtWidgets.QPushButton()
        self.newButton.setFlat(True)
        self.newButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.newButton.setFixedSize(30, 20)
        self.newButton.clicked.connect(self._add)
        self.newButton.setToolTip("New playlist")
        self.tabBar().setTabButton(0, QtWidgets.QTabBar.RightSide, self.dummyButton)
        self.tabBar().setTabButton(1, QtWidgets.QTabBar.RightSide, self.newButton)

        self.tabCloseRequested.connect(self._close)
        self.currentChanged.connect(self._changed)
        self.installEventFilter(self)
        self.tabBar().installEventFilter(self)

        self.tabs = {}
        self.tabs["Library viewer"] = {"playlist": Tree(parent), "sort": SortBox(parent)}
        self.current = self.tabs["Library viewer"]["playlist"]
        self.initStyle()

        self.viewLayout = QtWidgets.QGridLayout()
        self.viewLayout.addWidget(self.tabs["Library viewer"]["playlist"])
        self.viewLayout.addWidget(self.tabs["Library viewer"]["sort"])
        self.currentWidget().setLayout(self.viewLayout)

        self.playlist = tools.Database("playlist")
        self._playlistsInit()
        self._playlistsLoadAttributes()
        self._playlistsLoadContent()

    def eventFilter(self, obj, event):
        if obj == self.tabBar() and event.type() == QtCore.QEvent.MouseButtonDblClick:
            self._rename()
        elif obj == self and event.type() == QtCore.QEvent.ShortcutOverride:
            self.keyEvent.emit(event.modifiers(), event.key())
        return QtCore.QObject.event(obj, event)

    def _add(self, name=None):
        layout = QtWidgets.QVBoxLayout()
        tab = QtWidgets.QWidget(self)
        count = self.tabBar().count()
        index = 1
        if not name:
            name = "Playlist " + str(index)
        while name in self.tabs:
            index += 1
            name = "Playlist " + str(index)

        self.tabs[name] = {}
        self.tabs[name] = {"playlist": Tree(self.parent), "sort": SortBox(self.parent)}
        self.tabs[name]["playlist"].setSortingEnabled(self.tabs[name]["sort"].isChecked())
        header = self.tabs["Library viewer"]["playlist"].header()
        for column in (0, 1, 2, 4):
            self.tabs[name]["playlist"].setColumnWidth(column, header.sectionSize(column))

        self.addTab(tab, name)
        self.setCurrentWidget(tab)
        self.tabBar().moveTab(count - 1, count)
        self.currentWidget().setLayout(layout)
        layout.addWidget(self.tabs[name]["playlist"])
        layout.addWidget(self.tabs[name]["sort"])

    def _changed(self, index):
        tabName = self.tabText(index)
        tabName = tabName.lstrip("&")  # KDE bug fix (auto append of &)
        if tabName:
            self.current = self.tabs[tabName]["playlist"]
            self.changed.emit()

    def _close(self, tab):
        tabName = self.tabText(tab)
        tabName = tabName.lstrip("&")  # KDE bug fix (auto append of &)
        del self.tabs[tabName]
        if tabName in self.playlist.db:
            del self.playlist.db[tabName]
            self.playlist.save()
        self.removeTab(tab)
        self.clearTabPlaylist.emit(tabName)

        # Prevent landing on the '+' tab
        count = self.tabBar().count() - 1
        if count == self.tabBar().currentIndex():
            self.tabBar().setCurrentIndex(count - 1)

    def _playlistDumpAttributes(self, tabName):
        self.playlist.db[tabName]["sort enabled"] = self.tabs[tabName]["sort"].isChecked()
        self.playlist.db[tabName]["sort order"] = self.tabs[tabName]["playlist"].header().sortIndicatorOrder()
        self.playlist.db[tabName]["sort column"] = self.tabs[tabName]["playlist"].sortColumn()
        for column in (0, 1, 2, 4):
            width = self.tabs[tabName]["playlist"].header().sectionSize(column)
            self.playlist.db[tabName]["column width"][column] = width

    def _playlistDumpFiles(self, tabName):
        if self.tabs[tabName]["playlist"].currentItem():
            self.playlist.db[tabName]["current"] = self.tabs[tabName]["playlist"].currentItem().text(5)

        for item in range(self.tabs[tabName]["playlist"].topLevelItemCount()):
            item = self.tabs[tabName]["playlist"].topLevelItem(item)
            self.playlist.db[tabName]["files"].append(item.text(5))

    def _playlistsInit(self):
        for tabName in self.playlist.db:
            if not tabName == "Library viewer":
                self._add(tabName)

    def _playlistsLoadAttributes(self):
        for tabName in self.playlist.db:
            sortEnabled = self.playlist.db[tabName].get("sort enabled", DEFAULT["sort enabled"])
            sortOrder = self.playlist.db[tabName].get("sort order", DEFAULT["sort order"])
            sortColumn = self.playlist.db[tabName].get("sort column", DEFAULT["sort column"])
            columnWidth = self.playlist.db[tabName].get("column width", DEFAULT["column width"])
            self.tabs[tabName]["playlist"].sortByColumn(sortColumn, sortOrder)
            self.tabs[tabName]["sort"].setChecked(sortEnabled)
            self.tabs[tabName]["playlist"].setSortingEnabled(sortEnabled)
            for column in columnWidth:
                self.tabs[tabName]["playlist"].setColumnWidth(int(column), columnWidth[column])

    def _playlistsLoadContent(self):
        for tabName in self.playlist.db:
            for path in self.playlist.db[tabName]["files"]:
                item = self.tabs[tabName]["playlist"].add(path, append=True)
                if "current" in self.playlist.db[tabName] and path == self.playlist.db[tabName]["current"]:
                    self.tabs[tabName]["playlist"].setCurrentItem(item)
        self.tabBar().setCurrentIndex(self.preferences.get("state", "tab"))

    def _rename(self):
        tabIndex = self.tabBar().currentIndex()
        oldName = self.tabText(tabIndex)
        oldName = oldName.lstrip("&")  # KDE bug fix (auto append of &)
        if not oldName == "Library viewer":
            newName = self._renamePrompt(oldName)
            if newName and newName not in self.tabs:
                self.tabs[newName] = self.tabs.pop(oldName)
                if oldName in self.playlist.db:
                    self.playlist.db[newName] = self.playlist.db.pop(oldName)
                    self.playlist.save()
                self.setTabText(tabIndex, newName)

    def _renamePrompt(self, oldName):
        msg = QtWidgets.QInputDialog()
        msg.setInputMode(QtWidgets.QInputDialog.TextInput)
        msg.setWindowFlags(msg.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        msg.setWindowTitle(f"Rename '{oldName}'")
        msg.setLabelText("Enter the new name:")
        msg.setTextValue(oldName)
        msg.setFixedSize(250, 100)
        accept = msg.exec_()
        newName = msg.textValue()
        newName = newName.replace("&", "")  # KDE bug fix
        if accept and newName:
            return newName

    def initStyle(self):
        iconTheme = self.preferences.get("general", "icon theme")
        iconPath = f"{LOCAL_DIR}../icons/{iconTheme}/"
        stylesheet = f"QTabBar::close-button {{ image: url({iconPath}tab_close.svg); }}\n"
        stylesheet += f"QTabBar::close-button:hover {{ image: url({iconPath}tab_hover.svg); }}\n"
        self.setStyleSheet(stylesheet)
        self.newButton.setIcon(self.parent.icon["tab_add"])

    def playlistSave(self):
        for index in range(self.count() - 1):
            tabName = self.tabText(index)
            tabName = tabName.lstrip("&")  # KDE bug fix (auto append of &)
            self.playlist.db[tabName] = tools.copyDict(DEFAULT)
            self._playlistDumpAttributes(tabName)
            self._playlistDumpFiles(tabName)
        self.playlist.save()


class Tree(QtWidgets.QTreeWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.preferences = parent.preferences
        self.metadata = parent.parser.metadata
        self.setHeaderLabels(["Artist", "Album", "Track", "Title", "Duration"])
        self.header().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.header().setStretchLastSection(False)
        self.setAlternatingRowColors(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(parent.menuShow)
        self.itemActivated.connect(parent.player.activateSelection)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.acceptProposedAction()
        QtWidgets.QTreeWidget.dragEnterEvent(self, event)

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toString()[len("file://"):]
            if os.path.isfile(path):
                self.add(path)
            elif os.path.isdir(path):
                for root, subfolder, files in os.walk(path):
                    for f in files:
                        self.add(f"{root}/{f}")
        QtWidgets.QTreeWidget.dropEvent(self, event)

    def keyPressEvent(self, event):
        # Block default behavior (lateral tree scrolling)
        if not event.key() == QtCore.Qt.Key_Left and not event.key() == QtCore.Qt.Key_Right:
            QtWidgets.QTreeWidget.keyPressEvent(self, event)

    def add(self, path, append=False):
        basename = os.path.basename(path)
        extension = os.path.splitext(basename)[1].lower()
        if extension in parser.ALLOWED_AUDIO_TYPES:
            tags = self.parent.parser.header(path)
            item = TreeItem()
            item.setText(0, tags["artist"])
            item.setText(1, tags["album"])
            item.setText(2, tags["track"])
            item.setText(3, tags["title"])
            item.setText(4, tags["duration"])
            item.setText(5, path)

            if append:
                self.addTopLevelItem(item)
            else:
                index = self.currentIndex().row()
                if index == -1: index = 0
                self.insertTopLevelItem(index, item)
            return item
        return None


class TreeItem(QtWidgets.QTreeWidgetItem):
    def __init__(self):
        super().__init__()
        self.setFlags(self.flags() &~ QtCore.Qt.ItemIsDropEnabled)
        self.lastColor = "none"

    def __lt__(self, other):
        column = self.treeWidget().sortColumn()
        key1 = self.text(column)
        key2 = other.text(column)
        try:
            return int(key1) < int(key2)
        except ValueError:
            return key1.lower() < key2.lower()

    def setColor(self, color):
        priority = {"none": 0, "green": 0, "yellow": 1, "red": 2}
        if priority[color] >= priority[self.lastColor]:
            self.lastColor = color
            try:
                for column in range(5):
                    if color == "none":
                        self.setData(column, QtCore.Qt.BackgroundRole, None)
                        self.setData(column, QtCore.Qt.ForegroundRole, None)
                    elif color == "green":
                        self.setForeground(column, QtGui.QColor("#004000"))
                        self.setBackground(column, QtGui.QColor("#c6efce"))
                    elif color == "yellow":
                        self.setForeground(column, QtGui.QColor("#553400"))
                        self.setBackground(column, QtGui.QColor("#ffeb9c"))
                    elif color == "red":
                        self.setForeground(column, QtGui.QColor("#9c0006"))
                        self.setBackground(column, QtGui.QColor("#ffc7ce"))
            except RuntimeError:
                pass


