# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt_resources/DumpToFilesDialog.ui',
# licensing of 'qt_resources/DumpToFilesDialog.ui' applies.
#
# Created: Thu Dec 27 16:24:07 2018
#      by: pyside2-uic  running on PySide2 5.12.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_DumpToFilesDialog(object):
    def setupUi(self, DumpToFilesDialog):
        DumpToFilesDialog.setObjectName("DumpToFilesDialog")
        DumpToFilesDialog.resize(400, 204)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DumpToFilesDialog.sizePolicy().hasHeightForWidth())
        DumpToFilesDialog.setSizePolicy(sizePolicy)
        self.formLayout = QtWidgets.QFormLayout(DumpToFilesDialog)
        self.formLayout.setObjectName("formLayout")
        self.destDirLabel = QtWidgets.QLabel(DumpToFilesDialog)
        self.destDirLabel.setObjectName("destDirLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.destDirLabel)
        self.widget = QtWidgets.QWidget(DumpToFilesDialog)
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.destDir = QtWidgets.QLineEdit(self.widget)
        self.destDir.setEnabled(False)
        self.destDir.setObjectName("destDir")
        self.horizontalLayout.addWidget(self.destDir)
        self.destDirSelect = QtWidgets.QToolButton(self.widget)
        self.destDirSelect.setObjectName("destDirSelect")
        self.horizontalLayout.addWidget(self.destDirSelect)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.widget)
        self.buttonBox = QtWidgets.QDialogButtonBox(DumpToFilesDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.buttonBox)
        self.pointInTime = TimePointEdit(DumpToFilesDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pointInTime.sizePolicy().hasHeightForWidth())
        self.pointInTime.setSizePolicy(sizePolicy)
        self.pointInTime.setObjectName("pointInTime")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.pointInTime)
        self.pointInTimeLabel = QtWidgets.QLabel(DumpToFilesDialog)
        self.pointInTimeLabel.setObjectName("pointInTimeLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.pointInTimeLabel)
        self.tagLabel = QtWidgets.QLabel(DumpToFilesDialog)
        self.tagLabel.setObjectName("tagLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.tagLabel)
        self.tag = QtWidgets.QComboBox(DumpToFilesDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tag.sizePolicy().hasHeightForWidth())
        self.tag.setSizePolicy(sizePolicy)
        self.tag.setObjectName("tag")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.tag)
        self.localTags = QtWidgets.QCheckBox(DumpToFilesDialog)
        self.localTags.setObjectName("localTags")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.localTags)
        self.overwrite = QtWidgets.QCheckBox(DumpToFilesDialog)
        self.overwrite.setChecked(True)
        self.overwrite.setObjectName("overwrite")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.overwrite)
        self.destDirLabel.setBuddy(self.destDirSelect)
        self.pointInTimeLabel.setBuddy(self.pointInTime)
        self.tagLabel.setBuddy(self.tag)

        self.retranslateUi(DumpToFilesDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), DumpToFilesDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), DumpToFilesDialog.reject)
        QtCore.QObject.connect(self.destDirSelect, QtCore.SIGNAL("clicked()"), DumpToFilesDialog.selectDirectory)
        QtCore.QObject.connect(self.localTags, QtCore.SIGNAL("toggled(bool)"), DumpToFilesDialog.showLocalTags)
        QtCore.QMetaObject.connectSlotsByName(DumpToFilesDialog)

    def retranslateUi(self, DumpToFilesDialog):
        DumpToFilesDialog.setWindowTitle(QtWidgets.QApplication.translate("DumpToFilesDialog", "Dump to files", None, -1))
        self.destDirLabel.setText(QtWidgets.QApplication.translate("DumpToFilesDialog", "Destination &directory", None, -1))
        self.destDirSelect.setText(QtWidgets.QApplication.translate("DumpToFilesDialog", "...", None, -1))
        self.pointInTimeLabel.setText(QtWidgets.QApplication.translate("DumpToFilesDialog", "Point &in time", None, -1))
        self.tagLabel.setText(QtWidgets.QApplication.translate("DumpToFilesDialog", "Tag to &use", None, -1))
        self.localTags.setText(QtWidgets.QApplication.translate("DumpToFilesDialog", "show &local tags", None, -1))
        self.overwrite.setToolTip(QtWidgets.QApplication.translate("DumpToFilesDialog", "Overwrite already existing files", None, -1))
        self.overwrite.setText(QtWidgets.QApplication.translate("DumpToFilesDialog", "&overwrite", None, -1))

from CondDBBrowser.CondDBUI.Browser.Widgets import TimePointEdit
