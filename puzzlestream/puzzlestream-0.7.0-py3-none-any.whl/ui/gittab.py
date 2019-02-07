# -*- coding: utf-8 -*-
"""Git tab module.

contains PSGitTab, a subclass of QWidget
"""

from os import path
from threading import Thread

from puzzlestream.backend.signal import PSSignal
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

translate = QCoreApplication.translate


class PSGitTab(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.__repo = None
        self.__layout = QGridLayout()
        self.__reloadSignal = PSSignal()
        self.__fileSaveSignal, self.__fileUpdateSignal = PSSignal(), PSSignal()
        self.setLayout(self.__layout)

        self.btnBranchMenu = QPushButton()
        self.btnFetch = QPushButton()
        self.btnStageAll = QPushButton()
        self.btnUnstageAll = QPushButton()
        self.btnRevertAll = QPushButton()
        self.btnCommit = QPushButton()
        self.btnPullNPush = QPushButton()
        self.changedWidget = QWidget()
        self.stagedWidget = QWidget()
        self.lblCommitMessage = QLabel()
        self.fileListChanged = QListWidget()
        self.fileListStaged = QListWidget()
        self.txtCommitMessage = PSCommitMessageBox()

        self.lblChanged = QLabel()
        self.lblStaged = QLabel()
        self.btnStage = QPushButton()
        self.btnRevert = QPushButton()
        self.btnUnstage = QPushButton()
        self.__changedLayout = QHBoxLayout()
        self.__stagedLayout = QHBoxLayout()
        self.changedWidget.setLayout(self.__changedLayout)
        self.stagedWidget.setLayout(self.__stagedLayout)
        self.__changedLayout.addWidget(self.lblChanged)
        self.__changedLayout.addWidget(self.btnStage)
        self.__changedLayout.addWidget(self.btnRevert)
        self.__stagedLayout.addWidget(self.lblStaged)
        self.__stagedLayout.addWidget(self.btnUnstage)

        for btn in [self.btnFetch, self.btnStageAll, self.btnUnstageAll,
                    self.btnRevertAll, self.btnPullNPush]:
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            btn.setStyleSheet("* { width: 1.25em; height: 1.25em; }")
            # btn.setFixedSize(24, 24)

        for btn in [self.btnStage, self.btnUnstage, self.btnRevert,
                    self.btnBranchMenu]:
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            btn.setFixedSize(20, 20)

        for btn in [self.btnCommit, self.changedWidget, self.stagedWidget,
                    self.lblCommitMessage]:
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.txtCommitMessage.setMinimumWidth(200)

        self.menuCheckout = QMenu()
        self.__menuCheckoutActions = []
        self.btnBranchMenu.setMenu(self.menuCheckout)

        self.fileListChanged.setSelectionMode(QListWidget.ExtendedSelection)
        self.fileListStaged.setSelectionMode(QListWidget.ExtendedSelection)

        self.btnFetch.pressed.connect(self.fetch)
        self.btnStageAll.pressed.connect(self.stageAll)
        self.btnUnstageAll.pressed.connect(self.unstageAll)
        self.btnRevertAll.pressed.connect(self.revertAll)
        self.btnPullNPush.pressed.connect(self.pull)
        self.btnStage.pressed.connect(self.stage)
        self.btnUnstage.pressed.connect(self.unstage)
        self.btnRevert.pressed.connect(self.revert)
        self.btnCommit.pressed.connect(self.commit)
        self.fileListChanged.selectionModel().selectionChanged.connect(
            self.__changedSelectionChanged)
        self.fileListStaged.selectionModel().selectionChanged.connect(
            self.__stagedSelectionChanged)
        self.txtCommitMessage.textChanged.connect(self.__commitMessageChanged)
        self.txtCommitMessage.submitSignal.connect(self.commit)

        base = path.join(__file__, "../../icons/")
        self.btnStageAll.setIcon(QIcon(path.abspath(base + "plus.png")))
        self.btnUnstageAll.setIcon(QIcon(path.abspath(base + "minus.png")))
        self.btnRevertAll.setIcon(QIcon(path.abspath(base + "back_blue.png")))
        self.btnPullNPush.setIcon(QIcon(path.abspath(base + "pull_push.png")))
        self.btnStage.setIcon(QIcon(path.abspath(base + "plus.png")))
        self.btnUnstage.setIcon(QIcon(path.abspath(base + "minus.png")))
        self.btnRevert.setIcon(QIcon(path.abspath(base + "back_blue.png")))

        self.__layout.addWidget(self.btnBranchMenu, 0, 0)
        self.__layout.addWidget(self.btnFetch, 1, 0)
        self.__layout.addWidget(self.btnStageAll, 2, 0)
        self.__layout.addWidget(self.btnUnstageAll, 3, 0)
        self.__layout.addWidget(self.btnRevertAll, 4, 0)
        self.__layout.addWidget(self.btnPullNPush, 5, 0)
        self.__layout.addWidget(self.changedWidget, 0, 1)
        self.__layout.addWidget(self.fileListChanged, 1, 1, 6, 1)
        self.__layout.addWidget(self.stagedWidget, 0, 2)
        self.__layout.addWidget(self.fileListStaged, 1, 2, 6, 1)
        self.__layout.addWidget(self.lblCommitMessage, 0, 3)
        self.__layout.addWidget(self.txtCommitMessage, 1, 3, 4, 1)
        self.__layout.addWidget(self.btnCommit, 5, 3)

        self.__fetchTimer = QTimer()
        self.__fetchTimer.setInterval(60000)
        self.__fetchTimer.timeout.connect(self.fetch)
        self.__fetchTimer.start()

        self.__pullThread = None
        self.__pullTimer = QTimer()
        self.__pullTimer.setInterval(50)
        self.__pullTimer.timeout.connect(self.__pullCallback)

        self.btnBranchMenu.setEnabled(False)
        self.retranslateUi()

    def retranslateUi(self):
        if self.currentBranchHasRemote:
            self.btnFetch.setToolTip(translate("GitTab", "Fetch"))
        else:
            self.btnFetch.setToolTip(translate("GitTab", "Reload"))
        self.btnStageAll.setToolTip(translate("GitTab", "Stage all changes"))
        self.btnUnstageAll.setToolTip(
            translate("GitTab", "Unstage all changes"))
        self.btnRevertAll.setToolTip(translate("GitTab", "Revert all changes"))
        self.btnCommit.setText(translate("GitTab", "Commit"))
        self.btnPullNPush.setToolTip(translate("GitTab", "Pull and push"))
        self.lblCommitMessage.setToolTip(translate("GitTab", "Commit message"))

        self.lblChanged.setText(translate("GitTab", "Changed"))
        self.lblStaged.setText(translate("GitTab", "Staged changes"))
        self.btnStage.setToolTip(translate("GitTab", "Stage"))
        self.btnRevert.setToolTip(translate("GitTab", "Revert"))
        self.btnUnstage.setToolTip(translate("GitTab", "Unstage"))

    def changeEvent(self, event):
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi()
        return super().changeEvent(event)

    @property
    def reloadSignal(self):
        return self.__reloadSignal

    @property
    def fileSaveSignal(self):
        return self.__fileSaveSignal

    @property
    def fileUpdateSignal(self):
        return self.__fileUpdateSignal

    @property
    def numberOfChangedItems(self):
        return self.fileListChanged.count()

    @property
    def hasRemote(self):
        if self.__repo is not None:
            return len(self.__repo.remotes) > 0
        return False

    @property
    def currentBranchHasRemote(self):
        if self.__repo is not None:
            return self.__repo.active_branch.tracking_branch() is not None
        return False

    def setRepo(self, repo):
        self.__repo = repo
        self.__updateBranchMenu()
        self.fetch()

    def reload(self):
        self.fileListChanged.clear()
        self.fileListStaged.clear()

        if self.__repo is not None:
            self.btnBranchMenu.setText(self.__repo.active_branch.name)

            for f in self.__repo.untracked_files:
                item = QListWidgetItem(f)
                item.setBackground(Qt.darkRed)
                self.fileListChanged.addItem(item)

            for f in [item.a_path for item in self.__repo.index.diff(None)]:
                item = QListWidgetItem(f)
                item.setBackground(Qt.darkGreen)
                self.fileListChanged.addItem(item)

            for f in [item.a_path for item in self.__repo.index.diff("HEAD")]:
                self.fileListStaged.addItem(QListWidgetItem(f))

            for btn in [self.btnFetch, self.btnPullNPush, self.btnCommit,
                        self.btnRevertAll, self.btnStageAll,
                        self.btnUnstageAll]:
                btn.setEnabled(True)

            if not self.currentBranchHasRemote:
                self.btnPullNPush.setEnabled(False)
                self.btnFetch.setToolTip(translate("GitTab", "Reload"))
                self.btnFetch.setIcon(QIcon(path.abspath(
                    path.join(__file__, "../../icons/reload.png"))))
            else:
                self.btnFetch.setToolTip(translate("GitTab", "Fetch"))
                self.btnFetch.setIcon(QIcon(path.abspath(
                    path.join(__file__, "../../icons/fetch.png"))))

                nAhead = len(list(self.__repo.iter_commits(
                    "%s@{u}..%s" % (self.__repo.active_branch,
                                    self.__repo.active_branch)))
                             )
                nBehind = len(list(self.__repo.iter_commits(
                    "%s..%s@{u}" % (self.__repo.active_branch,
                                    self.__repo.active_branch)))
                              )
                if (self.__pullThread is None or not
                        self.__pullThread.isAlive()):
                    self.btnPullNPush.setToolTip(
                        translate("GitTab", "Pull" + " (%d)" % (nBehind)))
                    self.btnPullNPush.setEnabled(nBehind > 0)
                else:
                    self.btnPullNPush.setToolTip("Pulling...")
                    self.btnPullNPush.setEnabled(False)
                # self.btnPush.setText("Push (%d)" % (nAhead))
                # self.btnPush.setEnabled(nAhead > 0)
        else:
            for btn in [self.btnFetch, self.btnPullNPush, self.btnCommit,
                        self.btnRevertAll, self.btnStageAll,
                        self.btnUnstageAll]:
                btn.setEnabled(False)

        self.__changedSelectionChanged()
        self.__stagedSelectionChanged()
        self.__commitMessageChanged()

        self.reloadSignal.emit()

    def fetch(self):
        if self.hasRemote:
            self.btnFetch.setToolTip("Fetching...")
            self.btnFetch.setEnabled(False)

            try:
                thr = CallbackThread(target=self.__repo.git.fetch,
                                     callback=self.__fetchCallback)
                thr.start()
            except Exception as e:
                print(e)
        else:
            self.reload()

    def __fetchCallback(self):
        self.reload()
        if self.currentBranchHasRemote:
            self.btnFetch.setToolTip(translate("GitTab", "Fetch"))
        else:
            self.btnFetch.setToolTip(translate("GitTab", "Reload"))
        self.btnFetch.setEnabled(True)

    def stageAll(self):
        self.__repo.git.add(".")
        self.reload()

    def revertAll(self):
        if self.__confirmRevert(allChanges=True):
            self.__repo.git.checkout(
                "--", *[item.a_path for item in self.__repo.untracked_files])
            self.__repo.git.checkout(
                "--", *[item.a_path for item in self.__repo.index.diff(None)])
        self.reload()
        self.fileUpdateSignal.emit()
        self.fileSaveSignal.emit()

    def unstageAll(self):
        self.__repo.index.reset("HEAD")
        self.reload()

    def stage(self):
        for item in self.fileListChanged.selectedItems():
            self.__repo.git.add(item.text())
        self.reload()

    def revert(self):
        if self.__confirmRevert():
            self.__repo.git.checkout(
                "--",
                *[item.text() for item in self.fileListChanged.selectedItems()]
            )
        self.reload()
        self.fileUpdateSignal.emit()
        self.fileSaveSignal.emit()

    def unstage(self):
        self.__repo.index.reset(
            "HEAD",
            paths=[item.text() for item in self.fileListStaged.selectedItems()]
        )
        self.reload()

    def commit(self):
        if (self.txtCommitMessage.toPlainText() != "" and
                len(self.__repo.index.diff("HEAD")) > 0):
            self.__repo.index.commit(self.txtCommitMessage.toPlainText())
            self.txtCommitMessage.clear()
            self.reload()

    def pullAndPush(self):
        self.pull()
        self.push()

    def pull(self):
        try:
            self.__pullThread = Thread(target=self.__pull)
            self.__pullThread.start()
            self.__pullTimer.start()
        except Exception as e:
            print(e)

    def __pull(self):
        self.fileSaveSignal.emit()
        self.__repo.git.pull()

    def __pullCallback(self):
        if not self.__pullThread.isAlive():
            self.__pullTimer.stop()
            self.fileUpdateSignal.emit()
            self.reload()

    def push(self):
        self.btnPullNPush.setToolTip("Pushing...")
        self.btnPullNPush.setEnabled(False)

        try:
            thr = CallbackThread(target=self.__repo.git.push,
                                 callback=self.reload)
            thr.start()
        except Exception as e:
            print(e)

    def __changedSelectionChanged(self):
        enabled = len(self.fileListChanged.selectedIndexes()) != 0
        self.btnStage.setEnabled(enabled)
        self.btnRevert.setEnabled(enabled)

    def __stagedSelectionChanged(self):
        self.btnUnstage.setEnabled(
            len(self.fileListStaged.selectedIndexes()) != 0)

    def __commitMessageChanged(self):
        self.btnCommit.setEnabled(
            self.__repo is not None and
            self.txtCommitMessage.toPlainText() != "" and
            len(self.__repo.index.diff("HEAD")) > 0
        )

    def __confirmRevert(self, allChanges: bool = False):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("Revert confirmation")
        if allChanges:
            msgBox.setText("Are you sure you want to revert all changes?")
        else:
            msgBox.setText(
                "Are you sure you want to revert the selected changes?")
        msgBox.setStandardButtons(QMessageBox.Yes)
        msgBox.addButton(QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)
        if msgBox.exec_() == QMessageBox.Yes:
            return True
        return False

    def __updateBranchMenu(self):
        self.menuCheckout.clear()
        self.__menuCheckoutActions.clear()

        if self.__repo is not None:
            for h in self.__repo.heads:
                a = self.menuCheckout.addAction(h.name)
                a.triggered.connect(
                    lambda checked=False, n=h.name: self.__checkout(n))
                self.__menuCheckoutActions.append(a)

            a = self.menuCheckout.addAction("+ New branch")
            a.triggered.connect(self.__newBranch)
            self.__menuCheckoutActions.append(a)

    def __checkout(self, name: str):
        self.__repo.git.checkout(name)
        self.__updateBranchMenu()
        self.btnBranchMenu.setText(self.__repo.active_branch.name)
        self.fetch()

    def __newBranch(self):
        print("new branch")


class CallbackThread(Thread):
    def __init__(self, callback=None, callback_args=(), *args, **kwargs):
        target = kwargs.pop('target')
        super().__init__(target=self.target_with_callback, *args, **kwargs)
        self.callback = callback
        self.method = target
        self.callback_args = callback_args

    def target_with_callback(self):
        self.method()
        if self.callback is not None:
            self.callback(*self.callback_args)


class PSCommitMessageBox(QPlainTextEdit):

    def __init__(self, text="", parent=None):
        self.__submitSignal = PSSignal()
        return super().__init__(text, parent)

    @property
    def submitSignal(self):
        return self.__submitSignal

    def keyPressEvent(self, e):
        if (e.key() in (Qt.Key_Return, Qt.Key_Enter) and
                (e.modifiers() and Qt.ControlModifier)):
            self.submitSignal.emit()
        return super().keyPressEvent(e)
