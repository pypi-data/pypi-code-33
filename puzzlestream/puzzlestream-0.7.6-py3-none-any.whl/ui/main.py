# -*- coding: utf-8 -*-
"""Main window module.

contains PSMainWindow, a subclass of QMainWindow
"""

import json
import os
import shutil
import subprocess
import sys
import time
from distutils.version import LooseVersion
from threading import Thread
from urllib.request import urlopen

import pkg_resources
import psutil
from puzzlestream.backend import notificationsystem
from puzzlestream.ui import colors
from puzzlestream.ui.about import PSAboutWindow
from puzzlestream.ui.codeeditor import PSCodeEdit
from puzzlestream.ui.dataview import PSDataView
from puzzlestream.ui.editorwidget import PSEditorWidget
from puzzlestream.ui.gittab import PSGitTab
from puzzlestream.ui.graphicsview import PSGraphicsView
from puzzlestream.ui.manager import PSManager
from puzzlestream.ui.module import PSModule
from puzzlestream.ui.notificationtab import PSNotificationTab
from puzzlestream.ui.outputtextedit import PSOutputTextEdit
from puzzlestream.ui.pip import PSPipGUI
from puzzlestream.ui.pipe import PSPipe
from puzzlestream.ui.plotview import PSPlotView
from puzzlestream.ui.preferences import PSPreferencesWindow
from puzzlestream.ui.switch import PSSlideSwitch
from puzzlestream.ui.translate import changeLanguage
from pyqode.python.backend import server
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QCoreApplication, QTranslator
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMenu

translate = QCoreApplication.translate


class PSMainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.__manager = PSManager(self)
        self.__manager.configChanged.connect(self.__configChanged)
        self.__manager.scene.nameChanged.connect(self.__nameChanged)
        self.__manager.scene.itemDeleted.connect(self.__itemDeleted)

        self.setupUi()
        self.puzzleGraphicsView.setScene(self.__manager.scene)
        self.puzzleGraphicsView.setConfig(self.__manager.config)

        currentDir = os.path.dirname(__file__)
        self.setWindowIcon(QIcon(
            os.path.join(currentDir, "../icons//Puzzlestream_512.png")))

        # editor initialisation
        w = self.__newEditorWidget()
        self.__editorWidgets = [w]
        self.__editors = [w.editor]
        self.horizontalSplitter.insertWidget(0, w)
        self.btnOpenCloseSecondEditor = QtWidgets.QPushButton(self)
        self.btnOpenCloseSecondEditor.setIcon(QIcon(os.path.abspath(
                os.path.join(__file__, "../../icons/plus.png"))))
        self.__editorWidgets[0].editorHeaderLayout.addWidget(
            self.btnOpenCloseSecondEditor)
        self.btnOpenCloseSecondEditor.setFixedWidth(25)
        self.btnOpenCloseSecondEditor.pressed.connect(
            lambda: self.changeRightWidgetMode("editor"))
        self.__rightWidget = self.verticalSplitter
        self.__rightWidgetMode = "puzzle"

        # add active module run / pause / stop
        self.btnRunPauseActive = QtWidgets.QToolButton()
        self.btnRunPauseActive.pressed.connect(self.__runPauseActiveModuleOnly)
        self.btnStopActive = QtWidgets.QToolButton()
        self.btnStopActive.pressed.connect(self.__stopActiveModule)
        w.editorHeaderLayout.insertWidget(0, self.btnRunPauseActive)
        w.editorHeaderLayout.insertWidget(1, self.btnStopActive)

        # pre-add second editor for windows performance reasons
        w = self.__newEditorWidget()
        self.__editorWidgets.append(w)
        self.__editors.append(w.editor)

        # module switcher
        self.__connectSwitcher()

        # welcome screen
        self.__welcomeLabel = QtWidgets.QLabel(self)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.__welcomeLabel.setFont(font)
        self.__welcomeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.__welcomeLabel.setContentsMargins(5, 0, 5, 0)
        self.horizontalSplitter.insertWidget(
            0, self.__welcomeLabel)

        # toolbar
        self.__createToolBarActions()
        actionList = self.__getToolbarActions()
        for action in actionList:
            self.toolBar.addAction(action)

        self.toolBar.setMovable(False)
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                             QtWidgets.QSizePolicy.Preferred)
        self.toolBar.insertSeparator(actionList[2])
        self.toolBar.insertSeparator(actionList[7])
        self.toolBar.insertWidget(actionList[-3], spacer)

        self.horizontalSplitter.setStretchFactor(0, 1)
        self.horizontalSplitter.setStretchFactor(1, 6)
        self.horizontalSplitter.setStretchFactor(2, 3)
        self.horizontalSplitter.setCollapsible(0, True)
        self.horizontalSplitter.setCollapsible(1, True)

        self.verticalSplitter.setStretchFactor(0, 10)
        self.verticalSplitter.setStretchFactor(1, 1)
        self.verticalSplitter.setCollapsible(1, True)

        # create puzzle toolbar actions
        self.__createPuzzleToolBarActions()
        for action in self.__getPuzzleToolbarActions():
            self.puzzleToolbar.addAction(action)

        self.__btnAddStatusAbort = QtWidgets.QPushButton(self.toolBar)
        self.__btnAddStatusAbort.pressed.connect(self.__abortAdding)
        self.__btnAddStatusAction = self.puzzleToolbar.addWidget(
            self.__btnAddStatusAbort)
        self.__btnAddStatusAction.setVisible(False)
        self.__puzzleLabel = QtWidgets.QLabel(self.puzzleToolbar)
        self.puzzleToolbar.addWidget(self.__puzzleLabel)

        self.__lblPuzzleLock = QtWidgets.QLabel()
        self.__btnPuzzleLock = PSSlideSwitch()
        self.__btnPuzzleLock.setFixedWidth(36)
        self.__btnPuzzleLock.setFixedHeight(20)
        self.__btnPuzzleLock.toggled.connect(self.__togglePuzzleLocked)
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                             QtWidgets.QSizePolicy.Expanding)
        spacer2 = QtWidgets.QWidget()
        spacer2.setSizePolicy(QtWidgets.QSizePolicy.Fixed,
                              QtWidgets.QSizePolicy.Expanding)
        spacer2.setFixedWidth(5)

        self.puzzleToolbar.addWidget(spacer)
        self.puzzleToolbar.addWidget(self.__lblPuzzleLock)
        self.puzzleToolbar.addWidget(spacer2)
        self.puzzleToolbar.addWidget(self.__btnPuzzleLock)

        # create menu bar
        self.__createFileMenuActions()
        self.__createEditMenuActions()
        self.__createViewMenuActions()
        self.__createStreamMenuActions()
        self.__createHelpMenuActions()

        # create graphics scene
        self.__createGraphicsScene()

        # set active module to None
        self.__resetActiveModule()

        # set style
        self.__currentStyle = None
        design = self.__manager.config["design"]
        self.__setStyle(design[1][design[0]])

        # shortcuts
        self.__shortcuts = {}
        self.addShortcut("F5", self.__runPauseActiveModuleOnly)
        self.addShortcut("Alt+F5", self.__runPauseActiveModule)
        self.addShortcut("Ctrl+F5", self.__run)
        self.addShortcut("F11", self.__toggleFullscreen)
        self.addShortcut("Ctrl+s", self.__saveOpenFiles)
        self.addShortcut("Esc", self.__abortAdding)

        # git
        self.__gitTab = PSGitTab(self.outputTabWidget)
        self.outputTabWidget.addTab(self.__gitTab, "Git")
        self.__manager.updateSignal.connect(self.__gitTab.reload)
        self.__gitTab.reloadSignal.connect(self.__updateGitTabHeaderAndMenu)
        self.__gitTab.fileSaveSignal.connect(self.__saveOpenFiles)
        self.__gitTab.fileUpdateSignal.connect(self.__reloadAllEditors)
        self.__createGitMenuActions()

        # notifications
        self.__notificationTab = PSNotificationTab(
            self.outputTabWidget)
        self.outputTabWidget.addTab(self.__notificationTab,
                                    "Notifications (0)")
        notificationsystem.addReactionMethod(
            self.__notificationTab.addNotification)
        self.__notificationTab.setNumberUpdateMethod(
            self.__updateNotificationHeader)

        # collect elements that should be activated and deactivated
        self.__activeElements = [
            self.puzzleGraphicsView, self.__newModuleMenu,
            self.__newPipeAction, self.__newValveAction, self.__undoAction,
            self.__redoAction, self.__copyAction, self.__cutAction,
            self.__pasteAction, self.__runAction, self.__pauseAction,
            self.__stopAction, self.__btnPuzzleLock
        ]

        """
        =======================================================================
            Start update check
        """
        thr = Thread(target=self.__checkForUpdates)
        thr.start()
        self.__updateCheckTimer = QtCore.QTimer()
        self.__updateCheckTimer.singleShot(5000, self.__updateCheckFinished)

        """
        =======================================================================
            Select language
        """
        language = self.__manager.config["language"]
        language = language[1][language[0]]
        changeLanguage(language)

        """
        =======================================================================
            Try to load last project
        """

        if len(self.__manager.config["last projects"]) > 0:
            path = self.__manager.config["last projects"][-1]
            if os.path.isdir(path) and os.path.isfile(path + "/puzzle.json"):
                self.__openProject(path, start=True)
            else:
                self.__deactivate()
        else:
            self.__deactivate()

        self.__createLibMenuActions()

        """
        =======================================================================
            Timer for CPU and RAM update
        """

        self.__loadViewer = QtWidgets.QLabel(self.mainMenuBar)
        self.__loadViewer.setFixedHeight(25)
        self.mainMenuBar.setCornerWidget(self.__loadViewer)
        self.__loadTimer = QtCore.QTimer(self)
        self.__loadTimer.setInterval(3000)
        self.__loadTimer.timeout.connect(self.__updateLoad)
        self.__updateLoad()
        self.__loadTimer.start()

        """
        =======================================================================
            Show window
        """

        self.retranslateUi()
        self.resize(1200, 800)
        self.showMaximized()
        self.__lastWindowState = "maximized"

    @property
    def __newProjectText(self):
        return translate(
            "MainWindow",
            "Welcome to Puzzlestream!\nPlease create a new project folder " +
            "using File -> New Project\nor open an existing project."
        )

    @property
    def __projectOpenText(self):
        return translate(
            "MainWindow",
            "Add a new module or select an existing one to edit its " +
            "source code."
        )

    @property
    def __newItemText(self):
        return translate(
            "MainWindow",
            "Click left on the scrollable puzzle region to add a "
        )

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.centralGrid = QtWidgets.QWidget(self)
        self.centralGrid.setObjectName("centralGrid")
        self.gridLayout = QtWidgets.QGridLayout(self.centralGrid)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalSplitter = QtWidgets.QSplitter(self.centralGrid)
        self.horizontalSplitter.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSplitter.setObjectName("horizontalSplitter")
        self.verticalSplitter = QtWidgets.QSplitter(self.horizontalSplitter)
        self.verticalSplitter.setOrientation(QtCore.Qt.Vertical)
        self.verticalSplitter.setObjectName("verticalSplitter")
        self.verticalSplitter.setContentsMargins(0, 0, 0, 0)
        self.puzzleWidget = QtWidgets.QWidget(self.verticalSplitter)
        self.puzzleWidget.setObjectName("puzzleWidget")
        self.puzzleWidgetLayout = QtWidgets.QVBoxLayout()
        self.puzzleWidget.setLayout(self.puzzleWidgetLayout)
        self.puzzleWidgetLayout.setContentsMargins(0, 0, 0, 0)
        self.puzzleToolbar = QtWidgets.QToolBar(self.puzzleWidget)
        self.puzzleWidgetLayout.addWidget(self.puzzleToolbar)
        self.puzzleGraphicsView = PSGraphicsView(self.__manager,
                                                 self.puzzleWidget)
        self.puzzleGraphicsView.setObjectName("puzzleGraphicsView")
        self.puzzleWidgetLayout.addWidget(self.puzzleGraphicsView)
        self.outputTabWidget = QtWidgets.QTabWidget(self.verticalSplitter)
        self.outputTabWidget.setObjectName("outputTabWidget")
        self.textTab = QtWidgets.QWidget()
        self.textTab.setObjectName("textTab")
        self.textTabGridLayout = QtWidgets.QGridLayout(self.textTab)
        self.textTabGridLayout.setObjectName("textTabGridLayout")
        self.outputTextEdit = PSOutputTextEdit(self.textTab)
        self.outputTextEdit.setObjectName("outputTextEdit")
        self.textTabGridLayout.addWidget(self.outputTextEdit, 0, 0, 1, 1)
        self.outputTabWidget.addTab(self.textTab, "")
        self.statisticsTab = QtWidgets.QWidget()
        self.statisticsTab.setObjectName("statisticsTab")
        self.statisticsTabGridLayout = QtWidgets.QGridLayout(
            self.statisticsTab)
        self.statisticsTabGridLayout.setObjectName("statisticsTabGridLayout")
        self.vertPlotTabLayout = QtWidgets.QVBoxLayout()
        self.vertPlotTabLayout.setObjectName("vertPlotTabLayout")
        self.horPlotSelComboBoxLayout = QtWidgets.QHBoxLayout()
        self.horPlotSelComboBoxLayout.setObjectName("horPlotSelComboBoxLayout")
        self.vertPlotTabLayout.addLayout(self.horPlotSelComboBoxLayout)
        self.statisticsTabGridLayout.addLayout(
            self.vertPlotTabLayout, 0, 0, 1, 1)
        self.outputTabWidget.addTab(self.statisticsTab, "")
        self.statisticsTextEdit = QtWidgets.QTextEdit(self.statisticsTab)
        self.statisticsTextEdit.setReadOnly(True)
        self.statisticsTextEdit.setObjectName("statisticsTextEdit")
        self.statisticsTabGridLayout.addWidget(self.statisticsTextEdit,
                                               0, 0, 1, 1)
        self.gridLayout.addWidget(self.horizontalSplitter, 0, 1, 1, 1)
        self.setCentralWidget(self.centralGrid)
        self.mainMenuBar = QtWidgets.QMenuBar(self)
        self.mainMenuBar.setGeometry(QtCore.QRect(0, 0, 800, 27))
        self.setMenuBar(self.mainMenuBar)
        self.mainMenuBar.setObjectName("MainMenuBar")
        self.menuFile = QtWidgets.QMenu(self.mainMenuBar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.mainMenuBar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuView = QtWidgets.QMenu(self.mainMenuBar)
        self.menuView.setObjectName("menuView")
        self.menuLib = QtWidgets.QMenu(self.mainMenuBar)
        self.menuLib.setObjectName("menuLib")
        self.menuStream = QtWidgets.QMenu(self.mainMenuBar)
        self.menuStream.setObjectName("menuStream")
        self.menuGit = QtWidgets.QMenu(self.mainMenuBar)
        self.menuGit.setObjectName("menuGit")
        self.menuHelp = QtWidgets.QMenu(self.mainMenuBar)
        self.menuHelp.setObjectName("menuHelp")
        self.toolBar = QtWidgets.QToolBar(self)
        self.toolBar.setObjectName("toolBar")
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.mainMenuBar.addAction(self.menuFile.menuAction())
        self.mainMenuBar.addAction(self.menuEdit.menuAction())
        self.mainMenuBar.addAction(self.menuView.menuAction())
        self.mainMenuBar.addAction(self.menuLib.menuAction())
        self.mainMenuBar.addAction(self.menuStream.menuAction())
        self.mainMenuBar.addAction(self.menuGit.menuAction())
        self.mainMenuBar.addAction(self.menuHelp.menuAction())

    def retranslateUi(self):
        self.setWindowTitle(translate("MainWindow", "Puzzlestream"))
        self.__updateProjectLoadedStatus()
        self.outputTabWidget.setTabText(
            self.outputTabWidget.indexOf(self.textTab), translate(
                "MainWindow", "Output"))
        self.outputTabWidget.setTabText(
            self.outputTabWidget.indexOf(self.statisticsTab), translate(
                "MainWindow", "Statistics"))
        self.menuFile.setTitle(translate("MainWindow", "&File"))
        self.menuEdit.setTitle(translate("MainWindow", "&Edit"))
        self.menuView.setTitle(translate("MainWindow", "&View"))
        self.menuLib.setTitle(translate("MainWindow", "&Libraries"))
        self.menuStream.setTitle(translate("MainWindow", "&Stream"))
        self.menuGit.setTitle(translate("MainWindow", "&Git"))
        self.menuHelp.setTitle(translate("MainWindow", "&Help"))
        self.toolBar.setWindowTitle(translate("MainWindow", "toolBar"))

        self.btnOpenCloseSecondEditor.setToolTip("Open second editor")
        self.btnRunPauseActive.setToolTip("Run current module")
        self.btnStopActive.setToolTip("Stop current module")
        self.__btnAddStatusAbort.setText(translate("MainWindow", "Abort"))

        self.__newProjectMenuAction.setText(
            translate("MainWindow", "&New project"))
        self.__openProjectMenuAction.setText(
            translate("MainWindow", "&Open project"))
        self.__saveProjectAsMenuAction.setText(
            translate("MainWindow", "&Save project as..."))
        self.__recentProjectsMenu.setTitle(
            translate("MainWindow", "Recent projects"))

        self.__undoMenuAction.setText(translate("MainWindow", "&Undo"))
        self.__redoMenuAction.setText(translate("MainWindow", "&Redo"))
        self.__cutMenuAction.setText(translate("MainWindow", "&Cut"))
        self.__copyMenuAction.setText(translate("MainWindow", "&Copy"))
        self.__pasteMenuAction.setText(translate("MainWindow", "&Paste"))
        self.__autoformatMenuAction.setText(
            translate("MainWindow", "&Format code"))
        self.__preferencesMenuAction.setText(
            translate("MainWindow", "Pre&ferences"))

        self.__dataMenuAction.setText(translate("MainWindow", "Show &data"))
        self.__plotMenuAction.setText(translate("MainWindow", "Show &plots"))
        self.__cleanMenuAction.setText(
            translate("MainWindow", "&Clean stream"))

        self.__puzzleViewMenuAction.setText(
            translate("MainWindow", "Puzzle mode"))
        self.__dataViewMenuAction.setText(
            translate("MainWindow", "Data view mode"))
        self.__plotViewMenuAction.setText(
            translate("MainWindow", "Plot view mode"))
        self.__fullscreenMenuAction.setText(
            translate("MainWindow", "&Toggle fullscreen"))

        self.__createLibMenuActions()

        self.__fetchMenuAction.setText(
            translate("MainWindow", "&Fetch / reload"))
        self.__pullMenuAction.setText(translate("MainWindow", "Pull"))
        self.__pushMenuAction.setText(translate("MainWindow", "Push"))

        self.__aboutMenuAction.setText(
            translate("MainWindow", "&About Puzzlestream"))

        self.__newModuleMenu.setTitle(translate("MainWindow", "New module"))
        self.__newIntModuleAction.setText(
            translate("MainWindow", "New internal module"))
        self.__newExtModuleAction.setText(
            translate("MainWindow", "New external module"))
        self.__newPipeAction.setText(translate("MainWindow", "New pipe"))
        self.__newValveAction.setText(translate("MainWindow", "New valve"))

        self.__createGraphicsSceneContextMenu()
        self.btnOpenCloseSecondEditor.setToolTip(
            translate("MainWindow", "Open second editor"))

        if self.__activeModule is not None:
            self.__updateActiveModule(self.__activeModule)
        self.__updateNotificationHeader()

        for m in self.__manager.scene.modules.values():
            m.visualStatusUpdate(m)

        self.__openProjectAction.setText(
            translate("MainWindow", "Open project"))
        self.__saveFileAction.setText(translate("MainWindow", "Save file"))
        self.__undoAction.setText(translate("MainWindow", "Back"))
        self.__redoAction.setText(translate("MainWindow", "Forward"))
        self.__copyAction.setText(translate("MainWindow", "Copy"))
        self.__cutAction.setText(translate("MainWindow", "Cut"))
        self.__pasteAction.setText(translate("MainWindow", "Paste"))
        self.__runAction.setText(translate("MainWindow", "Run puzzle"))
        self.__pauseAction.setText(translate("MainWindow", "Pause puzzle"))
        self.__stopAction.setText(translate("MainWindow", "Stop puzzle"))
        self.__puzzleViewAction.setText(translate("MainWindow", "Puzzle"))
        self.__dataViewAction.setText(translate("MainWindow", "Data view"))
        self.__plotViewAction.setText(translate("MainWindow", "Plot view"))

        self.__togglePuzzleLocked()

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.LanguageChange:
            self.retranslateUi()
        return super().changeEvent(event)

    def __setStyle(self, style):
        self.__currentStyle = style
        currentDir = os.path.dirname(__file__)
        colors.update(os.path.join(currentDir, "style/" + style + ".yml"))
        self.setStyleSheet(
            colors.parseQSS(currentDir + "/style/sheet.qss"))
        for e in self.__editors:
            e.setSyntaxColorScheme(style)

        if style == "dark":
            self.__openProjectAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//folder_white.png")))
            self.__saveFileAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//save_blue_in.png")))
            self.__undoAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//back_white.png")))
            self.__redoAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//forward_white.png")))
            self.__copyAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//copy_blue_in.png")))
            self.__cutAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//cut_blue_in.png")))
            self.__pasteAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//paste_blue_in.png")))
            self.__runAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons/play_blue_in.png")))
            self.__pauseAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons/pause_blue_in.png")))
            self.__stopAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//stop_blue_in.png")))
            self.btnStopActive.setIcon(
                QIcon(os.path.join(currentDir, "../icons//stop_blue_in.png")))
        elif style == "light":
            self.__openProjectAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//folder_blue.png")))
            self.__saveFileAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//save_blue_out.png")))
            self.__undoAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//back_blue.png")))
            self.__redoAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//forward_blue.png")))
            self.__copyAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//copy_blue_out.png")))
            self.__cutAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//cut_blue_out.png")))
            self.__pasteAction.setIcon(
                QIcon(os.path.join(currentDir,
                                   "../icons//paste_blue_out.png")))
            self.__runAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons/play_blue_out.png")))
            self.__pauseAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons/pause_blue_out.png")))
            self.__stopAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//stop_blue_out.png")))
            self.btnStopActive.setIcon(
                QIcon(os.path.join(currentDir, "../icons//stop_blue_out.png")))

        self.updateActiveModuleButtons()

    def __saveOpenFiles(self):
        for e in self.__editors:
            if self.__manager.config["autoformatOnSave"]:
                e.autoformat()
            e.file.save()
        self.__fileDirty(False)
        self.__gitTab.reload()

    def __closeOpenFiles(self):
        for e in self.__editors:
            e.file.close()

    def __reloadAllEditors(self):
        for e in self.__editors:
            if e.file.path != "":
                e.file.reload(e.file.encoding)

    def __stopAllEditors(self):
        for e in self.__editors:
            e.backend.stop()

    def __autoformatAllEditors(self):
        for e in self.__editors:
            e.autoformat()

    def __newEditorWidget(self):
        e = PSEditorWidget()
        design = self.__manager.config["design"]
        e.editor.setSyntaxColorScheme(design[1][design[0]])

        # editor settings
        e.editor.save_on_focus_out = self.__manager.config[
            "saveOnEditorFocusOut"]
        e.editor.replace_tabs_by_spaces = True
        e.editor.dirty_changed.connect(self.__fileDirty)
        e.editor.textChanged.connect(
            lambda: self.__editorTextChanged(e.editor))
        return e

    def openPuzzle(self):
        self.verticalSplitter.show()
        self.__enableAddActions()
        self.__rightWidget = self.verticalSplitter

    def closePuzzle(self):
        self.verticalSplitter.hide()
        self.__disableAddActions()
        self.__rightWidget = None

    def openSecondEditor(self, oldMode="puzzle"):
        w = self.__editorWidgets[1]
        self.horizontalSplitter.insertWidget(2, w)
        i = self.horizontalSplitter.indexOf(
            self.verticalSplitter)
        self.__updateModuleSwitchers()
        self.__updateEditorModule(self.__activeModule, 1)
        self.__connectSwitcher(1)
        self.btnOpenCloseSecondEditor.setIcon(QIcon(os.path.abspath(
            os.path.join(__file__, "../../icons/minus.png"))))
        self.btnOpenCloseSecondEditor.pressed.disconnect()
        self.btnOpenCloseSecondEditor.setToolTip(
            translate("MainWindow", "Close second editor"))
        self.btnOpenCloseSecondEditor.pressed.connect(
            lambda: self.changeRightWidgetMode(oldMode))
        self.__rightWidget = w
        self.__rightWidgetMode = "editor"
        self.__rightWidget.show()

    def closeSecondEditor(self):
        w = self.__editorWidgets[1]
        w.editor.file.save()
        w.hide()
        w.setParent(None)
        self.btnOpenCloseSecondEditor.setIcon(QIcon(os.path.abspath(
            os.path.join(__file__, "../../icons/plus.png"))))
        self.btnOpenCloseSecondEditor.pressed.disconnect()
        self.btnOpenCloseSecondEditor.pressed.connect(
            lambda: self.changeRightWidgetMode("editor"))
        self.__rightWidget = None

    def openDataview(self):
        w = PSDataView(self.__manager, self.__activeModule, self)
        self.__manager.scene.statusChanged.connect(w.statusUpdate)
        self.horizontalSplitter.insertWidget(2, w)
        self.__rightWidget = w
        self.__rightWidgetMode = "dataview"

    def closeDataview(self):
        self.__rightWidget.close()
        self.__rightWidget.hide()
        self.__rightWidget.setParent(None)
        del self.__rightWidget
        self.__rightWidget = None

    def openPlotview(self):
        w = PSPlotView(self.__manager, self.__activeModule, self)
        self.__manager.scene.statusChanged.connect(w.statusUpdate)
        self.horizontalSplitter.insertWidget(2, w)
        self.__rightWidget = w
        self.__rightWidgetMode = "dataview"

    def closePlotview(self):
        self.__rightWidget.close()
        self.__rightWidget.hide()
        self.__rightWidget.setParent(None)
        del self.__rightWidget
        self.__rightWidget = None

    def changeRightWidgetMode(self, mode):
        if mode != self.__rightWidgetMode:
            self.__manager.addStatus = None
            self.__puzzleLabel.setText("")
            self.__btnAddStatusAction.setVisible(False)
            s = self.horizontalSplitter.sizes()

            # close old mode
            if self.__rightWidgetMode == "editor":
                self.closeSecondEditor()
            elif self.__rightWidgetMode == "puzzle":
                self.closePuzzle()
            elif self.__rightWidgetMode == "dataview":
                self.closeDataview()
            elif self.__rightWidgetMode == "plotview":
                self.closePlotview()

            # choose new mode
            if mode == "editor":
                self.openSecondEditor(self.__rightWidgetMode)
            elif mode == "puzzle":
                self.openPuzzle()
            elif mode == "dataview":
                self.openDataview()
            elif mode == "plotview":
                self.openPlotview()

            self.__rightWidgetMode = mode

            # restore sizes
            if len(self.horizontalSplitter.sizes()) == 3:
                self.horizontalSplitter.setSizes(
                    [0, s[1], sum(s) - s[1]])
            else:
                self.horizontalSplitter.setSizes(
                    [0, s[1], sum(s) - s[1], 0])

    def __editorTextChanged(self, editor):
        if editor.hasFocus():
            for e in self.__editors:
                if e != editor and e.file.path == editor.file.path:
                    e.setPlainText(editor.toPlainText())

    def closeEvent(self, event):
        if self.__manager.projectPath is not None:
            self.__manager.stopAllWorkers()
            self.__manager.save(thread=False)
            self.__manager.close()

        self.__saveOpenFiles()
        self.__closeOpenFiles()
        self.__stopAllEditors()
        event.accept()

    def __resetUI(self, path):
        self.__editorWidgets[0].hide()
        self.outputTextEdit.setText("")
        self.statisticsTextEdit.setText("")

    def __createGraphicsScene(self):
        scene = self.__manager.scene
        scene.stdoutChanged.connect(self.updateText)
        scene.statusChanged.connect(self.updateStatus)
        scene.itemAdded.connect(self.__itemAdded)
        scene.dataViewRequested.connect(self.__showData)
        scene.plotViewRequested.connect(self.__showPlots)
        scene.selectionChanged.connect(self.__selectionChanged)

    def __createGraphicsSceneContextMenu(self):
        menu = QMenu()
        newModuleMenu = menu.addMenu(
            translate("MainWindow", "New module"))
        newInternalModuleAction = newModuleMenu.addAction(
            translate("MainWindow", "New internal module"))
        newExternalModuleAction = newModuleMenu.addAction(
            translate("MainWindow", "New external module"))
        newPipeAction = menu.addAction(translate("MainWindow", "New pipe"))
        newValveAction = menu.addAction(translate("MainWindow", "New valve"))

        newModuleMenu.menuAction().triggered.connect(self.__newIntModule)
        newInternalModuleAction.triggered.connect(self.__newIntModule)
        newExternalModuleAction.triggered.connect(self.__newExtModule)
        newPipeAction.triggered.connect(self.__newPipe)
        newValveAction.triggered.connect(self.__newValve)

        self.__manager.scene.setStandardContextMenu(menu)

    def addShortcut(self, sequence, target):
        sc = QtWidgets.QShortcut(QtGui.QKeySequence(sequence), self)
        sc.activated.connect(target)
        self.__shortcuts[sequence] = sc

    def __selectionChanged(self):
        if len(self.__manager.scene.selectedItemList) == 1:
            puzzleItem = self.__manager.scene.selectedItemList[0]
            if isinstance(puzzleItem, PSModule):
                self.__updateActiveModule(puzzleItem)

    def __updateActiveModule(self, module):
        self.__updateEditorModule(module)
        self.__activeModule = module
        self.outputTextEdit.setText(module.stdout)
        cursor = self.outputTextEdit.textCursor()
        cursor.movePosition(cursor.End)
        self.outputTextEdit.setTextCursor(cursor)
        self.outputTextEdit.ensureCursorVisible()
        self.outputTextEdit.setFontFamily("monospace")
        self.statisticsTextEdit.setHtml(module.statistics)
        self.outputTabWidget.setTabText(
            0, translate("MainWindow", "Output") + " - " + module.name)
        self.outputTabWidget.setTabText(
            1, translate("MainWindow", "Statistics") + " - " + module.name)
        self.__welcomeLabel.hide()
        self.__editorWidgets[0].show()
        self.updateActiveModuleButtons()

        for a in [self.__plotViewMenuAction, self.__dataViewMenuAction,
                  self.__plotViewAction, self.__dataViewAction]:
            a.setEnabled(True)

        if self.__rightWidgetMode in ["dataview", "plotview"]:
            self.__rightWidget.updatePuzzleItem(module)

    def __updateEditorModule(self, module, i=0):
        self.__disconnectSwitcher(i)
        self.__editors[i].file.open(module.filePath)
        self.__editorWidgets[i].editorFilePathLabel.setText(
            module.filePath)
        self.__editorWidgets[i].moduleSwitcher.setCurrentText(
            module.name)
        self.__connectSwitcher(i)

    def __connectSwitcher(self, i=0):
        e = self.__editorWidgets[i]
        if not e.currentIndexChangedConnected:
            e.moduleSwitcher.currentIndexChanged.connect(
                lambda index: self.__moduleSwitcherIndexChanged(i, index))
            e.currentIndexChangedConnected = True

    def __disconnectSwitcher(self, i=0):
        e = self.__editorWidgets[i]
        if e.currentIndexChangedConnected:
            e.moduleSwitcher.currentIndexChanged.disconnect()
            e.currentIndexChangedConnected = False

    def __updateModuleSwitchers(self):
        for i in range(len(self.__editorWidgets)):
            switcher = self.__editorWidgets[i].moduleSwitcher
            oldText = switcher.currentText()
            self.__disconnectSwitcher(i)
            switcher.clear()
            names = sorted(
                [m.name for m in self.__manager.scene.modules.values()])
            switcher.addItems(names)
            if oldText in names:
                switcher.setCurrentText(oldText)
            self.__connectSwitcher(i)

    def __moduleSwitcherIndexChanged(self, switcherIndex, index):
        for m in self.__manager.scene.modules.values():
            if m.name == self.__editorWidgets[switcherIndex
                                              ].moduleSwitcher.currentText():
                if switcherIndex == 0:
                    self.__updateActiveModule(m)
                else:
                    self.__updateEditorModule(m, switcherIndex)
                break

    def __runPauseActiveModule(self, stopHere=False):
        if self.__activeModule is not None:
            if self.__manager.config["saveOnRun"]:
                self.__saveOpenFiles()

            if (self.__activeModule.status in
                    ["incomplete", "finished", "error"]):
                self.__activeModule.run(stopHere=stopHere)
            elif self.__activeModule.status == "paused":
                self.__activeModule.resume()
            elif self.__activeModule.status == "running":
                self.__activeModule.pause()

    def __runPauseActiveModuleOnly(self):
        self.__runPauseActiveModule(stopHere=True)

    def __stopActiveModule(self):
        self.__activeModule.stop()

    def __nameChanged(self, module):
        self.__updateModuleSwitchers()
        if module == self.__activeModule:
            self.__updateActiveModule(module)

    def __fileDirty(self, dirty):
        self.__saveFileAction.setEnabled(dirty)

    def __createFileMenuActions(self):
        self.__newProjectMenuAction = self.menuFile.addAction("")
        self.__openProjectMenuAction = self.menuFile.addAction("")
        self.__saveProjectAsMenuAction = self.menuFile.addAction("")

        self.__newProjectMenuAction.triggered.connect(self.__newProject)
        self.__openProjectMenuAction.triggered.connect(self.__openProject)
        self.__saveProjectAsMenuAction.triggered.connect(self.__saveProjectAs)

        self.__recentProjectsMenu = QtWidgets.QMenu("")
        self.menuFile.insertMenu(
            self.__saveProjectAsMenuAction, self.__recentProjectsMenu)

    def __createEditMenuActions(self):
        self.__undoMenuAction = self.menuEdit.addAction("")
        self.__redoMenuAction = self.menuEdit.addAction("")
        self.__undoRedoSeparator = self.menuEdit.addSeparator()
        self.__cutMenuAction = self.menuEdit.addAction("")
        self.__copyMenuAction = self.menuEdit.addAction("")
        self.__pasteMenuAction = self.menuEdit.addAction("")
        self.__cutCopyPasteSeparator = self.menuEdit.addSeparator()
        self.__autoformatMenuAction = self.menuEdit.addAction("")
        self.__preferencesSeperator = self.menuEdit.addSeparator()
        self.__preferencesMenuAction = self.menuEdit.addAction("")

        self.__undoMenuAction.triggered.connect(self.__editors[0].undo)
        self.__redoMenuAction.triggered.connect(self.__editors[0].redo)
        self.__cutMenuAction.triggered.connect(self.__editors[0].cut)
        self.__copyMenuAction.triggered.connect(self.__editors[0].copy)
        self.__pasteMenuAction.triggered.connect(self.__editors[0].paste)
        self.__autoformatMenuAction.triggered.connect(
            self.__editors[0].autoformat)
        self.__preferencesMenuAction.triggered.connect(self.__showPreferences)

    def __createViewMenuActions(self):
        self.__puzzleViewMenuAction = self.menuView.addAction("")
        self.__puzzleViewMenuAction.triggered.connect(
            lambda: self.changeRightWidgetMode("puzzle"))
        self.__dataViewMenuAction = self.menuView.addAction("")
        self.__dataViewMenuAction.triggered.connect(
            lambda: self.changeRightWidgetMode("dataview"))
        self.__plotViewMenuAction = self.menuView.addAction("")
        self.__plotViewMenuAction.triggered.connect(
            lambda: self.changeRightWidgetMode("plotview"))
        self.__fullscreenMenuAction = self.menuView.addAction("")
        self.__fullscreenMenuAction.triggered.connect(self.__toggleFullscreen)

    def __createLibMenuActions(self):
        self.menuLib.clear()
        self.__pipGUIMenuAction = self.menuLib.addAction(
            translate("MainWindow", "pip package manager"))
        self.__pipGUIMenuAction.triggered.connect(
            self.__openPipGUI)
        self.__addLibMenuAction = self.menuLib.addAction(
            translate("MainWindow", "Add lib path"))
        self.__libSeparator = self.menuLib.addSeparator()
        self.__addLibMenuAction.triggered.connect(self.__addLib)

        for path in self.__manager.libs:
            menu = self.menuLib.addMenu(path)
            openAction = menu.addAction(translate("MainWindow", "Open folder"))
            openAction.triggered.connect(lambda: self.__open_file(path))
            deleteAction = menu.addAction(translate("MainWindow", "Delete"))
            deleteAction.triggered.connect(lambda: self.__deleteLib(path))

    def __createStreamMenuActions(self):
        self.__dataMenuAction = self.menuStream.addAction("")
        self.__plotMenuAction = self.menuStream.addAction("")
        self.menuStream.addSeparator()
        self.__cleanMenuAction = self.menuStream.addAction("")

        self.__dataMenuAction.triggered.connect(self.__showStreamDataView)
        self.__plotMenuAction.triggered.connect(self.__showStreamPlotView)
        self.__cleanMenuAction.triggered.connect(self.__clearStream)

    def __createGitMenuActions(self):
        self.__fetchMenuAction = self.menuGit.addAction("")
        self.__pullMenuAction = self.menuGit.addAction("")
        self.__pushMenuAction = self.menuGit.addAction("")

        self.__fetchMenuAction.triggered.connect(self.__gitTab.fetch)
        self.__pullMenuAction.triggered.connect(self.__gitTab.pull)
        self.__pushMenuAction.triggered.connect(self.__gitTab.push)

    def __createHelpMenuActions(self):
        self.__aboutMenuAction = self.menuHelp.addAction("")
        self.__aboutMenuAction.triggered.connect(self.__showAboutWindow)

    def __toggleFullscreen(self):
        if self.isFullScreen():
            if self.__lastWindowState == "maximized":
                self.showMaximized()
            else:
                self.showNormal()
        else:
            if self.isMaximized():
                self.__lastWindowState = "maximized"
            else:
                self.__lastWindowState = "normal"
            self.showFullScreen()
        self.__updateLoad()

    def __showPreferences(self):
        preferences = PSPreferencesWindow(self.__manager.config, self)
        preferences.show()

    def __showStreamDataView(self):
        view = PSDataView(self.__manager, parent=self)
        self.__manager.scene.statusChanged.connect(view.statusUpdate)
        view.showMaximized()

    def __showStreamPlotView(self):
        view = PSPlotView(self.__manager, None, self)
        self.__manager.scene.statusChanged.connect(view.statusUpdate)
        view.show()

    def __clearStream(self):
        reply = QtWidgets.QMessageBox.question(
            self,
            translate("MainWindow", "Confirm clean up"),
            translate(
                "MainWindow",
                "Are you sure you want to erase ALL data from the stream?"
            ),
            QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes
        )

        if reply == QtWidgets.QMessageBox.Yes:
            self.__manager.stream.clear()

    def __showAboutWindow(self):
        about = PSAboutWindow(self)

    def __updateRecentProjects(self):
        self.__recentProjectsMenu.clear()

        for item in self.__manager.config["last projects"][::-1]:
            action = self.__recentProjectsMenu.addAction(item)
            action.triggered.connect(
                lambda x, item=item: self.__openProject(item))

    def __createToolBarActions(self):
        self.__openProjectAction = QAction(self)
        self.__saveFileAction = QAction(self)
        self.__undoAction = QAction(self)
        self.__redoAction = QAction(self)
        self.__copyAction = QAction(self)
        self.__cutAction = QAction(self)
        self.__pasteAction = QAction(self)
        self.__runAction = QAction(self)
        self.__pauseAction = QAction(self)
        self.__stopAction = QAction(self)
        self.__puzzleViewAction = QAction(self)
        self.__dataViewAction = QAction(self)
        self.__plotViewAction = QAction(self)

        self.__saveFileAction.setEnabled(False)

        self.__openProjectAction.triggered.connect(self.__openProject)
        self.__saveFileAction.triggered.connect(self.__saveFileToolbar)
        self.__runAction.triggered.connect(self.__run)
        self.__pauseAction.triggered.connect(self.__pause)
        self.__stopAction.triggered.connect(self.__stop)
        self.__connectEditorActions(self.__editors[0])
        self.__puzzleViewAction.triggered.connect(
            lambda: self.changeRightWidgetMode("puzzle"))
        self.__dataViewAction.triggered.connect(
            lambda: self.changeRightWidgetMode("dataview"))
        self.__plotViewAction.triggered.connect(
            lambda: self.changeRightWidgetMode("plotview"))

    def __connectEditorActions(self, editor):
        self.__undoAction.triggered.connect(editor.undo)
        self.__redoAction.triggered.connect(editor.redo)
        self.__copyAction.triggered.connect(editor.copy)
        self.__cutAction.triggered.connect(editor.cut)
        self.__pasteAction.triggered.connect(editor.paste)

    def __disconnectEditorActions(self):
        self.__undoAction.triggered.disconnect()
        self.__redoAction.triggered.disconnect()
        self.__copyAction.triggered.disconnect()
        self.__cutAction.triggered.disconnect()
        self.__pasteAction.triggered.disconnect(e)

    def __getToolbarActions(self):
        return [self.__openProjectAction, self.__saveFileAction,
                self.__undoAction, self.__redoAction,
                self.__copyAction, self.__cutAction, self.__pasteAction,
                self.__runAction, self.__pauseAction, self.__stopAction,
                self.__puzzleViewAction, self.__dataViewAction,
                self.__plotViewAction]

    def __createPuzzleToolBarActions(self):
        self.__newModuleMenu = QMenu("", self)
        self.__newIntModuleAction = self.__newModuleMenu.addAction("")
        self.__newExtModuleAction = self.__newModuleMenu.addAction("")
        self.__newPipeAction = QAction("", self)
        self.__newValveAction = QAction("", self)

        self.__newModuleMenu.menuAction().triggered.connect(
            self.__newIntModule)
        self.__newIntModuleAction.triggered.connect(self.__newIntModule)
        self.__newExtModuleAction.triggered.connect(self.__newExtModule)
        self.__newPipeAction.triggered.connect(self.__newPipe)
        self.__newValveAction.triggered.connect(self.__newValve)

    def __getPuzzleToolbarActions(self):
        return [self.__newModuleMenu.menuAction(), self.__newPipeAction,
                self.__newValveAction]

    def updateText(self, module, text):
        if module == self.__activeModule:
            if text is None:
                self.outputTextEdit.setText("")
                self.outputTextEdit.activateAutoscroll()
            else:
                cursor = self.outputTextEdit.textCursor()
                cursor.movePosition(cursor.End)
                f = cursor.charFormat()
                f.setFontFamily("monospace")
                cursor.insertText(text, f)

    def updateStatus(self, module):
        if module == self.__activeModule:
            self.statisticsTextEdit.setHtml(module.statistics)
            self.updateActiveModuleButtons()

    def updateActiveModuleButtons(self):
        currentDir = os.path.dirname(__file__)

        if self.__currentStyle == "dark":
            if (self.__activeModule is not None and
                    self.__activeModule.status == "running"):
                self.btnRunPauseActive.setIcon(QIcon(os.path.join(
                    currentDir, "../icons/pause_blue_in.png")))
            else:
                self.btnRunPauseActive.setIcon(QIcon(os.path.join(
                    currentDir, "../icons/play_blue_in.png")))
        elif (self.__activeModule is not None and
                self.__currentStyle == "light"):
            if self.__activeModule.status == "running":
                self.btnRunPauseActive.setIcon(QIcon(os.path.join(
                    currentDir, "../icons/pause_blue_out.png")))
            else:
                self.btnRunPauseActive.setIcon(QIcon(os.path.join(
                    currentDir, "../icons/play_blue_out.png")))

    def __updateGitTabHeaderAndMenu(self):
        self.__manager.save()
        self.outputTabWidget.setTabText(
            2, "Git (%d)" % (self.__gitTab.numberOfChangedItems))

        for a in [self.__pullMenuAction, self.__pushMenuAction]:
            a.setEnabled(self.__gitTab.hasRemote)

    def __updateLoad(self):
        vm = psutil.virtual_memory()

        text = (str(psutil.cpu_percent()) +
                "% CPU   " +
                "%.1f" % (vm.used / vm.total * 100) +
                "% RAM   ")

        if (self.isFullScreen() or not
                self.__manager.config["clockOnlyFullscreen"]):
            text += time.strftime("%H:%M") + "  "

        self.__loadViewer.setText(text)

    def __configChanged(self, key):
        if key == "last projects":
            self.__updateRecentProjects()
        elif key == "clockOnlyFullscreen":
            self.__updateLoad()
        elif key == "saveOnEditorFocusOut":
            for e in self.__editors:
                e.save_on_focus_out = self.__manager.config[
                    "saveOnEditorFocusOut"]
        elif key == "design":
            design = self.__manager.config["design"]
            self.__setStyle(design[1][design[0]])

    def __updateNotificationHeader(self):
        self.outputTabWidget.setTabText(
            3,
            translate("MainWindow", "Notifications") + " (%d)" % (
                len(self.__notificationTab.notifications))
        )

    """
        reaction routines
    """

    def __deactivate(self):
        for e in self.__editorWidgets:
            e.hide()
        self.__welcomeLabel.setText(self.__newProjectText)
        self.__welcomeLabel.show()
        for e in self.__activeElements:
            e.setEnabled(False)

    def __activate(self):
        self.__welcomeLabel.setText(self.__projectOpenText)
        for e in self.__activeElements:
            e.setEnabled(True)

    def __updateProjectLoadedStatus(self):
        if self.__manager.projectPath is None:
            self.__deactivate()
        else:
            self.__activate()

    def __newProject(self, path=None):
        if not isinstance(path, str):
            path = QtWidgets.QFileDialog.getExistingDirectory(
                self,
                translate("MainWindow", "New project folder")
            )

        if path != "":
            if len(os.listdir(path)) == 0:
                self.__manager.newProject(path)
                self.setWindowTitle(
                    "Puzzlestream - " + self.__manager.projectPath)
                self.__resetUI(path)
            else:
                msg = QtWidgets.QMessageBox(self)
                msg.setText(translate("MainWindow", "Directory not empty."))
                msg.show()

        self.__updateProjectLoadedStatus()
        self.__gitTab.setRepo(self.__manager.repo)

    def __openProject(self, path=None, start=False):
        if not isinstance(path, str):
            path = QtWidgets.QFileDialog.getExistingDirectory(
                self,
                translate("MainWindow", "Open project folder")
            )

        if os.path.isdir(path):
            if os.path.isfile(path + "/puzzle.json"):
                self.__manager.load(path, silent=start)
                self.setWindowTitle("Puzzlestream - " + path)
                self.__resetUI(path)
            elif not start:
                msg = QtWidgets.QMessageBox(self)
                msg.setText(
                    translate(
                        "MainWindow",
                        "The chosen project folder is not valid. " +
                        "Please choose another one.")
                )
                msg.exec()
                self.__openProject()

        self.__updateProjectLoadedStatus()
        self.__updateModuleSwitchers()
        self.__gitTab.setRepo(self.__manager.repo)
        if self.__btnPuzzleLock.isChecked() != self.__manager.puzzleLocked:
            self.__btnPuzzleLock.click()
        self.__togglePuzzleLocked()

    def __saveProjectAs(self, path=None):
        if not isinstance(path, str):
            path = QtWidgets.QFileDialog.getExistingDirectory(
                self,
                "Save project folder")

        if os.path.isdir(path):
            if len(os.listdir(path)) == 0:
                self.__manager.saveAs(path)
                self.setWindowTitle("Puzzlestream - " + path)
                self.__resetUI(path)
            else:
                msg = QtWidgets.QMessageBox(self)
                msg.setText(translate("MainWindow", "Directory not empty."))
                msg.show()

        self.__updateProjectLoadedStatus()

    def __saveFileToolbar(self, value):
        self.__saveOpenFiles()

    def __abortAdding(self):
        self.__manager.addStatus = None
        self.__btnAddStatusAction.setVisible(False)
        self.__enableAddActions()
        self.__puzzleLabel.setText("")
        self.__welcomeLabel.setText(self.__projectOpenText)

    def __newIntModule(self):
        self.__disableAddActions()
        self.__welcomeLabel.setText(self.__newItemText + "module.")
        self.__manager.addStatus = "intModule"
        self.__puzzleLabel.setText(
            translate(
                "MainWindow",
                "Click on a free spot inside the puzzle view to add a new " +
                "internal module."
            )
        )
        self.__btnAddStatusAction.setVisible(True)
        self.__updateModuleSwitchers()

    def __newExtModule(self):
        self.__disableAddActions()
        self.__welcomeLabel.setText(self.__newItemText + "module.")
        self.__manager.addStatus = "extModule"
        self.__puzzleLabel.setText(
            translate(
                "MainWindow",
                "Click on a free spot inside the puzzle view to add a new " +
                "external module."
            )
        )
        self.__btnAddStatusAction.setVisible(True)
        self.__updateModuleSwitchers()

    def __newPipe(self):
        self.__disableAddActions()
        self.__welcomeLabel.setText(self.__newItemText + "pipe.")
        self.__manager.addStatus = "pipe"
        self.__puzzleLabel.setText(
            translate(
                "MainWindow",
                "Click on a free spot inside the puzzle view to add a new " +
                "pipe."
            )
        )
        self.__btnAddStatusAction.setVisible(True)

    def __newValve(self):
        self.__disableAddActions()
        self.__welcomeLabel.setText(self.__newItemText + "valve.")
        self.__manager.addStatus = "valve"
        self.__puzzleLabel.setText(
            translate(
                "MainWindow",
                "Click on a free spot inside the puzzle view to add a new " +
                "valve."
            )
        )
        self.__btnAddStatusAction.setVisible(True)

    def __resetActiveModule(self):
        self.__activeModule = None
        for a in [self.__plotViewMenuAction, self.__dataViewMenuAction,
                  self.__plotViewAction, self.__dataViewAction]:
            a.setEnabled(False)

    def __itemAdded(self, item):
        self.__enableAddActions()
        self.__welcomeLabel.setText(self.__projectOpenText)
        self.__puzzleLabel.setText("")
        self.__btnAddStatusAction.setVisible(False)

        if self.__manager.puzzleLocked:
            self.__btnPuzzleLock.click()
            self.__togglePuzzleLocked()

        self.__manager.save()
        self.__gitTab.reload()

        if isinstance(item, PSModule):
            self.__updateModuleSwitchers()

    def __itemDeleted(self, item):
        if item == self.__activeModule:
            self.__welcomeLabel.setText(self.__projectOpenText)
            self.__editorWidgets[0].hide()
            self.__welcomeLabel.show()
            self.horizontalSplitter.setStretchFactor(0, 0)
            self.__resetActiveModule()

        if isinstance(item, PSModule):
            self.__updateModuleSwitchers()

        self.__manager.save()
        self.__gitTab.reload()

    def __togglePuzzleLocked(self, *args):
        if self.__btnPuzzleLock.isChecked():
            self.__manager.setAllItemsFixed()
            self.__lblPuzzleLock.setText(
                translate("MainWindow", "puzzle locked"))
        else:
            self.__manager.setAllItemsMovable()
            self.__lblPuzzleLock.setText(
                translate("MainWindow", "puzzle unlocked"))

        self.__manager.save()
        self.__gitTab.reload()

    def __enableAddActions(self):
        for a in self.puzzleToolbar.actions():
            if not isinstance(a, QtWidgets.QWidgetAction):
                a.setVisible(True)

        for a in (self.__runAction, self.__pauseAction, self.__stopAction):
            a.setEnabled(True)

    def __disableAddActions(self):
        for a in self.puzzleToolbar.actions():
            if not isinstance(a, QtWidgets.QWidgetAction):
                a.setVisible(False)

        for a in (self.__runAction, self.__pauseAction, self.__stopAction):
            a.setEnabled(False)

    def __showData(self, puzzleItem):
        if puzzleItem.streamSection is not None:
            view = PSDataView(self.__manager, puzzleItem, parent=self)
            self.__manager.scene.statusChanged.connect(view.statusUpdate)
            view.showMaximized()

    def __showPlots(self, puzzleItem):
        if puzzleItem.streamSection is not None:
            view = PSPlotView(self.__manager, puzzleItem, self)
            self.__manager.scene.statusChanged.connect(view.statusUpdate)
            view.show()

    def __run(self):
        if (self.__activeModule is not None and
                self.__manager.config["saveOnRun"]):
            self.__saveOpenFiles()

        for module in self.__manager.scene.modules.values():
            if ((module.status == "incomplete" or
                 module.status == "finished" or
                 module.status == "error" or
                 module.status == "test failed") and not module.hasInput):
                module.run()
            else:
                module.resume()

    def __pause(self):
        for module in self.__manager.scene.modules.values():
            module.pause()

    def __stop(self):
        for module in self.__manager.scene.modules.values():
            module.stop()

    """
    ===========================================================================
        Pip stuff
    """

    def __openPipGUI(self):
        window = PSPipGUI(parent=self)
        window.show()

    """
    ===========================================================================
        Lib stuff
    """

    def __addLib(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            translate("MainWindow", "Add lib folder")
        )
        if os.path.isdir(path):
            self.__manager.addLib(path)

            args = ["-s" + lib for lib in self.__manager.libs]

            for e in self.__editors:
                e.backend.start(
                    server.__file__, args=args)
            self.__createLibMenuActions()

    def __open_file(self, filename):
        if sys.platform == "win32":
            os.startfile(filename)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filename])

    def __deleteLib(self, path):
        self.__manager.deleteLib(path)
        self.__createLibMenuActions()

    """
    ===========================================================================
        Update check stuff
    """

    def __checkForUpdates(self):
        self.__updateStatus = None

        try:
            version = pkg_resources.get_distribution("puzzlestream").version
            with urlopen("https://pypi.org/pypi/puzzlestream/json") as res:
                versionAvailable = json.loads(res.read())["info"]["version"]
                self.__updateStatus = (version, versionAvailable)
        except Exception as e:
            print(e)

    def __updateCheckFinished(self):
        if isinstance(self.__updateStatus, tuple):
            linkEnding = translate("MainWindow", "get-puzzlestream/")

            if sys.platform == "linux" or sys.platform == "linux2":
                linkEnding += "linux"
            elif sys.platform == "darwin":
                linkEnding += "mac-os-x"
            elif sys.platform == "win32" or sys.platform == "win64":
                linkEnding += "windows"

            version, versionAvailable = self.__updateStatus
            if LooseVersion(versionAvailable) > LooseVersion(version):
                notificationsystem.newNotification(
                    translate("MainWindow", "An update to version ") +
                    str(versionAvailable) +
                    translate(
                        "MainWindow",
                        " is available; you are " +
                        "currently using version "
                    ) + str(version) + ". " +
                    translate(
                        "MainWindow",
                        "Please click <a href=\"https://puzzlestream.org/"
                    ) + linkEnding +
                    translate(
                        "MainWindow",
                        "\">here</a> for update instructions."
                    )
                )
