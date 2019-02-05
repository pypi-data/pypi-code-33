# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/martinrusilowicz/work/apps/intermake/intermake_qt/forms/designer/frm_maintenance_designer.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def __init__(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(715, 469)
        Dialog.setSizeGripEnabled(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.PAGER_MAIN = QtWidgets.QStackedWidget(Dialog)
        self.PAGER_MAIN.setObjectName("PAGER_MAIN")
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.page_2)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.LBL_PLEASE_WAIT = QtWidgets.QLabel(self.page_2)
        self.LBL_PLEASE_WAIT.setStyleSheet("background: gray;\n"
"color: white;\n"
"font-size: 24px;")
        self.LBL_PLEASE_WAIT.setAlignment(QtCore.Qt.AlignCenter)
        self.LBL_PLEASE_WAIT.setObjectName("LBL_PLEASE_WAIT")
        self.gridLayout_2.addWidget(self.LBL_PLEASE_WAIT, 0, 0, 1, 1)
        self.PAGER_MAIN.addWidget(self.page_2)
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.page)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.TXT_MESSAGES = QtWidgets.QTextEdit(self.page)
        font = QtGui.QFont()
        font.setFamily("Comic Sans MS")
        self.TXT_MESSAGES.setFont(font)
        self.TXT_MESSAGES.setStyleSheet("")
        self.TXT_MESSAGES.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.TXT_MESSAGES.setReadOnly(True)
        self.TXT_MESSAGES.setObjectName("TXT_MESSAGES")
        self.verticalLayout_2.addWidget(self.TXT_MESSAGES)
        self.frame = QtWidgets.QFrame(self.page)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setContentsMargins(-1, 0, -1, 0)
        self.horizontalLayout.setSpacing(8)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.BTN_OPTIONS = QtWidgets.QPushButton(self.frame)
        self.BTN_OPTIONS.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/intermake/settings.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.BTN_OPTIONS.setIcon(icon)
        self.BTN_OPTIONS.setObjectName("BTN_OPTIONS")
        self.horizontalLayout.addWidget(self.BTN_OPTIONS)
        self.BTN_CANCEL = QtWidgets.QPushButton(self.frame)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/images/resource_files/checkno.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.BTN_CANCEL.setIcon(icon1)
        self.BTN_CANCEL.setAutoDefault(False)
        self.BTN_CANCEL.setObjectName("BTN_CANCEL")
        self.horizontalLayout.addWidget(self.BTN_CANCEL)
        spacerItem = QtWidgets.QSpacerItem(40, 16, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.BTN_CLOSE = QtWidgets.QPushButton(self.frame)
        self.BTN_CLOSE.setStyleSheet("")
        self.BTN_CLOSE.setAutoDefault(False)
        self.BTN_CLOSE.setDefault(True)
        self.BTN_CLOSE.setObjectName("BTN_CLOSE")
        self.horizontalLayout.addWidget(self.BTN_CLOSE)
        self.verticalLayout_2.addWidget(self.frame)
        self.PAGER_MAIN.addWidget(self.page)
        self.verticalLayout.addWidget(self.PAGER_MAIN)

        self.retranslateUi(Dialog)
        self.PAGER_MAIN.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        self.LBL_PLEASE_WAIT.setText(_translate("Dialog", "<html>\n"
"<body>\n"
"\n"
"<img src=\":/intermake/wait.svg\" width=\"32\" height=\"32\" /><br/>\n"
"PLEASE WAIT\n"
"\n"
"</body>\n"
"</html>"))
        self.BTN_CANCEL.setText(_translate("Dialog", "Cancel"))
        self.BTN_CLOSE.setText(_translate("Dialog", "Close"))


