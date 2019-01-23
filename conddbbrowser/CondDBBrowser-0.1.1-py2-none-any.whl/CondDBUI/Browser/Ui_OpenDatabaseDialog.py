# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt_resources/OpenDatabaseDialog.ui',
# licensing of 'qt_resources/OpenDatabaseDialog.ui' applies.
#
# Created: Thu Dec 27 16:24:07 2018
#      by: pyside2-uic  running on PySide2 5.12.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_OpenDatabaseDialog(object):
    def setupUi(self, OpenDatabaseDialog):
        OpenDatabaseDialog.setObjectName("OpenDatabaseDialog")
        OpenDatabaseDialog.resize(400, 172)
        self.verticalLayout = QtWidgets.QVBoxLayout(OpenDatabaseDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(OpenDatabaseDialog)
        self.tabWidget.setObjectName("tabWidget")
        self.sqliteTab = QtWidgets.QWidget()
        self.sqliteTab.setObjectName("sqliteTab")
        self.formLayout = QtWidgets.QFormLayout(self.sqliteTab)
        self.formLayout.setObjectName("formLayout")
        self.filenameLabel = QtWidgets.QLabel(self.sqliteTab)
        self.filenameLabel.setObjectName("filenameLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.filenameLabel)
        self.filenameWidget = QtWidgets.QWidget(self.sqliteTab)
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
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.filenameWidget)
        self.partitionLabel = QtWidgets.QLabel(self.sqliteTab)
        self.partitionLabel.setObjectName("partitionLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.partitionLabel)
        self.partitionComboBox = QtWidgets.QComboBox(self.sqliteTab)
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
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.partitionComboBox)
        self.tabWidget.addTab(self.sqliteTab, "")
        self.advancedTab = QtWidgets.QWidget()
        self.advancedTab.setObjectName("advancedTab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.advancedTab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.connStringLabel = QtWidgets.QLabel(self.advancedTab)
        self.connStringLabel.setObjectName("connStringLabel")
        self.verticalLayout_2.addWidget(self.connStringLabel)
        self.connStringEdit = QtWidgets.QLineEdit(self.advancedTab)
        self.connStringEdit.setObjectName("connStringEdit")
        self.verticalLayout_2.addWidget(self.connStringEdit)
        self.tabWidget.addTab(self.advancedTab, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.widget = QtWidgets.QWidget(OpenDatabaseDialog)
        self.widget.setObjectName("widget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.readOnlyCheckBox = QtWidgets.QCheckBox(self.widget)
        self.readOnlyCheckBox.setChecked(True)
        self.readOnlyCheckBox.setObjectName("readOnlyCheckBox")
        self.horizontalLayout_2.addWidget(self.readOnlyCheckBox)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.widget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout_2.addWidget(self.buttonBox)
        self.verticalLayout.addWidget(self.widget)

        self.retranslateUi(OpenDatabaseDialog)
        self.tabWidget.setCurrentIndex(0)
        self.partitionComboBox.setCurrentIndex(1)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), OpenDatabaseDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), OpenDatabaseDialog.reject)
        QtCore.QObject.connect(self.fileDialogButton, QtCore.SIGNAL("clicked()"), OpenDatabaseDialog.openFileDialog)
        QtCore.QObject.connect(self.filenameEdit, QtCore.SIGNAL("textChanged(QString)"), OpenDatabaseDialog.checkValid)
        QtCore.QObject.connect(self.partitionComboBox, QtCore.SIGNAL("editTextChanged(QString)"), OpenDatabaseDialog.checkValid)
        QtCore.QObject.connect(self.connStringEdit, QtCore.SIGNAL("textChanged(QString)"), OpenDatabaseDialog.checkValid)
        QtCore.QMetaObject.connectSlotsByName(OpenDatabaseDialog)

    def retranslateUi(self, OpenDatabaseDialog):
        OpenDatabaseDialog.setWindowTitle(QtWidgets.QApplication.translate("OpenDatabaseDialog", "Open Database", None, -1))
        self.filenameLabel.setText(QtWidgets.QApplication.translate("OpenDatabaseDialog", "File Name", None, -1))
        self.filenameEdit.setToolTip(QtWidgets.QApplication.translate("OpenDatabaseDialog", "Path to the SQLite file", None, -1))
        self.fileDialogButton.setToolTip(QtWidgets.QApplication.translate("OpenDatabaseDialog", "Open a dialog box to select a file", None, -1))
        self.fileDialogButton.setText(QtWidgets.QApplication.translate("OpenDatabaseDialog", "...", None, -1))
        self.partitionLabel.setText(QtWidgets.QApplication.translate("OpenDatabaseDialog", "Partition", None, -1))
        self.partitionComboBox.setToolTip(QtWidgets.QApplication.translate("OpenDatabaseDialog", "Partition name: only uppercase letters or numbers", None, -1))
        self.partitionComboBox.setItemText(0, QtWidgets.QApplication.translate("OpenDatabaseDialog", "DDDB", None, -1))
        self.partitionComboBox.setItemText(1, QtWidgets.QApplication.translate("OpenDatabaseDialog", "LHCBCOND", None, -1))
        self.partitionComboBox.setItemText(2, QtWidgets.QApplication.translate("OpenDatabaseDialog", "SIMCOND", None, -1))
        self.partitionComboBox.setItemText(3, QtWidgets.QApplication.translate("OpenDatabaseDialog", "ONLINE", None, -1))
        self.partitionComboBox.setItemText(4, QtWidgets.QApplication.translate("OpenDatabaseDialog", "CALIBOFF", None, -1))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.sqliteTab), QtWidgets.QApplication.translate("OpenDatabaseDialog", "SQLite file", None, -1))
        self.connStringLabel.setText(QtWidgets.QApplication.translate("OpenDatabaseDialog", "Connection string", None, -1))
        self.connStringEdit.setToolTip(QtWidgets.QApplication.translate("OpenDatabaseDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">COOL connection string.<br />E.g.:</p>\n"
"<ul style=\"-qt-list-indent: 1;\"><li style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">CondDB/LHCBCOND</li>\n"
"<li style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">sqlite_file:/path/to/file/DDDB.db/DDDB</li></ul></body></html>", None, -1))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.advancedTab), QtWidgets.QApplication.translate("OpenDatabaseDialog", "Advanced", None, -1))
        self.readOnlyCheckBox.setToolTip(QtWidgets.QApplication.translate("OpenDatabaseDialog", "Uncheck if the database have to be opend in read/write mode", None, -1))
        self.readOnlyCheckBox.setText(QtWidgets.QApplication.translate("OpenDatabaseDialog", "Read Only", None, -1))

