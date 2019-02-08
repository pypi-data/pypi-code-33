#!/usr/bin/python3
import hashlib
import json
import os
import time
from collections import OrderedDict
from PyQt5 import QtWidgets, QtCore, QtGui

try:
    import qoob.backend.parser as parser
    import qoob.backend.tools as tools
    import qoob.frontend.playlist as playlist
except ImportError:
    import backend.parser as parser
    import backend.tools as tools
    import frontend.playlist as playlist


class LibraryTree(QtWidgets.QTreeWidget):
    selectEvent = QtCore.pyqtSignal(object)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.preferences = parent.preferences
        self.setAlternatingRowColors(True)
        self.header().setVisible(False)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setIndentation(10)
        self.itemSelectionChanged.connect(self._selectItem)

    def _selectItem(self):
        if self.selectedItems():
            self.selectEvent.emit(self.selectedItems())

    def addAlbum(self, node, path):
        name = os.path.splitext(os.path.basename(path))[0]
        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, name)
        item.setText(1, path)
        try:
            node.addChild(item)
        except RuntimeError:
            pass

    def addAllMusic(self):
        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, "All Music")
        item.setText(1, "__all__")
        self.insertTopLevelItem(0, item)

    def addArtist(self, node):
        self.addTopLevelItem(node)
        self.sortItems(0, QtCore.Qt.AscendingOrder)

    @QtCore.pyqtSlot()
    def expand(self):
        if self.preferences.get("viewer", "expand library"):
            count = self.topLevelItemCount()
            for item in range(self.topLevelItemCount()):
                count += self.topLevelItem(item).childCount()
            if (count * 12) <= self.height():  # Where 12px is the height of one item
                self.expandAll()
        if not self.parent.ui.libraryFilterLine.text():
            self.addAllMusic()


