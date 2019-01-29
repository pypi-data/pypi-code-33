#!/usr/bin/python3
import os
from PyQt5 import QtGui, QtWidgets, QtCore, QtMultimedia


class ArtLabel(QtWidgets.QLabel):
    setArtButtonIcon = QtCore.pyqtSignal(object)
    setFrameVisible = QtCore.pyqtSignal(bool)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.preferences = parent.preferences
        self.icon = parent.icon
        self.setMaximumSize(QtCore.QSize(280, 280))
        self.setAlignment(QtCore.Qt.AlignCenter)
        size = self.preferences.get("art", "size")
        art = self.icon["qoob"].pixmap(size, size)
        self.art = QtGui.QPixmap(None)
        self.setPixmap(art)

    def display(self):
        if self.preferences.get("art", "enable"):
            size = self.preferences.get("art", "size")
            if self.art.isNull():
                art = self.icon["qoob"].pixmap(64, 64)
                self.setFrameVisible.emit(self.preferences.get("art", "show empty"))
            else:
                aspectRatio = QtCore.Qt.IgnoreAspectRatio
                smooth = QtCore.Qt.SmoothTransformation
                art = self.art.scaled(size, size, aspectRatio, transformMode=smooth)
                self.setFrameVisible.emit(True)
            self.setFixedSize(size, size)
            self.setPixmap(art)

    def load(self, path):
        self.art = self.parent.parser.art(path)

    def toggle(self):
        if self.preferences.get("art", "enable"):
            self.preferences.db["art"]["enable"] = False
            self.setArtButtonIcon.emit(self.icon["art_off"])
            self.setFrameVisible.emit(False)
        else:
            self.preferences.db["art"]["enable"] = True
            self.setArtButtonIcon.emit(self.icon["art_on"])
            self.display()
        self.preferences.save()


class PopupWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.preferences = parent.preferences
        self.textLabel = QtWidgets.QLabel()
        self.textLabel.setWordWrap(True)
        self.textLabel.setAlignment(QtCore.Qt.AlignCenter)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.textLabel)
        layout.setAlignment(self.textLabel, QtCore.Qt.AlignCenter)
        self.setLayout(layout)

        self.hideTimer = QtCore.QTimer(singleShot=True)
        self.hideTimer.timeout.connect(self.hide)

        # Hide window from system taskbar
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)
        if os.environ.get("DESKTOP_SESSION") == "openbox":
            self.setAttribute(QtCore.Qt.WA_X11NetWmWindowTypeToolBar)
        else:
            self.setAttribute(QtCore.Qt.WA_X11NetWmWindowTypeUtility)
        self.setMouseTracking(True)
        self.updateView()

    def mouseMoveEvent(self, event):
        self.hide()

    def mousePressEvent(self, event):
        self.hide()

    def _setFontSize(self, message):
        font = self.textLabel.font()
        font.setPointSize(self.preferences.get("popup", "font size"))
        outside = self.contentsRect()
        inside = outside.marginsRemoved(QtCore.QMargins(1,5,1,5))

        while font.pointSize() > 5:
            size = QtGui.QFontMetrics(font).boundingRect(outside, QtCore.Qt.TextWordWrap, message)
            if inside.width() >= size.width() and inside.height() >= size.height():
                break
            else:
                font.setPointSize(font.pointSize()-1)
        self.textLabel.setFont(font)

    def _setGeometry(self):
        width = self.preferences.get("popup", "width")
        height = self.preferences.get("popup", "height")
        self.setFixedSize(width, height)

    def _setPosition(self):
        available = QtWidgets.QDesktopWidget().availableGeometry()
        position = self.frameGeometry()
        move = self.preferences.get("popup", "position")

        if move == "top left":
            position.moveTopLeft(available.topLeft())
        elif move == "top center":
            position.moveCenter(available.center())
            position.moveTop(available.top())
        elif move == "top right":
            position.moveTopRight(available.topRight())
        elif move == "bottom left":
            position.moveBottomLeft(available.bottomLeft())
        elif move == "bottom center":
            position.moveCenter(available.center())
            position.moveBottom(available.bottom())
        elif move == "bottom right":
            position.moveBottomRight(available.bottomRight())
        elif move == "middle left":
            position.moveCenter(available.center())
            position.moveLeft(available.left())
        elif move == "middle center":
            position.moveCenter(available.center())
        elif move == "middle right":
            position.moveCenter(available.center())
            position.moveRight(available.right())

        x = position.x() + self.preferences.get("popup", "horizontal offset")
        y = position.y() + self.preferences.get("popup", "vertical offset")
        self.move(x, y)

    def _setStyle(self):
        fg = QtGui.QColor(self.preferences.get("popup", "foreground"))
        bg = QtGui.QColor(self.preferences.get("popup", "background"))
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.WindowText, fg);
        palette.setColor(QtGui.QPalette.Window, bg);
        self.setPalette(palette)
        self.textLabel.setPalette(palette)
        self.setWindowOpacity(self.preferences.get("popup", "opacity"))

        font = QtGui.QFont()
        font.setFamily(self.preferences.get("popup", "font family"))
        self.textLabel.setFont(font)

    def display(self, message):
        if self.preferences.get("popup", "enable"):
            width = int(self.preferences.get("popup", "width") * 0.6)
            height = int(self.preferences.get("popup", "height") * 0.6)
            self.textLabel.setText(message)
            self._setFontSize(message)
            self.hideTimer.start(1000 * self.preferences.get("popup", "duration"))
            self.show()

    def updateView(self):
        self._setStyle()
        self._setGeometry()
        self._setPosition()


