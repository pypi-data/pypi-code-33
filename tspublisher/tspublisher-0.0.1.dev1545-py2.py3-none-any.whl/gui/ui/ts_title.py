# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\andrej.perfilov\git\pipeline\lib\python\ts_publisher\src\publisher\gui\\resources\ts_title.ui'
#
# Created: Wed Jan 30 18:09:09 2019
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_ts_title(object):
    def setupUi(self, ts_title):
        ts_title.setObjectName("ts_title")
        ts_title.resize(543, 51)
        self.horizontalLayout = QtGui.QHBoxLayout(ts_title)
        self.horizontalLayout.setSpacing(12)
        self.horizontalLayout.setContentsMargins(5, -1, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.icon = QtGui.QLabel(ts_title)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.icon.sizePolicy().hasHeightForWidth())
        self.icon.setSizePolicy(sizePolicy)
        self.icon.setMinimumSize(QtCore.QSize(32, 32))
        self.icon.setText("")
        self.icon.setPixmap(QtGui.QPixmap(":/icons/icons/TSIcon.png"))
        self.icon.setObjectName("icon")
        self.horizontalLayout.addWidget(self.icon)
        self.label = QtGui.QLabel(ts_title)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)

        self.retranslateUi(ts_title)
        QtCore.QMetaObject.connectSlotsByName(ts_title)

    def retranslateUi(self, ts_title):
        ts_title.setWindowTitle(QtGui.QApplication.translate("ts_title", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ts_title", "Title", None, QtGui.QApplication.UnicodeUTF8))

import icons_rc
