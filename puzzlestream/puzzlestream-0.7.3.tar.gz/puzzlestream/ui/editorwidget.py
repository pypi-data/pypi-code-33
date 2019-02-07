import os

from puzzlestream.ui.codeeditor import PSCodeEdit
from pyqode.python.backend import server
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class PSEditorWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__layout = QVBoxLayout()
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.setSpacing(0)
        self.setLayout(self.__layout)
        self.editorHeader = QWidget(self)
        self.editorHeader.setObjectName("editorHeader")
        self.editorHeaderLayout = QHBoxLayout()
        self.editorHeader.setLayout(self.editorHeaderLayout)
        self.editorFilePathLabel = QLabel(self.editorHeader)
        self.editorFilePathLabel.setObjectName("editorFilePathLabel")
        self.editorHeaderLayout.addWidget(self.editorFilePathLabel)
        self.moduleSwitcher = QComboBox(self.editorHeader)
        self.moduleSwitcher.setObjectName("moduleSwitcher")
        self.moduleSwitcher.setSizePolicy(QSizePolicy.Minimum,
                                          QSizePolicy.Maximum)
        self.editorHeaderLayout.addWidget(self.moduleSwitcher)
        self.__layout.addWidget(self.editorHeader)

        self.editor = PSCodeEdit(server.__file__)
        self.__layout.addWidget(self.editor)
        self.currentIndexChangedConnected = False
        self.currentModule = None
