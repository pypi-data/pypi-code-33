# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt_resources/SelectTagDialog.ui',
# licensing of 'qt_resources/SelectTagDialog.ui' applies.
#
# Created: Thu Dec 27 16:24:07 2018
#      by: pyside2-uic  running on PySide2 5.12.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_SelectTagDialog(object):
    def setupUi(self, SelectTagDialog):
        SelectTagDialog.setObjectName("SelectTagDialog")
        SelectTagDialog.resize(354, 84)
        self.formLayout = QtWidgets.QFormLayout(SelectTagDialog)
        self.formLayout.setObjectName("formLayout")
        self.tagLabel = QtWidgets.QLabel(SelectTagDialog)
        self.tagLabel.setObjectName("tagLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.tagLabel)
        self.tag = QtWidgets.QComboBox(SelectTagDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tag.sizePolicy().hasHeightForWidth())
        self.tag.setSizePolicy(sizePolicy)
        self.tag.setObjectName("tag")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.tag)
        self.buttonBox = QtWidgets.QDialogButtonBox(SelectTagDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.buttonBox)
        self.tagLabel.setBuddy(self.tag)

        self.retranslateUi(SelectTagDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), SelectTagDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), SelectTagDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SelectTagDialog)

    def retranslateUi(self, SelectTagDialog):
        SelectTagDialog.setWindowTitle(QtWidgets.QApplication.translate("SelectTagDialog", "Select a tag", None, -1))
        self.tagLabel.setText(QtWidgets.QApplication.translate("SelectTagDialog", "&Tag", None, -1))

