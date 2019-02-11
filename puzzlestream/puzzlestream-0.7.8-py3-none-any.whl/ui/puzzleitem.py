# -*- coding: utf-8 -*-
"""Puzzle item module.

contains PSPuzzleItem, a subclass of QGraphicsItem
"""

from math import sqrt

import numpy as np
from puzzlestream.backend.signal import PSSignal
from puzzlestream.backend.streamsection import PSStreamSection
from puzzlestream.ui import colors
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

translate = QCoreApplication.translate


class PSPuzzleItem(QGraphicsItem):

    # Defined by child classes:
    # -------------------------------------------------------------------------
    # PSModule / PSValve / PSPipe :
    _radius = 0

    def __init__(self, ID, *args):
        super().__init__(*args)

        self.__id = ID
        self.streamSection = None
        self.autopass = True
        self.__status = "incomplete"

        """ register item connections
        *disconnected
        *preconnected
        *connected
        *not available
        """
        self._freestates = ["disconnected", "preconnected"]
        self._connections = np.array(["disconnected"] * 4, dtype=str)
        self._positionIndex = {"top": 0, "left": 1, "bottom": 2, "right": 3}

        self.__statusChanged = PSSignal()
        self.__positionChanged = PSSignal()
        self.__mousePressed = PSSignal()
        self.__mouseReleased = PSSignal()
        self.__dataViewRequested = PSSignal()
        self.__plotViewRequested = PSSignal()
        self.__deletionRequested = PSSignal()
        self.__contextMenuRequested = PSSignal()

        self.__stopHere = False
        self.__oldCursorPos = None

        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

        self.__stickyDistance = 100
        self.__stickyIndicator = None

        # just for the translation files, all possible values of "status"
        translate("Status", "incomplete")
        translate("Status", "error")
        translate("Status", "running")
        translate("Status", "test failed")
        translate("Status", "paused")
        translate("Status", "waiting")
        translate("Status", "finished")

    # save and restore

    @property
    def saveProperties(self):
        props = {"id": self.id, "status": self.status,
                 "x": self.centerPos().x(), "y": self.centerPos().y(),
                 "autopass": self.autopass}
        if self.streamSection is not None:
            props["changelog"] = self.streamSection.changelog
        return props

    def restoreProperties(self, props, stream):
        self.autopass = props["autopass"]
        status = props["status"]
        self.streamSection = PSStreamSection(self.id, stream)
        if "changelog" in props:
            self.streamSection.changelog = props["changelog"]

        if (status == "finished" or
                status == "error" or
                status == "test failed"):
            self.status = status

    # draw bounding rect -> on selection
    def paint(self, painter, *args):
        if self.isSelected():
            pen = QPen()
            pen.setWidth(4)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

    @property
    def id(self):
        return self.__id

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, status):
        """Dictionary initialisation.

        Args:
            status (string): one of the following:
                incomplete, error, running, test failed, paused, waiting,
                finished
        """
        if isinstance(status, str):
            self.__status = status
            if self.autopass:
                self.statusChanged.emit(self)
        else:
            raise TypeError

    @property
    def stopHere(self):
        return self.__stopHere

    @stopHere.setter
    def stopHere(self, value):
        self.__stopHere = value

    @property
    def topFree(self):
        if (self._connections[self._positionIndex["top"]] in
                self._freestates):
            return True
        return False

    @property
    def leftFree(self):
        if (self._connections[self._positionIndex["left"]] in
                self._freestates):
            return True
        return False

    @property
    def bottomFree(self):
        if (self._connections[self._positionIndex["bottom"]] in
                self._freestates):
            return True
        return False

    @property
    def rightFree(self):
        if (self._connections[self._positionIndex["right"]] in
                self._freestates):
            return True
        return False

    # geometry information
    @property
    def radius(self):
        return self._radius

    # centerPos, setCenterPos Qt-like
    def centerPos(self):
        pass

    def setCenterPos(self):
        pass

    # -------------------------------------------------------------------------
    # Mouseevents and signals

    def contextMenuEvent(self, event):
        self.contextMenuRequested.emit(self, event)

    def mousePressEvent(self, event):
        check = (event.button() == Qt.LeftButton and
                 bool(self.flags() & QGraphicsItem.ItemIsMovable))
        if check:
            self.__oldCursorPos = event.pos()
            self.mousePressed.emit(self)
            super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.dataViewRequested.emit(self)

    def mouseMoveEvent(self, event):
        if self.__oldCursorPos is not None:
            distance = self.__distance(event.pos(), self.__oldCursorPos)
        else:
            distance = 2 * self.__stickyDistance

        if (distance > self.__stickyDistance or
                len(self.scene().connectionsToCut) == 0):
            if (QApplication.overrideCursor() != Qt.ClosedHandCursor and
                    bool(self.flags() & QGraphicsItem.ItemIsMovable)):
                QApplication.setOverrideCursor(Qt.ClosedHandCursor)
            self.positionChanged.emit(self)

            if self.__stickyIndicator is not None:
                self.__removeStickyIndicator()

            super().mouseMoveEvent(event)
        else:
            if self.__stickyIndicator is None:
                self.__showStickyIndicator(event.pos())
                if (QApplication.overrideCursor() != Qt.ClosedHandCursor and
                        bool(self.flags() & QGraphicsItem.ItemIsMovable)):
                    QApplication.setOverrideCursor(Qt.ClosedHandCursor)
            else:
                color = QColor(colors.get("standard-blue"))
                color.setAlpha(int(75 * distance / self.__stickyDistance))
                self.__stickyIndicator.setBrush(QBrush(color))

    def __showStickyIndicator(self, pos):
        self.__stickyIndicator = QGraphicsEllipseItem(
            QRectF(
                pos - QPointF(self.__stickyDistance, self.__stickyDistance),
                QSizeF(2 * self.__stickyDistance, 2 * self.__stickyDistance)
            ),
            self
        )

    def __removeStickyIndicator(self):
        self.__stickyIndicator.setParentItem(None)
        self.__stickyIndicator.hide()
        del self.__stickyIndicator
        self.__stickyIndicator = None
        self.__oldCursorPos = None

    def mouseReleaseEvent(self, event):
        QApplication.restoreOverrideCursor()
        if self.__stickyIndicator is not None:
            self.__removeStickyIndicator()
        self.mouseReleased.emit(self)
        super().mouseReleaseEvent(event)

    @property
    def inputItems(self):
        pass

    @property
    def contextMenuRequested(self):
        return self.__contextMenuRequested

    @property
    def statusChanged(self):
        return self.__statusChanged

    @property
    def mousePressed(self):
        return self.__mousePressed

    @property
    def positionChanged(self):
        return self.__positionChanged

    @property
    def mouseReleased(self):
        return self.__mouseReleased

    @property
    def dataViewRequested(self):
        return self.__dataViewRequested

    @property
    def plotViewRequested(self):
        return self.__plotViewRequested

    @property
    def deletionRequested(self):
        return self.__deletionRequested

    # -------------------------------------------------------------------------

    def runFromHere(self):
        if self.status in ("incomplete", "finished"):
            self.status = "finished"

    def inputUpdate(self, puzzleItem):
        pass

    def __distance(self, point1, point2):
        return sqrt((point1.x() - point2.x())**2 +
                    (point1.y() - point2.y())**2)

    """
    ===========================================================================
        Connection and Preconnection
    """

    @property
    def connectionPoints(self):
        x, y = self.centerPos().x(), self.centerPos().y()
        return {"top": QPointF(x, y - self.radius),
                "bottom": QPointF(x, y + self.radius),
                "left": QPointF(x - self.radius, y),
                "right": QPointF(x + self.radius, y)}

    def calculatePreconnectionDirection(self, otherItem):
        ownPoints = self.connectionPoints
        otherPoints = otherItem.connectionPoints

        dist = {("bottom", "top"): self.__distance(ownPoints["bottom"],
                                                   otherPoints["top"]),
                ("top", "bottom"): self.__distance(ownPoints["top"],
                                                   otherPoints["bottom"]),
                ("right", "left"): self.__distance(ownPoints["right"],
                                                   otherPoints["left"]),
                ("left", "right"): self.__distance(ownPoints["left"],
                                                   otherPoints["right"])}

        keys = sorted(dist, key=lambda x: dist[x])
        preConnectionDirection = None

        while preConnectionDirection is None and len(keys) > 0:
            key = keys[0]

            if (key == ("bottom", "top") and self.bottomFree and
                    otherItem.topFree):
                preConnectionDirection = key

            elif (key == ("top", "bottom") and self.topFree and
                  otherItem.bottomFree):
                preConnectionDirection = key

            elif (key == ("right", "left") and self.rightFree and
                  otherItem.leftFree):
                preConnectionDirection = key

            elif (key == ("left", "right") and self.leftFree and
                  otherItem.rightFree):
                preConnectionDirection = key

            if preConnectionDirection is None:
                del keys[0]

        return preConnectionDirection

    def preConnect(self, otherItem):
        self._preConnectionDirection = self.calculatePreconnectionDirection(
            otherItem)

        result = self._preConnectionDirection is not None
        if result:
            otherItem.preblockOutputConnectionPoint(
                self._preConnectionDirection[1])
        return result

    def preblockOutputConnectionPoint(self, direction):
        pass

    def establishConnection(self, otherItem, silent=False):
        pos = self.centerPos()

        # tuples: (own point, other item connection point)
        destinationCenterPoint = {
            ("top", "bottom"): (
                pos.x(), pos.y() - self.radius - otherItem.radius
            ),
            ("bottom", "top"): (
                pos.x(), pos.y() + self.radius + otherItem.radius
            ),
            ("left", "right"): (
                pos.x() - self.radius - otherItem.radius, pos.y()
            ),
            ("right", "left"): (
                pos.x() + self.radius + otherItem.radius, pos.y()
            )
        }

        destinationCenterPoint = QPointF(
            *destinationCenterPoint[self._preConnectionDirection])

        self.blockConnectionPoint(self._preConnectionDirection[0])
        otherItem.blockConnectionPoint(self._preConnectionDirection[1])

        if self.streamSection is not None:
            self.streamSection.connect(otherItem)
        return otherItem.centerPos() - destinationCenterPoint

    def removeConnection(self, otherItem):
        vector = otherItem.centerPos() - self.centerPos()

        if vector.x() == 0:
            if vector.y() > 0:
                direction = ("bottom", "top")
            else:
                direction = ("top", "bottom")
        else:
            if vector.x() > 0:
                direction = ("right", "left")
            else:
                direction = ("left", "right")

        self.freeConnectionPoint(direction[0])
        otherItem.freeConnectionPoint(direction[1])

        if self.streamSection is not None:
            self.streamSection.disconnect(otherItem)

    def freeConnectionPoint(self, position):
        self._connections[self._positionIndex[position]] = "disconnected"

    def blockConnectionPoint(self, position):
        self._connections[self._positionIndex[position]] = "connected"

    def removePreconnections(self):
        for i in range(len(self._connections)):
            if self._connections[i] == "preconnected":
                self._connections[i] = "disconnected"
