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

import os

import numpy
from PyQt5 import QtWidgets

import pyjamas.dialogs.measurepoly as measurepoly
import pyjamas.rannotations.rpolyline as rpolyline
from .rcallback import RCallback


class RCBMeasurePoly(RCallback):
    def cbMeasurePoly(self, measurement_list='', slice_numbers='', filename=''):
        '''
                Measures a set of polygons.
                The function has a number of parameters that can be used to call it from a script.
                :return: Dictionary with measurement results? Does skimage.measure have a measurement structure. Define
                measurement class?
        '''

        theresults = {}

        # Create and open dialog for measuring polygons.
        if filename == '' or filename is False or measurement_list == '' or measurement_list  is False or slice_numbers == '' or slice_numbers is False:
            # Create a measurement dialog that allows input of all this at once (unless all the parameters are given as arguments).
            dialog = QtWidgets.QDialog()
            ui = measurepoly.MeasurePolyDialog()
            ui.setupUi(dialog, savepath=self.pjs.cwd, firstslice=self.pjs.curslice+1, lastslice=self.pjs.slices.shape[0])
            dialog.exec_()
            dialog.show()
            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
        else:
            continue_flag = True

        if continue_flag:
            themeasurements = ui.measurements()
            theslicenumbers = range(ui.firstSlice-1, ui.lastSlice)

            theresults = self.measurePolygons(themeasurements, theslicenumbers)

            # If a file name was entered, save the data.
            if themeasurements["path"] != '':
                    # Save CSV file. If you implement the class, maybe just add a writeCSV (and also an openCSV method, and perhaps even saveMAT, loadMAT methods).
                    # The same could be done with an Annotation class.
               print(themeasurements)

            else:
                print(theresults)
                self.pjs.cwd = os.path.dirname(themeasurements["path"])

        return theresults

    def measurePolygons(self, measurements, slices):
        # todo: add other measurements: heterogeneity, shape factor, edge-to-centre distance profile, etc.
        # todo: change lists from dictionary into numpy.ndarrays.

        # Create dictionary with results.
        theresults = {'area': [], 'perimeter': [], 'pixel_values_perimeter': [], 'pixel_values_interior': [], 'image_mean': [], 'image_mode': []}

        theareas = [[] for i in slices]
        theperimeters = [[] for i in slices]
        thepixvalsperi = [[] for i in slices]
        thepixvalsinterior = [[] for i in slices]
        theimagemeans = []
        theimagemodes = []

        # For every slice ...
        for i in slices:
            theimage = self.pjs.slices[i]

            # Find the polylines in this slice.
            polygon_slice = self.pjs.polylines[i]

            n_polylines = len(polygon_slice)

            # For every polyline ...
            for j in range(n_polylines):
                # Create a polyline and measure it:
                thepolyline = rpolyline.RPolyline(polygon_slice[j])

                # Areas.
                if measurements['area']:
                    # Create a polyline and calculate the area.
                    theareas[i].append(thepolyline.area())

                # Perimeters.
                if measurements['perimeter']:
                    theperimeters[i].append(thepolyline.perimeter())

                # Pixel values.
                if measurements['pixels']:
                    intensities = thepolyline.pixel_values(theimage, self.pjs.brush_size)
                    thepixvalsperi[i].append(intensities[0])
                    thepixvalsinterior[i].append(intensities[1])

            # Image statistics.
            if measurements['image']:
                theimagemeans.append(numpy.mean(theimage))

                # todo: check for the numpy function to calculate the mode. If there isn't one, put the two lines below in a function.
                imhist = numpy.histogram(theimage, numpy.arange(numpy.max(theimage)+2))
                themode = imhist[1][numpy.argmax(imhist[0])]
                theimagemodes.append(themode)

        theresults['area'] = theareas
        theresults['perimeter'] = theperimeters
        theresults['pixel_values_perimeter'] = thepixvalsperi
        theresults['pixel_values_interior'] = thepixvalsinterior
        theresults['image_mean'] = theimagemeans
        theresults['image_mode'] = theimagemodes

        return theresults