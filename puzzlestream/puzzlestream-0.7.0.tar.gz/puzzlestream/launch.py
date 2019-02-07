import ctypes
import sys
from multiprocessing import current_process
from os import path
from time import sleep

import matplotlib

matplotlib.use("Qt5Agg")

if current_process().name == "MainProcess":
    import sys
    from PyQt5 import QtCore, QtGui, QtWidgets


def main():
    """ Create Application and MainWindow. """
    global app, psMainWindow

    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
    QtWidgets.QApplication.setAttribute(
        QtCore.Qt.AA_CompressHighFrequencyEvents
    )
    app = QtWidgets.QApplication(sys.argv)
    currentDir = path.dirname(__file__)

    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "puzzlestream")
    desktopWidget = app.desktop()
    desktopGeometry = desktopWidget.screenGeometry()

    app.setWindowIcon(QtGui.QIcon(
        path.join(currentDir, "icons/Puzzlestream.png")))
    app.setApplicationName("Puzzlestream")
    app.setApplicationDisplayName("Puzzlestream")

    splash_pix = QtGui.QPixmap(
        path.join(currentDir, "icons/Puzzlestream.png"))

    splash_pix = splash_pix.scaled(
        0.5*splash_pix.width()*desktopGeometry.width()/1080,
        0.5*splash_pix.height()*desktopGeometry.width()/1080,
        transformMode=QtCore.Qt.SmoothTransformation)
    splash = QtWidgets.QSplashScreen(
        splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.setWindowFlags(
        QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
    splash.show()
    app.processEvents()
    from puzzlestream.ui.main import PSMainWindow
    psMainWindow = PSMainWindow()
    splash.finish(psMainWindow)
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
