#!/usr/bin/env python3
import sys
import time
import os
import platform

from PyQt5.QtWidgets import (QMainWindow, QWidget, QToolTip, QLabel, QLineEdit,
                             QPushButton, QAction, qApp, QApplication, QHBoxLayout, QVBoxLayout, QGridLayout,
                             QDialogButtonBox, QGroupBox, QStyleFactory)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import QThread, QObject, Qt,  pyqtSignal, pyqtSlot

__APP_PATH__ = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir))
sys.path.insert(0, __APP_PATH__)  # Add module to sys path

from quackdns import launcher, config, cli


__APP_TITLE__ = "Quack DNS configuration"


class Worker(QObject):
    update_signal = pyqtSignal(tuple)


    @pyqtSlot()
    def status_update_function(self): # A slot takes no params
        while True:
            time.sleep(1)
            try:
                message_str = "Service: {}".format(
                    "Running" if launcher.check_running() else "Stopped")
                self.update_signal.emit((0, message_str))
            except launcher.SingleInstanceError as e:
                self.update_signal.emit((1, repr(e)))


class App(QMainWindow):

    def __init__(self):
        super().__init__()

        # From https://stackoverflow.com/a/33453124

        # 1 - create Worker and Thread inside the Form
        self.background_worker = Worker()  # no parent!
        self.status_update_thread = QThread()  # no parent!

        # 2 - Connect Worker`s Signals to Form method slots to post data.
        self.background_worker.update_signal.connect(self.update_statusbar_slot)

        # 3 - Move the Worker object to the Thread object
        self.background_worker.moveToThread(self.status_update_thread)

        # 4 - Connect Worker Signals to the Thread slots
        # self.background_worker.finished.connect(self.status_update_thread.quit)

        # 5 - Connect Thread started signal to Worker operational slot method
        self.status_update_thread.started.connect(self.background_worker.status_update_function)

        # * - Thread finished signal will close the app if you want!
        # self.thread.finished.connect(app.exit)

        # 6 - Start the thread
        self.status_update_thread.start()


        self.initUI()
        self.defaults_arg_dict = {"config": config.__DEFAULT_CONFIG_PATH__,
                                  "interval": config.__DEFAULT_UPDATE_INTERVAL__}

    def closeEvent(self, event):
        self.status_update_thread.quit()
        event.accept()


    def update_statusbar_slot(self, update_tuple):
        if update_tuple[0] == 0:
            self.statusBar().showMessage("{}".format(update_tuple[1]))
        else:
            print(update_tuple[1])

    def initUI(self):

        self.settings = None
        if os.path.exists(config.__DEFAULT_CONFIG_PATH__):
            self.settings = config.Settings()
            self.settings.load(config.__DEFAULT_CONFIG_PATH__)

        descriptionLabel = QLabel("Quack lets you configure your "
                                  "Duck DNS account on a local machine. "
                                  "If you don't have an account on Duck "
                                  "DNS or you don't remember your data, "
                                  "go to <a href=\"https://www.duckdns.org/\">https://www.duckdns.org/</a>.")
        descriptionLabel.setWordWrap(True)
        descriptionLabel.setTextFormat(Qt.RichText)
        descriptionLabel.setTextInteractionFlags(Qt.TextBrowserInteraction)
        descriptionLabel.setOpenExternalLinks(True)

        # Domain
        domainLabel = QLabel("Domain")
        domainLineEdit = QLineEdit()
        self.domainLineEdit = domainLineEdit
        domainLineEdit.setPlaceholderText("""http://subdomain.duckdns.org""")
        domainLineEdit.setClearButtonEnabled(True)
        if self.settings is not None:
            domainLineEdit.setText(self.settings.get_domain())

        # Token
        tokenLabel = QLabel("Token")
        tokenLineEdit = QLineEdit()
        self.tokenLineEdit = tokenLineEdit
        tokenLineEdit.setPlaceholderText("XXXXXXXX")
        tokenLineEdit.setClearButtonEnabled(True)
        if self.settings is not None:
            tokenLineEdit.setText(self.settings.get_token())

        # Apply - Cancel
        self.applyButton = QPushButton(QIcon.fromTheme("media-playback-start"), "Apply and Start")
        self.cancelButton = QPushButton(QIcon.fromTheme("media-playback-stop"), "Stop")
        buttonsBox = QDialogButtonBox()
        buttonsBox.addButton(self.cancelButton, QDialogButtonBox.RejectRole)
        buttonsBox.addButton(self.applyButton, QDialogButtonBox.ApplyRole)

        # Signal connection
        self.applyButton.clicked.connect(self.update_settings_and_restart)
        self.cancelButton.clicked.connect(self.stop_daemon)

        # Add all to main widget
        mainWidget = QWidget()
        mainBox = QVBoxLayout()
        grid = QGridLayout()
        grid.addWidget(domainLabel, 0, 0)
        grid.addWidget(domainLineEdit, 0, 1)
        grid.addWidget(tokenLabel, 1, 0)
        grid.addWidget(tokenLineEdit, 1, 1)
        mainBox.addWidget(descriptionLabel)
        mainBox.addLayout(grid)
        mainBox.addStretch()
        mainBox.addWidget(buttonsBox)
        mainWidget.setLayout(mainBox)
        self.setCentralWidget(mainWidget)

        self.setMinimumSize(300, 225)
        self.setWindowTitle(__APP_TITLE__)

        self.statusBar().showMessage("Checking service status..")

        self.show()


    def configure_dns_parameters(self):
        settings = config.Settings()
        settings.set_domain(self.domainLineEdit.text())
        settings.set_token(self.tokenLineEdit.text())
        return settings

    def update_settings_and_restart(self):
        settings = self.configure_dns_parameters()
        settings.save(config.__DEFAULT_CONFIG_PATH__)
        self.statusBar().showMessage("Starting service..")
        launcher.start(self.defaults_arg_dict)

    def stop_daemon(self):
        self.statusBar().showMessage("Stopping service..")
        launcher.stop(self.defaults_arg_dict)
        time.sleep(1)


def main():
    app = QApplication(sys.argv)

    # Use desktop settings
    qApp.setDesktopSettingsAware(True)
    app.setDesktopSettingsAware(True)

    # Create application instance
    myApp = App()

    # Apply title and icon
    myApp.setWindowIcon(QIcon.fromTheme('preferences-system'))
    myApp.setWindowTitle(__APP_TITLE__)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    
