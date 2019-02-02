# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'propagateseeds.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(212, 162)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(-160, 120, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.groupBox_2 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_2.setGeometry(QtCore.QRect(20, 10, 171, 101))
        self.groupBox_2.setObjectName("groupBox_2")
        self.sbLast = QtWidgets.QSpinBox(self.groupBox_2)
        self.sbLast.setGeometry(QtCore.QRect(95, 70, 48, 24))
        self.sbLast.setObjectName("sbLast")
        self.sbFirst = QtWidgets.QSpinBox(self.groupBox_2)
        self.sbFirst.setGeometry(QtCore.QRect(95, 26, 48, 24))
        self.sbFirst.setObjectName("sbFirst")
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setGeometry(QtCore.QRect(34, 70, 53, 24))
        self.label_2.setObjectName("label_2")
        self.label = QtWidgets.QLabel(self.groupBox_2)
        self.label.setGeometry(QtCore.QRect(31, 26, 56, 24))
        self.label.setObjectName("label")

        self.retranslateUi(Dialog)
        self.buttonBox.rejected.connect(Dialog.reject)
        self.buttonBox.accepted.connect(Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Propagate seeds"))
        self.groupBox_2.setTitle(_translate("Dialog", "Slices to propagate"))
        self.label_2.setText(_translate("Dialog", "last slice"))
        self.label.setText(_translate("Dialog", "first slice"))