class LibraryWorker(QtCore.QObject):
    setStatusMessage = QtCore.pyqtSignal(str)
    addArtist = QtCore.pyqtSignal(object)
    state = QtCore.pyqtSignal(bool)
    expand = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.preferences = parent.preferences
        self.libraryView = parent.libraryView
        self.log = parent.logger.new("Library")
        self.cacheTree = tools.Database("cache_tree")
        self.cacheView = tools.Database("cache_view")
        self.selection = []
        self.siftAborted = False
        self.sift = ""

    def _buildTree(self, paths):
        tree = {}
        musicDb = self.preferences.get("general", "music database")
        for p in paths:
            if self._siftChanged():
                self.siftAborted = True
                break
            albumPath = os.path.abspath(os.path.join(p, os.pardir))
            if albumPath not in musicDb:
                artistPath = os.path.abspath(os.path.join(albumPath, os.pardir))
                if artistPath in musicDb:
                    artistPath = albumPath

                artist, album = self._tagFromPath(p)
                if artist not in tree:
                    tree[artist] = {"path": artistPath, "albums": {}}
                tree[artist]["albums"][album] = albumPath
        return tree

    def _cacheViewSave(self, available):
        self.cacheView.db[available] = []
        for item in range(self.libraryView.topLevelItemCount()):
            item = self.libraryView.topLevelItem(item)
            self.cacheView.db[available].append(item.text(5))
        self.cacheView.save()
        self.log.info(f"View cache saved for 'All Music'")

    def _cacheTreeRestore(self):
        self.setStatusMessage.emit("Loading library tree cache ...")
        for artist in self.cacheTree.db:
            if self._siftChanged(): break
            if self._isPathValid(artist):
                node = self._item(artist)
                for album in self.cacheTree.db[artist]:
                    if self._siftChanged(): break
                    if self._isPathValid(album):
                        album = self._item(album)
                        node.addChild(album)
                self.addArtist.emit(node)
        self.state.emit(False)

    def _fetchAllMusic(self):
        self.setStatusMessage.emit("Loading of 'All Music' view cache ...")
        paths = self.preferences.get("general", "music database")

        available = ""
        for p in paths:
            if os.path.isdir(p):
                available += f"%{p}%"

        if not self.parent.ui.libraryFilterLine.text():
            started = time.time()
            if available in self.cacheView.db:
                tags = self._fetchTag(self.cacheView.db[available])
                self._fillLibraryView(tags)
                elapsed = int((time.time() - started)*1000)
                self.log.info(f"View loaded from cache after {elapsed}ms, {len(tags)} items")
                self.setStatusMessage.emit(f"View loaded from cache after {elapsed}ms, {len(tags)} items")
            else:
                self._fetchView(paths)
                self._cacheViewSave(available)
        else:
            self._fetchView(paths)

    def _fetchTag(self, files):
        tags = {}
        for path in files:
            if self._siftChanged(): break
            if self._selectionChanged(): break
            if parser.allowedType(path):
                tags[path] = self.parent.parser.header(path)
        return tags

    def _fetchTree(self):
        if self.cacheTree.db:
            started = time.time()
            self._cacheTreeRestore()
            elapsed = int((time.time() - started)*1000)
            self.log.info(f"Library tree loaded from cache after {elapsed}ms")
            self.setStatusMessage.emit(f"Library tree loaded from cache after {elapsed}ms")
        else:
            QtCore.QMetaObject.invokeMethod(self.parent.parser, "scanAll", QtCore.Qt.QueuedConnection)

    def _fetchView(self, paths):
        tags = {}
        for p in paths:
            started = time.time()
            tags.update(self._selectionScan(p))
        tags = self._sortRoutine(tags)
        self._fillLibraryView(tags)
        elapsed = int((time.time() - started)*1000)
        itemsCount = self.libraryView.topLevelItemCount()
        self.log.info(f"View loaded after {elapsed}ms, {itemsCount} items")
        self.setStatusMessage.emit(f"View loaded after {elapsed}ms, {itemsCount} items")

    def _fillLibraryTree(self, tree):
        for artist in sorted(tree, key=str.lower):
            if self._siftChanged():
                self.siftAborted = True
                break
            artistPath = tree[artist]["path"]
            item = QtWidgets.QTreeWidgetItem()
            for album in sorted(tree[artist]["albums"], key=str.lower):
                albumPath = tree[artist]["albums"][album]
                if not albumPath == artistPath:
                    subItem = QtWidgets.QTreeWidgetItem()
                    subItem.setText(0, album)
                    subItem.setText(1, albumPath)
                    item.addChild(subItem)
            item.setText(0, artist)
            item.setText(1, artistPath)
            self.addArtist.emit(item)

    def _fillLibraryView(self, metadata):
        for path in metadata:
            if self._siftChanged(): break
            if self._selectionChanged(): break
            item = playlist.TreeItem()
            item.setText(0, metadata[path]["artist"])
            item.setText(1, metadata[path]["album"])
            item.setText(2, metadata[path]["track"])
            item.setText(3, metadata[path]["title"])
            item.setText(4, metadata[path]["duration"])
            item.setText(5, path)
            self.libraryView.addTopLevelItem(item)  ## QBasicTimer error?

    def _item(self, path):
        name = os.path.basename(path)
        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, name)
        item.setText(1, path)
        return item

    def _isPathValid(self, path):
        for p in self.preferences.get("general", "music database"):
            if os.path.isdir(p) and path.startswith(f"{p}/"):
                return True
        return False

    def _selectionChanged(self):
        selection = self.parent.library.selectedItems()
        if selection:
            return not self.selection == selection
        return False

    def _selectionScan(self, path):
        sifted = set()
        for root, subfolder, files in os.walk(path):
            if self._siftChanged(): break
            if self._selectionChanged(): break
            for f in files:
                p = os.path.join(root, f)
                if self._siftView(f, p):
                    sifted.add(p)
        if os.path.isfile(path):
            if self._siftView(path):
                sifted.add(path)
        return self._fetchTag(sifted)

    def _siftChanged(self):
        return not self.sift == self.parent.ui.libraryFilterLine.text()

    def _siftTree(self, metadata, sift):
        result = set()
        for f in metadata:
            if self._siftChanged():
                self.siftAborted = True
                break

            if self._isPathValid(f):
                value = metadata[f]["title"].lower()
                if value.count(sift):
                    result.add(f)
        return result

    def _siftView(self, filename, path):
        metadata = self.parent.parser.metadata.db
        if path in metadata:
            tag = metadata[path]["title"]
            if tag.lower().count(self.sift.lower()):
                return True
        return False

    def _sortRoutine(self, metadata):
        direction = {"(ascending)": False, "(descending)": True}
        for action in self.preferences.get("viewer", "sorting routine"):
            if self._siftChanged(): return {}
            if self._selectionChanged(): return {}
            action = action.lower().split()
            try:
                column = action[0]
                reverse = direction[action[1]]
                metadata = self._sortMetadata(metadata, column, reverse=reverse)
            except KeyError:
                pass  # Legacy fix for "Disable sorting" key
        return metadata

    def _sortMetadata(self, db, column, reverse):
        if column == "track" or column == "duration":
            return OrderedDict(sorted(db.items(), key=lambda item:(self._toInt(item[1][column])), reverse=reverse))
        else:
            return OrderedDict(sorted(db.items(), key=lambda item:(item[1][column]), reverse=reverse))

    def _tagFromPath(self, path):
        for p in self.preferences.get("general", "music database"):
            if path.startswith(f"{p}/"):
                path = path[len(p)+1:]
        path = path.split("/")
        artist = path[0]
        album = path[1] if len(path) > 1 else None
        return (artist, album)

    def _toInt(self, string):
        try:
            if string.count(":"):
                string = string.split(":")
                return int(string[0])*3600 + int(string[1])*60 + int(string[2])
            else:
                return int(string)
        except ValueError:
            return 0

    @QtCore.pyqtSlot()
    def clearViewCache(self):
        self.cacheView.db = {}
        self.cacheView.save()
        self.log.info("Cleared view cache")

    @QtCore.pyqtSlot(str)
    def filterEvent(self, sift):
        started = time.time()
        QtCore.QMetaObject.invokeMethod(self.libraryView, "clear", QtCore.Qt.BlockingQueuedConnection)
        QtCore.QMetaObject.invokeMethod(self.parent.library, "clear", QtCore.Qt.BlockingQueuedConnection)
        self.sift = sift
        self.siftAborted = False

        if sift:
            # Search pattern in titles / filenames
            self.setStatusMessage.emit(f"Searching for '{sift}' ...")
            metadata = self.parent.parser.metadata.db
            sifted = self._siftTree(metadata, sift)
            tree = self._buildTree(sifted)
            tags = {}
            for artist in tree:
                if self._siftChanged():
                    self.siftAborted = True
                    break
                path = tree[artist]["path"]
                tags.update(self._selectionScan(path))
            tags = self._sortRoutine(tags)
            self._fillLibraryView(tags)
            self._fillLibraryTree(tree)

            self.expand.emit()
            elapsed = int((time.time() - started)*1000)
            if not self.siftAborted:
                self.log.info(f"Search of '{sift}' done after {elapsed}ms, {len(tags)} results")
                self.setStatusMessage.emit(f"Search of '{sift}' done after {elapsed}ms, {len(tags)} results")
        else:
            self._cacheTreeRestore()
            self._fetchAllMusic()

    @QtCore.pyqtSlot(str)
    def removeViewCache(self, folder):
        for path in dict(self.cacheView.db):
            if path.startswith(folder + "/"):
                del self.cacheView.db[path]
        self.cacheView.save()

    @QtCore.pyqtSlot()
    def saveTreeCache(self):
        self.cacheTree.db = {}
        for artist in range(self.parent.library.topLevelItemCount()):
            artist = self.parent.library.topLevelItem(artist)
            self.cacheTree.db[artist.text(1)] = []
            for album in range(artist.childCount()):
                album = artist.child(album)
                self.cacheTree.db[artist.text(1)].append(album.text(1))
        self.cacheTree.save()

    @QtCore.pyqtSlot(object)
    def selectEvent(self, selection):
        self.selection = selection
        QtCore.QMetaObject.invokeMethod(self.libraryView, "clear", QtCore.Qt.BlockingQueuedConnection)
        try:
            for item in selection:
                if item.text(1) == "__all__":
                    self._fetchAllMusic()
                    break
            else:
                paths = [i.text(1) for i in selection]
                self._fetchView(paths)
        except RuntimeError:
            pass

