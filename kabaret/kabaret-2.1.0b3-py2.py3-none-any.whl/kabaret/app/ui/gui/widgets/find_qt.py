from __future__ import print_function


raise Exception("OBSOLETE, use QtPy !")

print('Looking for Qt')
try:
    from PySide import QtGui, QtCore
    print ('-> PySide')
except ImportError:
    print (':/ PySide not found, trying PyQt4')
    from PyQt4 import QtGui, QtCore
    print ('-> PyQt4')

