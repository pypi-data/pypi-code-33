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

from typing import List

import numpy
from PyQt5 import QtWidgets

from .rcallback import RCallback
from pyjamas.rimage.rimutils import rimutils
from pyjamas.rutils import RUtils


class RCBImage(RCallback):
    CW: int = 90
    CCW: int = -90
    UP_DOWN: int = 1
    LEFT_RIGHT: int = 2

    def cbRotateImage(self, direction: int = CW) -> bool:
        if self.pjs.slices == []:
            return False

        if direction == self.CW:
            # self.pjs.slices = numpy.asarray([numpy.rot90(x, -1) for x in self.pjs.slices]) # An order of magnitude slower than below.
            self.pjs.slices = numpy.rot90(self.pjs.slices, -1, (1, 2))

        elif direction == self.CCW:
            # self.pjs.slices = numpy.asarray([numpy.rot90(x) for x in self.pjs.slices]) # An order of magnitude slower than below.
            self.pjs.slices = numpy.rot90(self.pjs.slices, 1, (1, 2))

        self.pjs.initImage()

        return True

    def cbFlipImage(self, direction: int = LEFT_RIGHT) -> bool:
        if self.pjs.slices == []:
            return False

        if direction == self.LEFT_RIGHT:
            # self.pjs.slices = numpy.flip(self.pjs.slices, 2)  # Order or magnitude slower than the code below.
            self.pjs.slices = self.pjs.slices[..., ::-1]
        elif direction == self.UP_DOWN:
            # self.pjs.slices = numpy.fliplr(self.pjs.slices)  # Could have used flip with parameter 1, but this is faster. Unfortunately, there is no fast function to flip with parameter 2. Still, slower than below.
            self.pjs.slices = self.pjs.slices[..., ::-1, :]

        self.pjs.initImage()

        return True

    def cbMIPImage(self, slice_list: List[int]) -> bool:
        if self.pjs.slices == []:
            return False

        if slice_list is False:
            slice_list_str, ok_pressed = QtWidgets.QInputDialog.getText(None, "Maximum intenstiy projection", "Enter a range of slices (e.g. 0, 1, 4-8, 15): ", QtWidgets.QLineEdit.Normal, "")

            if not ok_pressed:
                return False

            if slice_list_str == '':
                slice_list = list(range(self.pjs.n_frames))
            else:
                slice_list = RUtils.parse_range_list(slice_list_str)

        self.pjs.slices = rimutils.mip(self.pjs.slices[slice_list])

        self.pjs.initImage()

        return True
