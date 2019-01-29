# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/martinrusilowicz/work/apps/intermake/intermake_qt/forms/designer/frm_arguments_designer.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def __init__(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(917, 747)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.LBL_APP_NAME = QtWidgets.QLabel(Dialog)
        self.LBL_APP_NAME.setStyleSheet("color: gray;\n"
"font-size: 8px;\n"
"font-variant: small-caps;")
        self.LBL_APP_NAME.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.LBL_APP_NAME.setObjectName("LBL_APP_NAME")
        self.verticalLayout.addWidget(self.LBL_APP_NAME)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(12, 0, 12, 12)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.LBL_PLUGIN_NAME = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LBL_PLUGIN_NAME.sizePolicy().hasHeightForWidth())
        self.LBL_PLUGIN_NAME.setSizePolicy(sizePolicy)
        self.LBL_PLUGIN_NAME.setObjectName("LBL_PLUGIN_NAME")
        self.horizontalLayout_2.addWidget(self.LBL_PLUGIN_NAME)
        self.BTN_HELP_MAIN = QtWidgets.QPushButton(Dialog)
        self.BTN_HELP_MAIN.setObjectName("BTN_HELP_MAIN")
        self.horizontalLayout_2.addWidget(self.BTN_HELP_MAIN)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.scrollArea = QtWidgets.QScrollArea(Dialog)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.GRID_ARGS_OWNER = QtWidgets.QWidget()
        self.GRID_ARGS_OWNER.setGeometry(QtCore.QRect(0, 0, 893, 634))
        self.GRID_ARGS_OWNER.setObjectName("GRID_ARGS_OWNER")
        self.GRID_ARGS = QtWidgets.QGridLayout(self.GRID_ARGS_OWNER)
        self.GRID_ARGS.setContentsMargins(0, 8, 0, 8)
        self.GRID_ARGS.setObjectName("GRID_ARGS")
        self.scrollArea.setWidget(self.GRID_ARGS_OWNER)
        self.verticalLayout_2.addWidget(self.scrollArea)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.BTN_OPTIONS = QtWidgets.QToolButton(Dialog)
        self.BTN_OPTIONS.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/intermake/settings.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.BTN_OPTIONS.setIcon(icon)
        self.BTN_OPTIONS.setAutoRaise(True)
        self.BTN_OPTIONS.setObjectName("BTN_OPTIONS")
        self.horizontalLayout.addWidget(self.BTN_OPTIONS)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/intermake/execute.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton.setIcon(icon1)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout.addLayout(self.verticalLayout_2)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.LBL_APP_NAME.setText(_translate("Dialog", "parameter query"))
        self.LBL_PLUGIN_NAME.setText(_translate("Dialog", "TextLabel"))
        self.LBL_PLUGIN_NAME.setProperty("style", _translate("Dialog", "title"))
        self.BTN_HELP_MAIN.setText(_translate("Dialog", "..."))
        self.pushButton.setText(_translate("Dialog", "Execute"))


