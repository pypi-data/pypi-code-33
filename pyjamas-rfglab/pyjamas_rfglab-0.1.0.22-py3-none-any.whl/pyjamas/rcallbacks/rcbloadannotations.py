"""
    PyJAMAS is Just A More Awesome Siesta
    Copyright (C) 2018  Rodrigo Fernandez-Gonzalez (rodrigo.fernandez.gonzalez@utoronto.ca)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import gzip
import os
import pickle

from PyQt5 import QtCore, QtGui, QtWidgets

import pyjamas.pjscore as pjscore
from .rcallback import RCallback


class RCBLoadAnnotations(RCallback):
    def cbLoadAnnotations(self, filename: str = None):  # Handle IO errors
        # Get file name.
        if filename is None or filename is False or filename == '': # When the menu option is clicked on, for some reason that I do not understand, the function is called with filename = False, which causes a bunch of problems.
            fname = QtWidgets.QFileDialog.getOpenFileName(None, 'Load classifier ...', self.pjs.cwd,
                                                          filter='PyJAMAS data (*' + pjscore.PyJAMAS.data_extension + ')')  # fname[0] is the full filename, fname[1] is the filter used.
            filename = fname[0]
            if filename == '':
                return False

        # Open file name and read annotations.
        fh = None

        try:
            fh = gzip.open(filename, "rb")
            self.pjs.fiducials = pickle.load(fh)
            polyline_list = pickle.load(fh)

        except (IOError, OSError) as ex:
            if fh is not None:
                fh.close()

            print(ex)

        self.pjs.polylines = [[] for i in range(self.pjs.n_frames)]
        for i, theframepolylines in enumerate(polyline_list):
            for j, thepolyline in enumerate(theframepolylines):
                if thepolyline != [[]]:
                    self.pjs.polylines[i].append(QtGui.QPolygonF())
                    for thepoint in thepolyline:
                        self.pjs.polylines[i][-1].append(QtCore.QPointF(thepoint[0], thepoint[1]))

        self.pjs.repaint()

        # Modify current path.
        self.pjs.cwd = filename[0:filename.rfind(os.sep)]

        return True

