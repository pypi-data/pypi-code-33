# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\users\ricks\onedrive\development\tools\cgdat\cgdat\..\qt\splash_screen.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_splash_screen(object):
    def setupUi(self, splash_screen):
        splash_screen.setObjectName("splash_screen")
        splash_screen.resize(350, 199)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(splash_screen.sizePolicy().hasHeightForWidth())
        splash_screen.setSizePolicy(sizePolicy)
        splash_screen.setMinimumSize(QtCore.QSize(350, 150))
        splash_screen.setMaximumSize(QtCore.QSize(16777215, 1600000))
        self.verticalLayout = QtWidgets.QVBoxLayout(splash_screen)
        self.verticalLayout.setObjectName("verticalLayout")
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setSpacing(10)
        self.main_layout.setObjectName("main_layout")
        self.text_layout = QtWidgets.QVBoxLayout()
        self.text_layout.setObjectName("text_layout")
        self.label = QtWidgets.QLabel(splash_screen)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.text_layout.addWidget(self.label)
        self.main_layout.addLayout(self.text_layout)
        self.icon_layout = QtWidgets.QVBoxLayout()
        self.icon_layout.setContentsMargins(-1, 15, -1, -1)
        self.icon_layout.setObjectName("icon_layout")
        self.icon_holder = QtWidgets.QLabel(splash_screen)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.icon_holder.sizePolicy().hasHeightForWidth())
        self.icon_holder.setSizePolicy(sizePolicy)
        self.icon_holder.setMinimumSize(QtCore.QSize(100, 100))
        self.icon_holder.setMaximumSize(QtCore.QSize(100, 100))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.icon_holder.setFont(font)
        self.icon_holder.setText("")
        self.icon_holder.setPixmap(QtGui.QPixmap("../cgdat/static/media/CGDAT.png"))
        self.icon_holder.setScaledContents(True)
        self.icon_holder.setWordWrap(True)
        self.icon_holder.setObjectName("icon_holder")
        self.icon_layout.addWidget(self.icon_holder)
        spacerItem = QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.icon_layout.addItem(spacerItem)
        self.main_layout.addLayout(self.icon_layout)
        self.verticalLayout.addLayout(self.main_layout)
        self.progress_bar = QtWidgets.QProgressBar(splash_screen)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setProperty("value", 0)
        self.progress_bar.setAlignment(QtCore.Qt.AlignCenter)
        self.progress_bar.setInvertedAppearance(False)
        self.progress_bar.setObjectName("progress_bar")
        self.verticalLayout.addWidget(self.progress_bar)
        self.buttonBox = QtWidgets.QDialogButtonBox(splash_screen)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.buttonBox.setFont(font)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(splash_screen)
        self.buttonBox.accepted.connect(splash_screen.accept)
        self.buttonBox.rejected.connect(splash_screen.reject)
        QtCore.QMetaObject.connectSlotsByName(splash_screen)

    def retranslateUi(self, splash_screen):
        _translate = QtCore.QCoreApplication.translate
        splash_screen.setWindowTitle(_translate("splash_screen", "Please wait"))
        self.label.setText(_translate("splash_screen", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:600;\">CGDat (V2.3.0)</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">Welcome to the conditional game data analyse tool (CGDAT). Please wait as we load the application.</span></p></body></html>"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    splash_screen = QtWidgets.QDialog()
    ui = Ui_splash_screen()
    ui.setupUi(splash_screen)
    splash_screen.show()
    sys.exit(app.exec_())

