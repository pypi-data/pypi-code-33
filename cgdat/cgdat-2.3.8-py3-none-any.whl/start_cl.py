'''This script is used to starts the cgdat gui out of the command line'''

### Import modules ###
from PyQt5 import QtCore, QtGui, QtWidgets
import os, sys

### Import package modules ###
from cgdat import DataAnalyserGUI

### Get relative script path ###
DIRNAME = os.path.dirname(os.path.abspath(__file__))

##############################################################
#### Main execution function                              ####
##############################################################
def main():
    '''Main function that is executed when we use the :samp:`cgdat-gui` command. This function starts the
    cgdat gui window.'''

    ### Create QT app ###
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

    ### Create Main window ###
    ui = DataAnalyserGUI()
    ui.setupUi(MainWindow)

    ### Set icon ###
    CGDAT_icon = os.path.abspath(os.path.join(DIRNAME, "static/media/CGDAT.ico")).replace('\\','/')
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap(CGDAT_icon), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    MainWindow.setWindowIcon(icon)

    ### Show main window ###
    MainWindow.showMaximized()
    sys.exit(app.exec_())