# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\repos\Jetperch\pyjoulescope_ui\joulescope_ui\save_data_dialog.ui',
# licensing of 'D:\repos\Jetperch\pyjoulescope_ui\joulescope_ui\save_data_dialog.ui' applies.
#
# Created: Sat Feb 16 11:08:35 2019
#      by: pyside2-uic  running on PySide2 5.12.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(644, 313)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(Form)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.formLayout = QtWidgets.QFormLayout(self.frame)
        self.formLayout.setObjectName("formLayout")
        self.filenameLabel = QtWidgets.QLabel(self.frame)
        self.filenameLabel.setObjectName("filenameLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.filenameLabel)
        self.filenameWidget = QtWidgets.QWidget(self.frame)
        self.filenameWidget.setObjectName("filenameWidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.filenameWidget)
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.filenameLineEdit = QtWidgets.QLineEdit(self.filenameWidget)
        self.filenameLineEdit.setObjectName("filenameLineEdit")
        self.horizontalLayout_2.addWidget(self.filenameLineEdit)
        self.filenameSelectButton = QtWidgets.QPushButton(self.filenameWidget)
        self.filenameSelectButton.setObjectName("filenameSelectButton")
        self.horizontalLayout_2.addWidget(self.filenameSelectButton)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.filenameWidget)
        self.contentsLabel = QtWidgets.QLabel(self.frame)
        self.contentsLabel.setObjectName("contentsLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.contentsLabel)
        self.contentsWidget = QtWidgets.QWidget(self.frame)
        self.contentsWidget.setObjectName("contentsWidget")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.contentsWidget)
        self.horizontalLayout_3.setContentsMargins(-1, 0, -1, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.contentsComboBox = QtWidgets.QComboBox(self.contentsWidget)
        self.contentsComboBox.setObjectName("contentsComboBox")
        self.contentsComboBox.addItem("")
        self.contentsComboBox.addItem("")
        self.horizontalLayout_3.addWidget(self.contentsComboBox)
        spacerItem = QtWidgets.QSpacerItem(358, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.contentsWidget)
        self.verticalLayout.addWidget(self.frame)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.closeWidget = QtWidgets.QWidget(Form)
        self.closeWidget.setObjectName("closeWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.closeWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.cancelButton = QtWidgets.QPushButton(self.closeWidget)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.saveButton = QtWidgets.QPushButton(self.closeWidget)
        self.saveButton.setEnabled(False)
        self.saveButton.setObjectName("saveButton")
        self.horizontalLayout.addWidget(self.saveButton)
        self.verticalLayout.addWidget(self.closeWidget)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtWidgets.QApplication.translate("Form", "Form", None, -1))
        self.filenameLabel.setText(QtWidgets.QApplication.translate("Form", "Filename", None, -1))
        self.filenameSelectButton.setText(QtWidgets.QApplication.translate("Form", "Choose", None, -1))
        self.contentsLabel.setText(QtWidgets.QApplication.translate("Form", "Contents", None, -1))
        self.contentsComboBox.setItemText(0, QtWidgets.QApplication.translate("Form", "View", None, -1))
        self.contentsComboBox.setItemText(1, QtWidgets.QApplication.translate("Form", "Buffer", None, -1))
        self.cancelButton.setText(QtWidgets.QApplication.translate("Form", "Cancel", None, -1))
        self.saveButton.setText(QtWidgets.QApplication.translate("Form", "Save", None, -1))

