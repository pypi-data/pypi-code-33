from PyQt5 import QtCore, QtWidgets

class ProgressBar(object):
    def __init__(self, Dialog, max_value: int, title: str, message: str):
        super().__init__()

        Dialog.setObjectName("Dialog")
        Dialog.resize(274, 63)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 60, 16))
        self.label.setObjectName("label")
        self.progressBar = QtWidgets.QProgressBar(Dialog)
        self.progressBar.setGeometry(QtCore.QRect(10, 30, 251, 23))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setMaximum(max_value)
        self.progressBar.setObjectName("progressBar")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog, title: str, message: str):
        _translate = QtCore.QCoreApplication.translate
        if title is not None and title is not False:
            Dialog.setWindowTitle(_translate("Dialog", title))
        if message is not None and message is not False:
            self.label.setText(_translate("Dialog", message))

    def update_status(self, value: int, message: str = None) -> bool:
        self.progressBar.setValue(value)

        if message is not None and message is not False:
            self.label.setText(message)

        if value == self.progressBar.maximum():
            pass

