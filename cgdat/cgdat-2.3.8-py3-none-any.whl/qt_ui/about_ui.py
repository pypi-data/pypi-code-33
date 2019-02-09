# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\ricks\OneDrive\Development\Tools\cgdat\cgdat\..\qt\about.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_About(object):
    def setupUi(self, About):
        About.setObjectName("About")
        About.resize(464, 266)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(About.sizePolicy().hasHeightForWidth())
        About.setSizePolicy(sizePolicy)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(About)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label = QtWidgets.QLabel(About)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setStyleSheet("QLabel{background-color: white;padding: 5px 10px 15px 10px;}\n"
"QFrame{border: 1px solid rgb(179, 179, 179);border-radius: 3px;}\n"
"")
        self.label.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.label.setLineWidth(1)
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label.setWordWrap(True)
        self.label.setOpenExternalLinks(True)
        self.label.setObjectName("label")
        self.verticalLayout_4.addWidget(self.label)

        self.retranslateUi(About)
        QtCore.QMetaObject.connectSlotsByName(About)

    def retranslateUi(self, About):
        _translate = QtCore.QCoreApplication.translate
        About.setWindowTitle(_translate("About", "Dialog"))
        self.label.setText(_translate("About", "<html><head/><body><p><span style=\" text-decoration: underline;\">Description:</span></p><p>This tool was created to aid in a more streamlinedgame data analysation process. For questions or suggestions mail <a href=\"mailto:wbosman@fittestbody.nl\"><span style=\" text-decoration: underline; color:#0000ff;\">wbosman@fittestbody.nl</span></a>.</p><p><br/><span style=\" text-decoration: underline;\">Other info:</span></p><p><span style=\" font-weight:600;\">Repository: </span><a href=\"https://github.com/rickstaa/CGDAT\"><span style=\" text-decoration: underline; color:#0000ff;\">https://github.com/rickstaa/CGDAT</span></a></p><p><span style=\" font-weight:600;\">Created By: </span><a href=\"https://github.com/rickstaa\"><span style=\" text-decoration: underline; color:#0000ff;\">Rick Staa</span></a> &amp; Wesley Bosman<br/></p><p>Copyright 2018 <span style=\" font-weight:600;\">© </span><a href=\"https://github.com/rickstaa/\"><span style=\" text-decoration: underline; color:#0000ff;\">Rick Staa</span></a> &amp; Wesley Bosman<span style=\" font-weight:600;\"> (Licenced under a </span><a href=\"https://github.com/rickstaa/CGDAT/blob/master/LICENSE\"><span style=\" text-decoration: underline; color:#0000ff;\">GNU General Public License v3.0</span></a><span style=\" font-size:medium; font-weight:600;\">)</span></p></body></html>"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    About = QtWidgets.QDialog()
    ui = Ui_About()
    ui.setupUi(About)
    About.show()
    sys.exit(app.exec_())