class TrayIcon(QtWidgets.QSystemTrayIcon):
    hideWindow = QtCore.pyqtSignal()
    showWindow = QtCore.pyqtSignal()
    close = QtCore.pyqtSignal()
    play = QtCore.pyqtSignal()
    stop = QtCore.pyqtSignal()
    next = QtCore.pyqtSignal()
    previous = QtCore.pyqtSignal()
    shuffle = QtCore.pyqtSignal()
    showPreferencesForm = QtCore.pyqtSignal()
    popup = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.icon = parent.icon
        self.preferences = parent.preferences
        self.setIcon(QtGui.QIcon(self.icon["qoob"].pixmap(64, 64)))  # SVG to pixmap conversion (KDE compatibility)
        self.activated.connect(self._clickEvent)
        self._menuSetup()
        if self.preferences.get("general", "tray icon"):
            self.show()

    def _clickEvent(self, event):
        if event == QtWidgets.QSystemTrayIcon.Trigger:
            if self.preferences.get("general", "tray minimize"):
                self.hideWindow.emit() if self.parent.isVisible() else self.showWindow.emit()
        elif event == QtWidgets.QSystemTrayIcon.MiddleClick:
            self.play.emit()
            if self.parent.player.state() == QtMultimedia.QMediaPlayer.PausedState:
                self.popup.emit("Paused")

    def _menuSetup(self):
        menu = QtWidgets.QMenu()
        menu.addAction(self.icon["play"], "Play/Pause", self.play.emit)
        menu.addAction(self.icon["next"], "Next", self.next.emit)
        menu.addAction(self.icon["previous"], "Previous", self.previous.emit)
        menu.addAction(self.icon["shuffle_on"], "Shuffle", self._shuffleTrayEvent)
        menu.addAction(self.icon["stop"], "Stop", self.stop.emit)
        menu.addSeparator()
        menu.addAction(self.icon["preferences"], "Preferences", self.showPreferencesForm.emit)
        menu.addAction(self.icon["quit"], "Quit", self.close.emit)
        self.setContextMenu(menu)

    def _shuffleTrayEvent(self):
        self.shuffle.emit()
        self.popup.emit("Shuffle enabled" if self.parent.player.shuffle else "Shuffle disabled")
