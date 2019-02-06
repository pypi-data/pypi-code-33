# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\users\ricks\onedrive\development\tools\cgdat\cgdat\..\qt\import_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ImportDialog(object):
    def setupUi(self, ImportDialog):
        ImportDialog.setObjectName("ImportDialog")
        ImportDialog.resize(350, 150)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ImportDialog.sizePolicy().hasHeightForWidth())
        ImportDialog.setSizePolicy(sizePolicy)
        ImportDialog.setMinimumSize(QtCore.QSize(350, 150))
        ImportDialog.setMaximumSize(QtCore.QSize(350, 150))
        self.gridLayout = QtWidgets.QGridLayout(ImportDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.progress_bar = QtWidgets.QProgressBar(ImportDialog)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setProperty("value", 0)
        self.progress_bar.setAlignment(QtCore.Qt.AlignCenter)
        self.progress_bar.setInvertedAppearance(False)
        self.progress_bar.setObjectName("progress_bar")
        self.gridLayout.addWidget(self.progress_bar, 1, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(ImportDialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.buttonBox.setFont(font)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 1)
        self.progress_header = QtWidgets.QLabel(ImportDialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.progress_header.setFont(font)
        self.progress_header.setWordWrap(True)
        self.progress_header.setObjectName("progress_header")
        self.gridLayout.addWidget(self.progress_header, 0, 0, 1, 1)

        self.retranslateUi(ImportDialog)
        self.buttonBox.accepted.connect(ImportDialog.accept)
        self.buttonBox.rejected.connect(ImportDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ImportDialog)

    def retranslateUi(self, ImportDialog):
        _translate = QtCore.QCoreApplication.translate
        ImportDialog.setWindowTitle(_translate("ImportDialog", "Please wait"))
        self.progress_header.setText(_translate("ImportDialog", "<html><head/><body><p><span style=\" font-size:12pt;\">The data file is being imported. Please wait until the import is ready or cancel the import by using the cancel button below.</span></p></body></html>"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ImportDialog = QtWidgets.QDialog()
    ui = Ui_ImportDialog()
    ui.setupUi(ImportDialog)
    ImportDialog.show()
    sys.exit(app.exec_())

