# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/martinrusilowicz/work/apps/mhelper/mhelper_qt/designer/frm_generic_list_designer.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def __init__(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(881, 591)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.LBL_MAIN = QtWidgets.QLabel(Dialog)
        self.LBL_MAIN.setObjectName("LBL_MAIN")
        self.verticalLayout.addWidget(self.LBL_MAIN)
        self.TVW_MAIN = QtWidgets.QTreeWidget(Dialog)
        self.TVW_MAIN.setObjectName("TVW_MAIN")
        self.TVW_MAIN.headerItem().setText(0, "1")
        self.verticalLayout.addWidget(self.TVW_MAIN)
        self.BTNBOX_MAIN = QtWidgets.QDialogButtonBox(Dialog)
        self.BTNBOX_MAIN.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.BTNBOX_MAIN.setObjectName("BTNBOX_MAIN")
        self.verticalLayout.addWidget(self.BTNBOX_MAIN)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.LBL_MAIN.setText(_translate("Dialog", "TextLabel"))

