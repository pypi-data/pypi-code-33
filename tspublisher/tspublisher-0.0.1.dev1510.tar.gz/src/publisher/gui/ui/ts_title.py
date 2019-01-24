# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ts_title.ui'
#
# Created: Tue Aug 14 11:24:16 2018
#
# WARNING! All changes made in this file will be lost!

from Qt import QtWidgets, QtCore, QtGui


class Ui_ts_title(object):
    def setupUi(self, ts_title):
        ts_title.setObjectName("ts_title")
        ts_title.resize(543, 51)
        self.horizontalLayout = QtWidgets.QHBoxLayout(ts_title)
        self.horizontalLayout.setSpacing(12)
        self.horizontalLayout.setContentsMargins(5, -1, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.icon = QtWidgets.QLabel(ts_title)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.icon.sizePolicy().hasHeightForWidth())
        self.icon.setSizePolicy(sizePolicy)
        self.icon.setMinimumSize(QtCore.QSize(32, 32))
        self.icon.setText("")
        self.icon.setPixmap(QtGui.QPixmap(":/icons/icons/TSIcon.png"))
        self.icon.setObjectName("icon")
        self.horizontalLayout.addWidget(self.icon)
        self.label = QtWidgets.QLabel(ts_title)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)

        self.retranslateUi(ts_title)
        QtCore.QMetaObject.connectSlotsByName(ts_title)

    def retranslateUi(self, ts_title):
        ts_title.setWindowTitle(QtWidgets.QApplication.translate("ts_title", "Form", None))
        self.label.setText(QtWidgets.QApplication.translate("ts_title", "Title", None))

from . import icons_rc
