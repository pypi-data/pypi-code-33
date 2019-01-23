# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt_resources/EditConditionPayloadDialog.ui',
# licensing of 'qt_resources/EditConditionPayloadDialog.ui' applies.
#
# Created: Thu Dec 27 16:24:07 2018
#      by: pyside2-uic  running on PySide2 5.12.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_EditConditionPayloadDialog(object):
    def setupUi(self, EditConditionPayloadDialog):
        EditConditionPayloadDialog.setObjectName("EditConditionPayloadDialog")
        EditConditionPayloadDialog.resize(709, 441)
        self.verticalLayout = QtWidgets.QVBoxLayout(EditConditionPayloadDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.fieldsLayout = QtWidgets.QWidget(EditConditionPayloadDialog)
        self.fieldsLayout.setObjectName("fieldsLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.fieldsLayout)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.fields = QtWidgets.QComboBox(self.fieldsLayout)
        self.fields.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.fields.setObjectName("fields")
        self.horizontalLayout_2.addWidget(self.fields)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addWidget(self.fieldsLayout)
        self.buttons = QtWidgets.QWidget(EditConditionPayloadDialog)
        self.buttons.setObjectName("buttons")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.buttons)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.importButton = QtWidgets.QToolButton(self.buttons)
        self.importButton.setObjectName("importButton")
        self.horizontalLayout.addWidget(self.importButton)
        self.exportButton = QtWidgets.QToolButton(self.buttons)
        self.exportButton.setObjectName("exportButton")
        self.horizontalLayout.addWidget(self.exportButton)
        self.externalEditorButton = QtWidgets.QToolButton(self.buttons)
        self.externalEditorButton.setObjectName("externalEditorButton")
        self.horizontalLayout.addWidget(self.externalEditorButton)
        self.insertConditionButton = QtWidgets.QToolButton(self.buttons)
        self.insertConditionButton.setObjectName("insertConditionButton")
        self.horizontalLayout.addWidget(self.insertConditionButton)
        self.insertAlignCondButton = QtWidgets.QToolButton(self.buttons)
        self.insertAlignCondButton.setObjectName("insertAlignCondButton")
        self.horizontalLayout.addWidget(self.insertAlignCondButton)
        self.insertParamButton = QtWidgets.QToolButton(self.buttons)
        self.insertParamButton.setObjectName("insertParamButton")
        self.horizontalLayout.addWidget(self.insertParamButton)
        self.insertParamVectorButton = QtWidgets.QToolButton(self.buttons)
        self.insertParamVectorButton.setObjectName("insertParamVectorButton")
        self.horizontalLayout.addWidget(self.insertParamVectorButton)
        self.verticalLayout.addWidget(self.buttons)
        self.editor = SearchableTextEdit(EditConditionPayloadDialog)
        self.editor.setObjectName("editor")
        self.verticalLayout.addWidget(self.editor)
        self.buttonBox = QtWidgets.QDialogButtonBox(EditConditionPayloadDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(EditConditionPayloadDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), EditConditionPayloadDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), EditConditionPayloadDialog.reject)
        QtCore.QObject.connect(self.importButton, QtCore.SIGNAL("clicked()"), EditConditionPayloadDialog.importFromFile)
        QtCore.QObject.connect(self.exportButton, QtCore.SIGNAL("clicked()"), EditConditionPayloadDialog.exportToFile)
        QtCore.QObject.connect(self.externalEditorButton, QtCore.SIGNAL("clicked()"), EditConditionPayloadDialog.openInExternalEditor)
        QtCore.QObject.connect(self.insertConditionButton, QtCore.SIGNAL("clicked()"), EditConditionPayloadDialog.insertCondition)
        QtCore.QObject.connect(self.insertAlignCondButton, QtCore.SIGNAL("clicked()"), EditConditionPayloadDialog.insertAlignmentCondition)
        QtCore.QObject.connect(self.insertParamButton, QtCore.SIGNAL("clicked()"), EditConditionPayloadDialog.insertParam)
        QtCore.QObject.connect(self.insertParamVectorButton, QtCore.SIGNAL("clicked()"), EditConditionPayloadDialog.insertParamVector)
        QtCore.QObject.connect(self.fields, QtCore.SIGNAL("currentIndexChanged(QString)"), EditConditionPayloadDialog.selectField)
        QtCore.QObject.connect(self.editor, QtCore.SIGNAL("textChanged()"), EditConditionPayloadDialog.updateData)
        QtCore.QMetaObject.connectSlotsByName(EditConditionPayloadDialog)

    def retranslateUi(self, EditConditionPayloadDialog):
        EditConditionPayloadDialog.setWindowTitle(QtWidgets.QApplication.translate("EditConditionPayloadDialog", "Edit Condition Payload", None, -1))
        self.importButton.setText(QtWidgets.QApplication.translate("EditConditionPayloadDialog", "&Import", None, -1))
        self.exportButton.setText(QtWidgets.QApplication.translate("EditConditionPayloadDialog", "E&xport", None, -1))
        self.externalEditorButton.setText(QtWidgets.QApplication.translate("EditConditionPayloadDialog", "&External editor", None, -1))
        self.insertConditionButton.setText(QtWidgets.QApplication.translate("EditConditionPayloadDialog", "<&condition>", None, -1))
        self.insertAlignCondButton.setText(QtWidgets.QApplication.translate("EditConditionPayloadDialog", "<&align.condition>", None, -1))
        self.insertParamButton.setText(QtWidgets.QApplication.translate("EditConditionPayloadDialog", "<&param>", None, -1))
        self.insertParamVectorButton.setText(QtWidgets.QApplication.translate("EditConditionPayloadDialog", "<param&Vector>", None, -1))

from CondDBBrowser.CondDBUI.Browser.Widgets import SearchableTextEdit
