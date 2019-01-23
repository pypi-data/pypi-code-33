# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt_resources/NewDatabaseDialog.ui',
# licensing of 'qt_resources/NewDatabaseDialog.ui' applies.
#
# Created: Thu Dec 27 16:24:07 2018
#      by: pyside2-uic  running on PySide2 5.12.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_NewDatabaseDialog(object):
    def setupUi(self, NewDatabaseDialog):
        NewDatabaseDialog.setObjectName("NewDatabaseDialog")
        NewDatabaseDialog.resize(408, 130)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(NewDatabaseDialog.sizePolicy().hasHeightForWidth())
        NewDatabaseDialog.setSizePolicy(sizePolicy)
        self.formLayout = QtWidgets.QFormLayout(NewDatabaseDialog)
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.filenameLabel = QtWidgets.QLabel(NewDatabaseDialog)
        self.filenameLabel.setObjectName("filenameLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.filenameLabel)
        self.filenameWidget = QtWidgets.QWidget(NewDatabaseDialog)
        self.filenameWidget.setObjectName("filenameWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.filenameWidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.filenameEdit = QtWidgets.QLineEdit(self.filenameWidget)
        self.filenameEdit.setObjectName("filenameEdit")
        self.horizontalLayout.addWidget(self.filenameEdit)
        self.fileDialogButton = QtWidgets.QToolButton(self.filenameWidget)
        self.fileDialogButton.setObjectName("fileDialogButton")
        self.horizontalLayout.addWidget(self.fileDialogButton)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.filenameWidget)
        self.partitionLabel = QtWidgets.QLabel(NewDatabaseDialog)
        self.partitionLabel.setObjectName("partitionLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.partitionLabel)
        self.partitionComboBox = QtWidgets.QComboBox(NewDatabaseDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.partitionComboBox.sizePolicy().hasHeightForWidth())
        self.partitionComboBox.setSizePolicy(sizePolicy)
        self.partitionComboBox.setEditable(True)
        self.partitionComboBox.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.partitionComboBox.setObjectName("partitionComboBox")
        self.partitionComboBox.addItem("")
        self.partitionComboBox.addItem("")
        self.partitionComboBox.addItem("")
        self.partitionComboBox.addItem("")
        self.partitionComboBox.addItem("")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.partitionComboBox)
        self.buttonBox = QtWidgets.QDialogButtonBox(NewDatabaseDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.buttonBox)

        self.retranslateUi(NewDatabaseDialog)
        self.partitionComboBox.setCurrentIndex(1)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), NewDatabaseDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), NewDatabaseDialog.reject)
        QtCore.QObject.connect(self.fileDialogButton, QtCore.SIGNAL("clicked()"), NewDatabaseDialog.openFileDialog)
        QtCore.QObject.connect(self.filenameEdit, QtCore.SIGNAL("textChanged(QString)"), NewDatabaseDialog.checkValid)
        QtCore.QObject.connect(self.partitionComboBox, QtCore.SIGNAL("textChanged(QString)"), NewDatabaseDialog.checkValid)
        QtCore.QMetaObject.connectSlotsByName(NewDatabaseDialog)

    def retranslateUi(self, NewDatabaseDialog):
        NewDatabaseDialog.setWindowTitle(QtWidgets.QApplication.translate("NewDatabaseDialog", "Create New Database", None, -1))
        self.filenameLabel.setText(QtWidgets.QApplication.translate("NewDatabaseDialog", "File Name", None, -1))
        self.filenameEdit.setToolTip(QtWidgets.QApplication.translate("NewDatabaseDialog", "Path to the SQLite file", None, -1))
        self.fileDialogButton.setToolTip(QtWidgets.QApplication.translate("NewDatabaseDialog", "Open a dialog box to select a file", None, -1))
        self.fileDialogButton.setText(QtWidgets.QApplication.translate("NewDatabaseDialog", "...", None, -1))
        self.partitionLabel.setText(QtWidgets.QApplication.translate("NewDatabaseDialog", "Partition", None, -1))
        self.partitionComboBox.setToolTip(QtWidgets.QApplication.translate("NewDatabaseDialog", "Partition name: only uppercase letters or numbers", None, -1))
        self.partitionComboBox.setItemText(0, QtWidgets.QApplication.translate("NewDatabaseDialog", "DDDB", None, -1))
        self.partitionComboBox.setItemText(1, QtWidgets.QApplication.translate("NewDatabaseDialog", "LHCBCOND", None, -1))
        self.partitionComboBox.setItemText(2, QtWidgets.QApplication.translate("NewDatabaseDialog", "SIMCOND", None, -1))
        self.partitionComboBox.setItemText(3, QtWidgets.QApplication.translate("NewDatabaseDialog", "ONLINE", None, -1))
        self.partitionComboBox.setItemText(4, QtWidgets.QApplication.translate("NewDatabaseDialog", "CALIBOFF", None, -1))

