# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\users\ricks\onedrive\development\tools\cgdat\cgdat\..\qt\progress_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ProgressDialog(object):
    def setupUi(self, ProgressDialog):
        ProgressDialog.setObjectName("ProgressDialog")
        ProgressDialog.resize(475, 338)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ProgressDialog.sizePolicy().hasHeightForWidth())
        ProgressDialog.setSizePolicy(sizePolicy)
        ProgressDialog.setMinimumSize(QtCore.QSize(475, 338))
        ProgressDialog.setMaximumSize(QtCore.QSize(475, 338))
        self.gridLayout = QtWidgets.QGridLayout(ProgressDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.progress_console = QtWidgets.QTextEdit(ProgressDialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.progress_console.setFont(font)
        self.progress_console.setReadOnly(True)
        self.progress_console.setObjectName("progress_console")
        self.gridLayout.addWidget(self.progress_console, 3, 0, 1, 1)
        self.progress_bar = QtWidgets.QProgressBar(ProgressDialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.progress_bar.setFont(font)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setProperty("value", 0)
        self.progress_bar.setInvertedAppearance(False)
        self.progress_bar.setObjectName("progress_bar")
        self.gridLayout.addWidget(self.progress_bar, 5, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(ProgressDialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.buttonBox.setFont(font)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 9, 0, 1, 1)
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setObjectName("header_layout")
        self.progress_header = QtWidgets.QLabel(ProgressDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progress_header.sizePolicy().hasHeightForWidth())
        self.progress_header.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.progress_header.setFont(font)
        self.progress_header.setWordWrap(True)
        self.progress_header.setObjectName("progress_header")
        self.header_layout.addWidget(self.progress_header)
        self.loader_gif = QtWidgets.QLabel(ProgressDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.loader_gif.sizePolicy().hasHeightForWidth())
        self.loader_gif.setSizePolicy(sizePolicy)
        self.loader_gif.setMinimumSize(QtCore.QSize(45, 45))
        self.loader_gif.setMaximumSize(QtCore.QSize(45, 45))
        self.loader_gif.setText("")
        self.loader_gif.setScaledContents(True)
        self.loader_gif.setObjectName("loader_gif")
        self.header_layout.addWidget(self.loader_gif)
        self.gridLayout.addLayout(self.header_layout, 0, 0, 1, 1)

        self.retranslateUi(ProgressDialog)
        self.buttonBox.accepted.connect(ProgressDialog.accept)
        self.buttonBox.rejected.connect(ProgressDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ProgressDialog)

    def retranslateUi(self, ProgressDialog):
        _translate = QtCore.QCoreApplication.translate
        ProgressDialog.setWindowTitle(_translate("ProgressDialog", "Data analysis progress dialog"))
        self.progress_console.setHtml(_translate("ProgressDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8.25pt;\"><br /></p></body></html>"))
        self.progress_header.setText(_translate("ProgressDialog", "<html><head/><body><p>Performing data analysis...</p></body></html>"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ProgressDialog = QtWidgets.QDialog()
    ui = Ui_ProgressDialog()
    ui.setupUi(ProgressDialog)
    ProgressDialog.show()
    sys.exit(app.exec_())

