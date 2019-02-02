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

import numpy

import pyjamas.pjscore as pjscore
from .rcallback import RCallback


class RCBCrop(RCallback):
    """
    Crops an image.
    """

    def cbCrop(self, coordinates: numpy.ndarray = None, new_window: bool = False) -> bool:
        """

        :param coordinates: ndarray with two columns containing the x, y coordinates of the region to crop.
        :param new_window: True if the cropped image should open in a new PyJAMAS session, False if the current window
        should be used instead.
        :return: False if no coordinates are provided, True otherwise.
        """
        if (not coordinates) | (coordinates is None) | (coordinates == []):
            thepolylines = self.pjs.polylines[self.pjs.curslice]

            if thepolylines != [] and thepolylines[0] != []:
                thepolyline = thepolylines[0].boundingRect()
                minx, miny, maxx, maxy = thepolyline.getCoords()

            else:
                return False

        else:
            # This is here mainly to crop around non-rectangular polylines.
            minx, miny = numpy.min(coordinates, axis=0)
            maxx, maxy = numpy.max(coordinates, axis=0)

        # Make sure you are working with integers to prevent errrors when slicing the original image.
        minx, miny, maxx, maxy = numpy.uint((minx, miny, maxx, maxy))


        # Open in current window or new window?
        if not new_window:
            # Crop.
            one = numpy.uint(1)
            self.pjs.slices = self.pjs.slices[:, miny:(maxy+one), minx:(maxx+one)]

            # Initialize annotations and image.
            self.pjs.initImage()
        else:
            # Create a new window containing the cropped image.
            new_pjs = pjscore.PyJAMAS()
            one = numpy.uint(1)
            new_pjs.slices = self.pjs.slices[:, miny:(maxy + one), minx:(maxx + one)].copy()  # Make a copy of the data.
            new_pjs.curslice = self.pjs.curslice

            # Initialize annotations and image.
            new_pjs.initImage()

        return True
