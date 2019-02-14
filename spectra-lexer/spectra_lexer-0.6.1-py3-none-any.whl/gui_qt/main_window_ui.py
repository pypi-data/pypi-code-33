# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'spectra_lexer\gui_qt\main_window.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(580, 470)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/spectra_lexer/icon.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.w_main = QtWidgets.QWidget(MainWindow)
        self.w_main.setObjectName("w_main")
        self.layout_main = QtWidgets.QGridLayout(self.w_main)
        self.layout_main.setObjectName("layout_main")
        self.w_search_input = QtWidgets.QLineEdit(self.w_main)
        self.w_search_input.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.w_search_input.sizePolicy().hasHeightForWidth())
        self.w_search_input.setSizePolicy(sizePolicy)
        self.w_search_input.setMinimumSize(QtCore.QSize(150, 22))
        self.w_search_input.setMaximumSize(QtCore.QSize(150, 22))
        self.w_search_input.setReadOnly(False)
        self.w_search_input.setObjectName("w_search_input")
        self.layout_main.addWidget(self.w_search_input, 0, 0, 1, 1)
        self.w_display_title = QtWidgets.QLineEdit(self.w_main)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.w_display_title.sizePolicy().hasHeightForWidth())
        self.w_display_title.setSizePolicy(sizePolicy)
        self.w_display_title.setMinimumSize(QtCore.QSize(0, 22))
        self.w_display_title.setMaximumSize(QtCore.QSize(16777215, 22))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        self.w_display_title.setFont(font)
        self.w_display_title.setReadOnly(True)
        self.w_display_title.setPlaceholderText("")
        self.w_display_title.setObjectName("w_display_title")
        self.layout_main.addWidget(self.w_display_title, 0, 1, 1, 1)
        self.w_search_matches = SearchListWidget(self.w_main)
        self.w_search_matches.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.w_search_matches.sizePolicy().hasHeightForWidth())
        self.w_search_matches.setSizePolicy(sizePolicy)
        self.w_search_matches.setMinimumSize(QtCore.QSize(150, 0))
        self.w_search_matches.setMaximumSize(QtCore.QSize(150, 16777215))
        self.w_search_matches.setAutoScroll(False)
        self.w_search_matches.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.w_search_matches.setProperty("showDropIndicator", False)
        self.w_search_matches.setObjectName("w_search_matches")
        self.layout_main.addWidget(self.w_search_matches, 1, 0, 1, 1)
        self.w_display_text = TextGraphWidget(self.w_main)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.w_display_text.sizePolicy().hasHeightForWidth())
        self.w_display_text.setSizePolicy(sizePolicy)
        self.w_display_text.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        self.w_display_text.setFont(font)
        self.w_display_text.setMouseTracking(True)
        self.w_display_text.setUndoRedoEnabled(False)
        self.w_display_text.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.w_display_text.setReadOnly(True)
        self.w_display_text.setObjectName("w_display_text")
        self.layout_main.addWidget(self.w_display_text, 1, 1, 1, 1)
        self.w_search_bottom = QtWidgets.QFrame(self.w_main)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.w_search_bottom.sizePolicy().hasHeightForWidth())
        self.w_search_bottom.setSizePolicy(sizePolicy)
        self.w_search_bottom.setMinimumSize(QtCore.QSize(150, 180))
        self.w_search_bottom.setMaximumSize(QtCore.QSize(150, 180))
        self.w_search_bottom.setObjectName("w_search_bottom")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.w_search_bottom)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.w_search_mappings = SearchListWidget(self.w_search_bottom)
        self.w_search_mappings.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.w_search_mappings.sizePolicy().hasHeightForWidth())
        self.w_search_mappings.setSizePolicy(sizePolicy)
        self.w_search_mappings.setMinimumSize(QtCore.QSize(0, 120))
        self.w_search_mappings.setAutoScroll(False)
        self.w_search_mappings.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.w_search_mappings.setProperty("showDropIndicator", False)
        self.w_search_mappings.setObjectName("w_search_mappings")
        self.verticalLayout.addWidget(self.w_search_mappings)
        self.w_search_type = QtWidgets.QCheckBox(self.w_search_bottom)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.w_search_type.sizePolicy().hasHeightForWidth())
        self.w_search_type.setSizePolicy(sizePolicy)
        self.w_search_type.setObjectName("w_search_type")
        self.verticalLayout.addWidget(self.w_search_type)
        self.w_search_regex = QtWidgets.QCheckBox(self.w_search_bottom)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.w_search_regex.sizePolicy().hasHeightForWidth())
        self.w_search_regex.setSizePolicy(sizePolicy)
        self.w_search_regex.setObjectName("w_search_regex")
        self.verticalLayout.addWidget(self.w_search_regex)
        self.layout_main.addWidget(self.w_search_bottom, 2, 0, 1, 1)
        self.w_display_info = QtWidgets.QFrame(self.w_main)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.w_display_info.sizePolicy().hasHeightForWidth())
        self.w_display_info.setSizePolicy(sizePolicy)
        self.w_display_info.setMinimumSize(QtCore.QSize(0, 180))
        self.w_display_info.setMaximumSize(QtCore.QSize(16777215, 180))
        self.w_display_info.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.w_display_info.setObjectName("w_display_info")
        self.layout_info = QtWidgets.QVBoxLayout(self.w_display_info)
        self.layout_info.setContentsMargins(6, 6, 6, 6)
        self.layout_info.setSpacing(2)
        self.layout_info.setObjectName("layout_info")
        self.w_display_desc = QtWidgets.QLabel(self.w_display_info)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.w_display_desc.sizePolicy().hasHeightForWidth())
        self.w_display_desc.setSizePolicy(sizePolicy)
        self.w_display_desc.setMinimumSize(QtCore.QSize(0, 0))
        self.w_display_desc.setMaximumSize(QtCore.QSize(16777215, 64))
        font = QtGui.QFont()
        font.setFamily("Courier New")
        font.setPointSize(10)
        self.w_display_desc.setFont(font)
        self.w_display_desc.setAlignment(QtCore.Qt.AlignCenter)
        self.w_display_desc.setWordWrap(True)
        self.w_display_desc.setObjectName("w_display_desc")
        self.layout_info.addWidget(self.w_display_desc)
        self.w_display_board = StenoBoardWidget(self.w_display_info)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.w_display_board.sizePolicy().hasHeightForWidth())
        self.w_display_board.setSizePolicy(sizePolicy)
        self.w_display_board.setMinimumSize(QtCore.QSize(0, 100))
        self.w_display_board.setObjectName("w_display_board")
        self.layout_info.addWidget(self.w_display_board)
        self.layout_main.addWidget(self.w_display_info, 2, 1, 1, 1)
        self.layout_main.setColumnMinimumWidth(0, 150)
        self.layout_main.setColumnMinimumWidth(1, 275)
        self.layout_main.setRowMinimumHeight(0, 22)
        self.layout_main.setRowMinimumHeight(1, 210)
        self.layout_main.setRowMinimumHeight(2, 180)
        MainWindow.setCentralWidget(self.w_main)
        self.m_menu = QtWidgets.QMenuBar(MainWindow)
        self.m_menu.setGeometry(QtCore.QRect(0, 0, 580, 21))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(9)
        self.m_menu.setFont(font)
        self.m_menu.setObjectName("m_menu")
        MainWindow.setMenuBar(self.m_menu)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Spectra Lexer"))
        self.w_search_input.setPlaceholderText(_translate("MainWindow", "No dictionary."))
        self.w_display_text.setPlaceholderText(_translate("MainWindow", "Stroke a word to see its breakdown."))
        self.w_search_type.setText(_translate("MainWindow", "Stroke Search"))
        self.w_search_regex.setText(_translate("MainWindow", "Regex Search"))

from spectra_lexer.gui_qt.board.steno_board_widget import StenoBoardWidget
from spectra_lexer.gui_qt.search.search_list_widget import SearchListWidget
from spectra_lexer.gui_qt.text.text_graph_widget import TextGraphWidget
from . import resources_rc
