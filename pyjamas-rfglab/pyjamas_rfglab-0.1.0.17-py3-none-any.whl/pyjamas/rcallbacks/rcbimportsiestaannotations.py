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

from .rcallback import RCallback
from PyQt5 import QtWidgets
import os
import scipy.io


class RCBImportSIESTAAnnotations(RCallback):
    def cbImportSIESTAAnnotations(self, filename=''):
        # Get file name.
        if filename == '' or filename is False: # When the menu option is clicked on, for some reason that I do not understand, the function is called with filename = False, which causes a bunch of problems.
            fname = QtWidgets.QFileDialog.getOpenFileName(None, 'Import SIESTA annotations ...', self.pjs.cwd,
                                                          filter='SIESTA annotations (*.mat)')  # fname[0] is the full filename, fname[1] is the filter used.
            filename = fname[0]
            if filename == '':
                return False

        # Open file name and read annotations.
        try:
            matlabVars = scipy.io.loadmat(filename, struct_as_record=False)
        except (IOError, OSError) as ex:
            print(ex)
            return False

        ud = matlabVars['ud'][0][0]

        rfidu = ud.rfiducials
        rpoly = ud.rpolygons

        fidu_shape = rfidu.shape

        self.pjs.fiducials = [[] for i in range(self.pjs.n_frames)]

        for z in range(fidu_shape[2]):
            for row in range(fidu_shape[0]):
                if rfidu[row, 0, z] >= 0:
                    #  self.pjs.fiducials[z].append(rfidu[row, 0:2, z].tolist())
                    self.pjs.addFiducial(int(rfidu[row, 0, z]), int(rfidu[row, 1, z]), z)  # Conversion to int here is critical: otherwise, testing for coordinate equality is a mess.

        poly_shape = rpoly.shape
        self.pjs.polylines = [[] for i in range(self.pjs.n_frames)]

        for z in range(poly_shape[2]):
            for row in range(poly_shape[0]):
                thepolyline = rpoly[row, 0, z].tolist()
                if thepolyline != []:
                    self.pjs.addPolyline(thepolyline, z)

                    #self.pjs.polylines[z].append(QtGui.QPolygonF())
                    #for k, thepoint in enumerate(thepolyline):
                    #    self.pjs.polylines[z][-1].append(QtCore.QPointF(thepoint[0], thepoint[1]))

        self.pjs.repaint()

        # Modify current path.
        self.pjs.cwd = filename[0:filename.rfind(os.sep)]

        return True

