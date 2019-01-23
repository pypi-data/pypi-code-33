# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt_resources/FindDialog.ui',
# licensing of 'qt_resources/FindDialog.ui' applies.
#
# Created: Thu Dec 27 16:24:07 2018
#      by: pyside2-uic  running on PySide2 5.12.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_FindDialog(object):
    def setupUi(self, FindDialog):
        FindDialog.setObjectName("FindDialog")
        FindDialog.resize(364, 156)
        self.horizontalLayout = QtWidgets.QHBoxLayout(FindDialog)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.criteria = QtWidgets.QWidget(FindDialog)
        self.criteria.setObjectName("criteria")
        self.formLayout = QtWidgets.QFormLayout(self.criteria)
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.textLabel = QtWidgets.QLabel(self.criteria)
        self.textLabel.setObjectName("textLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.textLabel)
        self.searchText = QtWidgets.QLineEdit(self.criteria)
        self.searchText.setObjectName("searchText")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.searchText)
        self.caseSensitive = QtWidgets.QCheckBox(self.criteria)
        self.caseSensitive.setObjectName("caseSensitive")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.caseSensitive)
        self.wholeWord = QtWidgets.QCheckBox(self.criteria)
        self.wholeWord.setObjectName("wholeWord")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.wholeWord)
        self.searchBackward = QtWidgets.QCheckBox(self.criteria)
        self.searchBackward.setObjectName("searchBackward")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.searchBackward)
        self.wrappedSearch = QtWidgets.QCheckBox(self.criteria)
        self.wrappedSearch.setObjectName("wrappedSearch")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.wrappedSearch)
        self.horizontalLayout.addWidget(self.criteria)
        self.buttons = QtWidgets.QWidget(FindDialog)
        self.buttons.setObjectName("buttons")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.buttons)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.findButton = QtWidgets.QPushButton(self.buttons)
        self.findButton.setObjectName("findButton")
        self.verticalLayout.addWidget(self.findButton)
        self.closeButton = QtWidgets.QPushButton(self.buttons)
        self.closeButton.setObjectName("closeButton")
        self.verticalLayout.addWidget(self.closeButton)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout.addWidget(self.buttons)
        self.textLabel.setBuddy(self.searchText)

        self.retranslateUi(FindDialog)
        QtCore.QObject.connect(self.closeButton, QtCore.SIGNAL("clicked()"), FindDialog.close)
        QtCore.QObject.connect(self.searchText, QtCore.SIGNAL("textChanged(QString)"), FindDialog.setText)
        QtCore.QObject.connect(self.caseSensitive, QtCore.SIGNAL("toggled(bool)"), FindDialog.setCaseSensitive)
        QtCore.QObject.connect(self.wholeWord, QtCore.SIGNAL("toggled(bool)"), FindDialog.setWholeWord)
        QtCore.QObject.connect(self.wrappedSearch, QtCore.SIGNAL("toggled(bool)"), FindDialog.setWrappedSearch)
        QtCore.QObject.connect(self.searchBackward, QtCore.SIGNAL("toggled(bool)"), FindDialog.setBackwardSearch)
        QtCore.QObject.connect(self.findButton, QtCore.SIGNAL("clicked()"), FindDialog.doFind)
        QtCore.QMetaObject.connectSlotsByName(FindDialog)

    def retranslateUi(self, FindDialog):
        FindDialog.setWindowTitle(QtWidgets.QApplication.translate("FindDialog", "Find", None, -1))
        self.textLabel.setText(QtWidgets.QApplication.translate("FindDialog", "Te&xt", None, -1))
        self.caseSensitive.setText(QtWidgets.QApplication.translate("FindDialog", "Match &case", None, -1))
        self.wholeWord.setText(QtWidgets.QApplication.translate("FindDialog", "&Whole word", None, -1))
        self.searchBackward.setText(QtWidgets.QApplication.translate("FindDialog", "Search &backward", None, -1))
        self.wrappedSearch.setText(QtWidgets.QApplication.translate("FindDialog", "W&rapped search", None, -1))
        self.findButton.setText(QtWidgets.QApplication.translate("FindDialog", "Find", None, -1))
        self.closeButton.setText(QtWidgets.QApplication.translate("FindDialog", "Close", None, -1))

