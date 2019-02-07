# -*- coding: utf-8 -*-
"""Graphics view module.

contains PSGraphicsView, a subclass of QGraphicsView
"""

from puzzlestream.ui.module import PSModule
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import *

translate = QCoreApplication.translate


class PSGraphicsView(QtWidgets.QGraphicsView):

    def __init__(self, manager, *args):
        super().__init__(*args)
        self.setTransformationAnchor(
            QtWidgets.QGraphicsView.AnchorUnderMouse
        )

        self.__minZoom, self.__maxZoom = 0.25, 1.5

        self.slider = QtWidgets.QSlider(self)
        self.slider.setRange(int(10 * self.__minZoom),
                             int(10 * self.__maxZoom))
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setValue(10)
        self.slider.setSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                  QtWidgets.QSizePolicy.Fixed)
        self.slider.valueChanged.connect(self.__sliderValueChanged)
        self.addScrollBarWidget(self.slider, Qt.AlignRight)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setDragMode(self.RubberBandDrag)

        self.__shortcuts = {}
        self.addShortcut("Del", self.__deleteSelection)
        self.__config = None
        self.__manager = manager

    def setConfig(self, config):
        self.__config = config
        self.slider.setValue(config["puzzleZoom"])
        self.__config.edited.connect(self.__configChanged)
        self.__configChanged("slowerRedraw")

    def __configChanged(self, key):
        if key == "slowerRedraw":
            if self.__config["slowerRedraw"]:
                self.setViewportUpdateMode(
                    QtWidgets.QGraphicsView.BoundingRectViewportUpdate)
            else:
                self.setViewportUpdateMode(
                    QtWidgets.QGraphicsView.MinimalViewportUpdate)

    def __saveZoom(self):
        if self.__config is not None:
            self.__config["puzzleZoom"] = self.slider.value()

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            if (event.angleDelta().y() < 0 and
                    self.transform().m11() > self.__minZoom):
                self.scale(0.9, 0.9)

            elif (event.angleDelta().y() > 0 and
                    self.transform().m11() < self.__maxZoom):
                self.scale(1.1, 1.1)

            self.slider.setValue(int(self.transform().m11() * 10))
            self.__saveZoom()
        else:
            super().wheelEvent(event)

    def resizeEvent(self, event):
        locked = self.__manager.puzzleLocked
        if not locked:
            self.__manager.setAllItemsFixed()
        super().resizeEvent(event)
        if not locked:
            self.__manager.setAllItemsMovable()

    def __sliderValueChanged(self, event):
        scale = self.slider.value() / 10
        self.setTransform(QtGui.QTransform.fromScale(scale, scale))
        self.__saveZoom()

    def addShortcut(self, sequence, target):
        sc = QtWidgets.QShortcut(QtGui.QKeySequence(sequence), self)
        sc.activated.connect(target)
        self.__shortcuts[sequence] = sc

    def __deleteSelection(self):
        items = self.scene().selectedItemList

        if len(items) == 0:
            return

        if len(items) == 1:
            if isinstance(items[0], PSModule):
                msg = (
                    translate("GraphicsScene",
                              "Are you sure you want to delete") +
                    " " + str(items[0]) + translate("GraphicsScene", "?")
                )
                reply = QtGui.QMessageBox.question(
                    self, translate("GraphicsScene", "Item deletion"), msg,
                    QtGui.QMessageBox.Yes,
                    QtGui.QMessageBox.No
                )
                if reply == QtGui.QMessageBox.Yes:
                    self.scene().deleteItem(items[0])
            else:
                self.scene().deleteItem(items[0])
        elif any([isinstance(i, PSModule) for i in items]):
            msg = translate(
                "GraphicsScene",
                "Are you sure you want to delete the following items?"
            )

            for i in items:
                msg += "\n" + "- " + str(i)
            reply = QtGui.QMessageBox.question(self, "Item deletion", msg,
                                               QtGui.QMessageBox.Yes,
                                               QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                self.scene().deleteItems(items)
        else:
            self.scene().deleteItems(items)
