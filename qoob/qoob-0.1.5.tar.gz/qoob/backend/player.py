#!/usr/bin/python3
from PyQt5 import QtWidgets, QtCore, QtMultimedia

try:
    import qoob.backend.parser as parser
except ImportError:
    import backend.parser as parser

REPEAT_ALL = 1
REPEAT_SINGLE = 2


class MediaPlayer(QtMultimedia.QMediaPlayer):
    currentMediaChanged = QtCore.pyqtSignal(str)
    setItemColor = QtCore.pyqtSignal(str)
    setSliderRange = QtCore.pyqtSignal(int, int)
    setSliderValue = QtCore.pyqtSignal(int)
    setPlayPauseIcon = QtCore.pyqtSignal(object)
    setShuffleIcon = QtCore.pyqtSignal(object)
    setRepeatIcon = QtCore.pyqtSignal(object)
    setStatusMessage = QtCore.pyqtSignal(str, str)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.icon = parent.icon
        self.log = parent.logger.new("Player")
        self.preferences = parent.preferences
        self.mediaStatusChanged.connect(self._mediaChangedEvent)
        self.durationChanged.connect(self._updateDuration)
        self.positionChanged.connect(self._updateSlider)
        self.seekableChanged.connect(self._seekableEvent)
        self.random = QtCore.QRandomGenerator()
        self.playLater = QtCore.QTimer(singleShot=True, interval=500)
        self.playLater.timeout.connect(self.nextEvent)

        self.setVolume(self.preferences.get("state", "volume"))
        self.lastPlayed = {}
        self.lastState = None
        self.lastItem = None
        self.mediaLength = "?"
        self.path = ""

        self.statusTimer = QtCore.QTimer(interval=500)
        self.statusTimer.timeout.connect(self._updateStatus)
        self.statusTimer.start()

    def _currentItem(self):
        return self.parent.tabWidget.current.currentItem()

    def _currentTab(self):
        index = self.parent.tabWidget.currentIndex()
        tabName = self.parent.tabWidget.tabText(index)
        tabName = tabName.lstrip("&")  # KDE bug fix (auto append of &)
        return tabName

    def _currentView(self):
        return self.parent.tabWidget.current

    def _mediaChangedEvent(self, event):
        tab = self._currentTab()
        if not tab in self.lastPlayed:
            self.lastPlayed[tab] = []

        currentRow = self._currentView().currentIndex().row()
        if event == QtMultimedia.QMediaPlayer.EndOfMedia:
            self.setPosition(0)
            self.nextEvent()
        elif event == QtMultimedia.QMediaPlayer.InvalidMedia:
            self.lastPlayed[tab].append(currentRow)
            self.setItemColor.emit("red")
            self.setStatusMessage.emit(f"! {self.path}", "Invalid media")
            self.playLater.start()  # Cannot call nextEvent directly (too fast)
        elif event == QtMultimedia.QMediaPlayer.BufferedMedia:
            if not self.repeat == REPEAT_SINGLE:
                self.lastPlayed[tab].append(currentRow)
                self.log.info(f"'{self._currentTab()}' playlist: {self.lastPlayed[tab]}")

    def _seekableEvent(self):
        if self.resumePlayback and self.isSeekable():
            self.resumePlayback = False
            self.setPosition(self.preferences.get("state", "playback position"))

    def _setCurrentItem(self, item):
        # Slots/signals too slow, sync required
        self._currentView().setCurrentItem(item)

    def _nextPlay(self):
        next = self._currentView().itemBelow(self._currentItem())
        self._setCurrentItem(next)
        self.activateSelection()

    def _nextRepeat(self):
        next = self._currentView().topLevelItem(0)
        self._setCurrentItem(next)
        self.activateSelection()

    def _nextShuffle(self):
        currentRow = self._currentView().currentIndex().row()
        itemCount = self._currentView().topLevelItemCount()
        tab = self._currentTab()
        self.lastPlayed.setdefault(tab, [])

        if len(self.lastPlayed[tab]) == itemCount:
            self.lastPlayed[tab] = []
            if self.repeat == REPEAT_ALL:
                self.nextEvent()
            else:
                self.stopEvent()
        else:
            next = self._shuffleTrack(itemCount)
            self._setCurrentItem(next)
            self.activateSelection()

    def _shuffleTrack(self, count):
        tab = self._currentTab()
        next = self.random.bounded(count)
        while next in self.lastPlayed[tab]:
            next = self.random.bounded(count)
        return self._currentView().topLevelItem(next)

    def _updateDuration(self, duration):
        s = duration / 1000
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        self.mediaLength = "%02d:%02d:%02d" % (h, m, s)
        self.setSliderRange.emit(0, self.duration())

    def _updateSlider(self, progress):
        if not self.parent.ui.playbackSlider.isSliderDown():
            self.setSliderValue.emit(progress)

    def _updateStatus(self):
        if self.duration() > -1:
            right, left = None, None

            if not self.state() == self.lastState:
                if self.state() == QtMultimedia.QMediaPlayer.PlayingState:
                    left = "Now playing: " + self.tags["title"] + " (" + self.tags["artist"] + ")"
                elif self.state() == QtMultimedia.QMediaPlayer.PausedState:
                    left = "Paused"
                elif self.state() == QtMultimedia.QMediaPlayer.StoppedState:
                    left = "Stopped"

            if self.state() == QtMultimedia.QMediaPlayer.PlayingState and not self.mediaLength == "?":
                s = self.parent.ui.playbackSlider.value() / 1000
                m, s = divmod(s, 60)
                h, m = divmod(m, 60)
                elapsed = "%02d:%02d:%02d" % (h, m, s)
                right = f"    {elapsed} / {self.mediaLength}"

            self.lastState = self.state()
            self.setStatusMessage.emit(left, right)

    def activateSelection(self):
        self.resumePlayback = False
        if self.lastItem:
            self.lastItem.setColor("none")

        if self._currentItem():
            self._currentItem().setColor("green")
            self.setCurrentMedia(self._currentItem().text(5))
            self.lastItem = self._currentItem()

        elif self._currentView().topLevelItemCount() > 0:
            first = self._currentView().topLevelItem(0)
            self._currentView().setCurrentItem(first)
            self._setCurrentItem(first)
            self.activateSelection()

    def clearTabPlaylist(self, tab):
        if tab in self.lastPlayed:
            del self.lastPlayed[tab]

    def clearViewerPlaylist(self):
        self.lastPlayed["Library viewer"] = []

    def nextEvent(self, forced=False):
        currentRow = self._currentView().currentIndex().row()
        itemCount = self._currentView().topLevelItemCount()
        if self._currentItem():
            if self.repeat == REPEAT_SINGLE:
                self.activateSelection()
            elif self.shuffle:
                self._nextShuffle()
            elif currentRow == itemCount - 1:
                if self.repeat == REPEAT_ALL or (forced and self.state() == QtMultimedia.QMediaPlayer.StoppedState):
                    tab = self._currentTab()
                    self.lastPlayed[tab] = []
                    self._nextRepeat()
                else:
                    self.stopEvent()
            else:
                self._nextPlay()
        elif self.shuffle:
            self._nextShuffle()
        else:
            self.activateSelection()

    def pauseEvent(self):
        self.playLater.stop()
        self.pause()
        self.setPlayPauseIcon.emit(self.icon["play"])

    def playEvent(self):
        self.playLater.stop()
        if self.state() == QtMultimedia.QMediaPlayer.PausedState:
            self.play()
            self.setPlayPauseIcon.emit(self.icon["pause"])
        elif self.state() == QtMultimedia.QMediaPlayer.StoppedState:
            self.activateSelection()

    def playPauseEvent(self):
        self.playLater.stop()
        if self.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.pauseEvent()
        else:
            self.playEvent()

    def previousEvent(self):
        self.playLater.stop()
        if self._currentItem():
            tab = self._currentTab()
            if self.lastPlayed[tab]:
                self.lastPlayed[tab].pop()
            if self.lastPlayed[tab]:
                previous = self.lastPlayed[tab].pop()
                previous = self._currentView().topLevelItem(previous)
            else:
                previous = self._currentView().itemAbove(self._currentItem())
                if not previous:
                    previous = self._currentView().topLevelItem(0)
            self._setCurrentItem(previous)
        self.activateSelection()

    def setCurrentMedia(self, path):
        self.path = path
        self.media = QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(self.path))
        self.setMedia(self.media)
        self.play()
        self.setPlayPauseIcon.emit(self.icon["pause"])
        self.tags = self.parent.parser.header(self.path)
        self.currentMediaChanged.emit(path)
        self.lastState = None
        if "error" in self.tags:
            self.setItemColor.emit("yellow")
            self.setStatusMessage.emit(self.path, self.tags["error"])

    def shuffleEvent(self, event=None, enable=None):
        self.shuffle = not self.shuffle if enable is None else enable
        if self.shuffle:
            self.setShuffleIcon.emit(self.icon["shuffle_on"])
        else:
            self.setShuffleIcon.emit(self.icon["shuffle_off"])

    def repeatEvent(self, event=None, state=None):
        self.repeat = self.repeat + 1 if state is None else state
        if self.repeat > 2:
            self.repeat = 0
        icon = {0: "repeat_off", 1: "repeat_all", 2: "repeat_single"}
        stateIcon = icon[self.repeat]
        self.setRepeatIcon.emit(self.icon[stateIcon])

    def skip(self, seconds):
        self.setPosition(self.position() + seconds*1000)

    def stopEvent(self):
        tab = self._currentTab()
        self.stop()
        self.playLater.stop()
        self.lastPlayed[tab] = []
        self.setSliderValue.emit(0)
        self.setPlayPauseIcon.emit(self.icon["play"])
