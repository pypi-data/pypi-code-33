# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'nonmax_suppr.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(304, 234)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(-60, 193, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.max_num_objects = QtWidgets.QDial(Dialog)
        self.max_num_objects.setGeometry(QtCore.QRect(220, 4, 50, 64))
        self.max_num_objects.setObjectName("max_num_objects_dial")
        self.prob_threshold = QtWidgets.QDial(Dialog)
        self.prob_threshold.setGeometry(QtCore.QRect(220, 64, 50, 64))
        self.prob_threshold.setObjectName("prob_threshold")
        self.iou_threshold = QtWidgets.QDial(Dialog)
        self.iou_threshold.setGeometry(QtCore.QRect(220, 124, 50, 64))
        self.iou_threshold.setObjectName("iou_threshold")
        self.label_8 = QtWidgets.QLabel(Dialog)
        self.label_8.setGeometry(QtCore.QRect(33, 24, 181, 24))
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(Dialog)
        self.label_9.setGeometry(QtCore.QRect(33, 84, 181, 24))
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(Dialog)
        self.label_10.setGeometry(QtCore.QRect(33, 144, 181, 24))
        self.label_10.setObjectName("label_10")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Non-maximum suppression"))
        self.label_8.setText(_translate("Dialog", "maximum number of objects"))
        self.label_9.setText(_translate("Dialog", "minimum object probability"))
        self.label_10.setText(_translate("Dialog", "minimum intersection/union"))

