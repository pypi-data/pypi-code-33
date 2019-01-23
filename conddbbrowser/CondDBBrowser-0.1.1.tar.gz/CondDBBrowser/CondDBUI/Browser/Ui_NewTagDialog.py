# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt_resources/NewTagDialog.ui',
# licensing of 'qt_resources/NewTagDialog.ui' applies.
#
# Created: Thu Dec 27 16:24:07 2018
#      by: pyside2-uic  running on PySide2 5.12.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_NewTagDialog(object):
    def setupUi(self, NewTagDialog):
        NewTagDialog.setObjectName("NewTagDialog")
        NewTagDialog.resize(400, 340)
        self.formLayout = QtWidgets.QFormLayout(NewTagDialog)
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.nodeLabel = QtWidgets.QLabel(NewTagDialog)
        self.nodeLabel.setObjectName("nodeLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.nodeLabel)
        self.node = QtWidgets.QLineEdit(NewTagDialog)
        self.node.setReadOnly(True)
        self.node.setObjectName("node")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.node)
        self.tagLabel = QtWidgets.QLabel(NewTagDialog)
        self.tagLabel.setObjectName("tagLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.tagLabel)
        self.tag = QtWidgets.QLineEdit(NewTagDialog)
        self.tag.setObjectName("tag")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.tag)
        self.childTagsLabel = QtWidgets.QLabel(NewTagDialog)
        self.childTagsLabel.setObjectName("childTagsLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.childTagsLabel)
        self.childTags = QtWidgets.QTableView(NewTagDialog)
        self.childTags.setObjectName("childTags")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.childTags)
        self.fillChildTagsBtn = QtWidgets.QPushButton(NewTagDialog)
        self.fillChildTagsBtn.setObjectName("fillChildTagsBtn")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.fillChildTagsBtn)
        self.buttonBox = QtWidgets.QDialogButtonBox(NewTagDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.buttonBox)
        self.nodeLabel.setBuddy(self.node)
        self.tagLabel.setBuddy(self.tag)
        self.childTagsLabel.setBuddy(self.childTags)

        self.retranslateUi(NewTagDialog)
        QtCore.QObject.connect(self.tag, QtCore.SIGNAL("textChanged(QString)"), NewTagDialog.checkValidData)
        QtCore.QObject.connect(self.fillChildTagsBtn, QtCore.SIGNAL("clicked()"), NewTagDialog.fillChildTags)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), NewTagDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), NewTagDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(NewTagDialog)

    def retranslateUi(self, NewTagDialog):
        NewTagDialog.setWindowTitle(QtWidgets.QApplication.translate("NewTagDialog", "New tag", None, -1))
        self.nodeLabel.setText(QtWidgets.QApplication.translate("NewTagDialog", "&Node", None, -1))
        self.tagLabel.setText(QtWidgets.QApplication.translate("NewTagDialog", "New &tag name", None, -1))
        self.childTagsLabel.setText(QtWidgets.QApplication.translate("NewTagDialog", "&Child tags", None, -1))
        self.fillChildTagsBtn.setText(QtWidgets.QApplication.translate("NewTagDialog", "&Fill from an existing tag", None, -1))

