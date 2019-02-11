# -*- coding: utf-8 -*-
"""About window module.

contains PSAboutWindow
"""

import os
from PyQt5 import QtCore, QtGui, QtWidgets

translate = QtCore.QCoreApplication.translate


class PSAboutWindow(QtWidgets.QMainWindow):
    """Window that shows some information about Puzzlestream."""

    def __init__(self, parent=None):
        """Window init.

        Args:
            parent: Qt parent
        """
        super().__init__(parent)
        self.label = QtWidgets.QLabel()
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.label.setOpenExternalLinks(True)
        self.setCentralWidget(self.label)
        self.setFixedSize(400, 280)
        self.show()

        self.retranslateUi()

    def retranslateUi(self):
        self.label.setText(
            translate(
                "About",
                "<p>Puzzlestream is an interactive analysis enviroment for " +
                "Python, providing a fast and simple way from raw data to " +
                "meaningful results and visualisations. By organising your " +
                "code in modules, Puzzlestream gives you an instantaneous " +
                "overview of your project's structure - however complicated " +
                "it may be. Highly interactive graphical interfaces support " +
                "you in gaining an intuition for your data, asking the " +
                "right questions and finding the corresponding answers. " +
                "Platform independence and easy installation allow a quick " +
                "start on any system you like.</p><p>More information and " +
                "the documentation can be found " +
                "<a href=\"https://puzzlestream.org\">here</a>.</p>"
            )
        )

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.LanguageChange:
            self.retranslateUi()
        return super().changeEvent(event)

    def closeEvent(self, event):
        """Set parent to None on exit to free RAM."""
        self.setParent(None)
        event.accept()
