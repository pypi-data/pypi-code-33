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
from PyQt5 import QtWidgets
from shapely.geometry import Point
from scipy.spatial import ConvexHull
import skimage.filters

import pyjamas.dialogs as dialogs
from .rcallback import RCallback
from pyjamas.rimage.rimutils import rimutils
from pyjamas.rutils import RUtils


class RCBSegment(RCallback):
    DEFAULT_FLOW_WINDOW_SZ = 64
    DEFAULT_SMOOTHING_SIGMA = 0.65
    DEFAULT_ALPHA_CONCAVE_HULL = 25  # Trial and error ...
    _MIN_CELL_AREA = 10
    _MAX_CELL_AREA = 10000
    CENTER_SEEDS_CLOSER_TO_THE_EDGE = 6

    # Smallest possible value for firstSlice is 1.
    def cbPropagateSeeds(self, firstSlice: int = None, lastSlice: int = None, xcorrWindowSize: int = None) -> bool:

        # If not enough parameters, open a dialog.
        if (firstSlice is False or firstSlice is None or lastSlice is False or lastSlice is None or xcorrWindowSize is False or xcorrWindowSize is None) and self.pjs is not None:
            dialog = QtWidgets.QDialog()
            ui = dialogs.propagateseeds.PropagateSeedsDialog()
            ui.setupUi(dialog, firstslice=self.pjs.curslice + 1, lastslice=self.pjs.slices.shape[0],
                       xcorrwinsz=dialogs.propagateseeds.PropagateSeedsDialog.xcorrWindowSize)
            dialog.exec_()
            dialog.show()
            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            theparameters = ui.parameters()

            dialog.close()

        # Otherwise, continue with the supplied parameters.
        else:
            theparameters = {'first': firstSlice, 'last': lastSlice, 'xcorr_win_sz': xcorrWindowSize}
            continue_flag = True

        # When you have the input parameters:
        if continue_flag:
            # Propagate forward.
            if theparameters['first'] <= theparameters['last']:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'])

            # Propagate backwards.
            else:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'] - 2, -1)

            # But DO propagate!!
            self.propagateSeeds(theparameters, theslicenumbers)

            self.pjs.repaint()

            return True
        else:
            return False

    def cbExpandSeeds(self, firstSlice: int = None, lastSlice: int = None, sigma: float = None) -> bool:

        # If not enough parameters, open a dialog.
        if (firstSlice is False or firstSlice is None or lastSlice is False or lastSlice is None or sigma is False or sigma is None) and self.pjs is not None:
            dialog = QtWidgets.QDialog()
            ui = dialogs.expandseeds.ExpandSeedsDialog()
            ui.setupUi(dialog, firstslice=self.pjs.curslice + 1, lastslice=self.pjs.slices.shape[0],
                       gaussian_sigma=dialogs.expandseeds.ExpandSeedsDialog.gaussianSigma)
            dialog.exec_()
            dialog.show()
            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            theparameters = ui.parameters()

            dialog.close()

        # Otherwise, continue with the supplied parameters.
        else:
            theparameters = {'first': firstSlice, 'last': lastSlice, 'sigma': sigma}
            continue_flag = True

        # When you have the input parameters:
        if continue_flag:
            # Expand forward.
            if ui.firstSlice <= ui.lastSlice:
                theslicenumbers = numpy.arange(ui.firstSlice - 1, ui.lastSlice)

            # Expand backwards.
            else:
                theslicenumbers = numpy.arange(ui.firstSlice - 1, ui.lastSlice - 2, -1)

            # But DO expand!!
            self.expandSeeds(theparameters, theslicenumbers)

            self.pjs.repaint()

            return True
        else:
            return False

    def cbExpandNPropagateSeeds(self, firstSlice: int = None, lastSlice: int = None, sigma: float = None,
                                xcorrWindowSize: int = None) -> bool:
        # If not enough parameters, open a dialog.
        if (firstSlice is False or firstSlice is None or lastSlice is False or lastSlice is None or xcorrWindowSize is False or xcorrWindowSize is None or sigma is False or sigma is None) and self.pjs is not None:
            dialog = QtWidgets.QDialog()
            ui = dialogs.expandnpropagateseeds.ExpandNPropagateSeedsDialog()
            ui.setupUi(dialog, firstslice=self.pjs.curslice + 1, lastslice=self.pjs.slices.shape[0],
                       gaussian_sigma=dialogs.expandnpropagateseeds.ExpandNPropagateSeedsDialog.gaussianSigma,
                       xcorrwinsz=dialogs.expandnpropagateseeds.ExpandNPropagateSeedsDialog.xcorrWindowSize)
            dialog.exec_()
            dialog.show()
            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            theparameters = ui.parameters()

            dialog.close()

        # Otherwise, continue with the supplied parameters.
        else:
            theparameters = {'first': firstSlice, 'last': lastSlice, 'sigma': sigma, 'xcorr_win_sz': xcorrWindowSize}
            continue_flag = True

        # When you have the input parameters:
        if continue_flag:
            # Expand forward.
            if ui.firstSlice <= ui.lastSlice:
                theslicenumbers = numpy.arange(ui.firstSlice - 1, ui.lastSlice)

            # Expand backwards.
            else:
                theslicenumbers = numpy.arange(ui.firstSlice - 1, ui.lastSlice - 2, -1)

            # But DO expand!!
            self.expandNPropagateSeeds(theparameters, theslicenumbers)

            self.pjs.repaint()

            return True
        else:
            return False

    def propagateSeeds(self, parameters: dict, theslices: numpy.ndarray):

        # Output parameters.
        Xflow: numpy.ndarray = numpy.empty(0)
        Yflow: numpy.ndarray = numpy.empty(0)

        xcorr_win_sz = parameters.get('xcorr_win_sz', RCBSegment.DEFAULT_FLOW_WINDOW_SZ)

        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        self.pjs.statusbar.showMessage(f"Processing {num_slices-1} images ...")

        # For every slice ...
        for i in range(num_slices - 1):
            self.pjs.statusbar.showMessage(f"Processing image {i+1}/{num_slices-1} ...")

            # Make sure there are fiducials to move.
            if not self.pjs.fiducials[theslices[i]]:
                return

            # Calculate the optic flow between consecutive images and interpolate at the fiducials.
            Xflow, Yflow, _, _ = rimutils.flow(self.pjs.slices[theslices[i]],
                                               self.pjs.slices[theslices[i + 1]],
                                               numpy.array(self.pjs.fiducials[theslices[i]]), xcorr_win_sz)

            # Shift the position of the fiducials in this slice by the flow ... In this case, the coordinates are
            # organized as [x, y], as they come from the fiducial list in PyJAMAS.
            destination_point_array = numpy.array(self.pjs.fiducials[theslices[i]])
            destination_point_array[:, 0] = numpy.int64(numpy.round(
                numpy.float64(destination_point_array[:, 0]) + Xflow))  # X coordinate.
            destination_point_array[:, 1] = numpy.int64(numpy.round(
                numpy.float64(destination_point_array[:, 1]) + Yflow))  # Y coordinate.

            # Here we should clip the fiducials at the ends so that seeds do not go beyond image margins.
            # ind2 = find(next_seeds(:, 1) < 0);
            # next_seeds(intersect(ind, ind2), 1) = 0;
            # ind2 = find(next_seeds(:, 1) >= ud.imsize(1));
            # next_seeds(intersect(ind, ind2), 1) = ud.imsize(1) - 1;
            # ind2 = find(next_seeds(:, 2) < 0);
            # next_seeds(intersect(ind, ind2), 2) = 0;
            # ind2 = find(next_seeds(:, 2) >= ud.imsize(2));
            # next_seeds(intersect(ind, ind2), 2) = ud.imsize(2) - 1;

            # ... before copying them onto the next slice.
            self.pjs.fiducials[theslices[i + 1]] = destination_point_array.tolist()

        self.pjs.statusbar.showMessage("Done!")

        return

    def expandSeeds(self, parameters, theslices) -> bool:
        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        self.pjs.statusbar.showMessage(f"Processing {num_slices} images ...")

        # For every slice ...
        for i in range(num_slices):
            self.pjs.statusbar.showMessage(f"Processing image {i + 1}/{num_slices} ...")

            # Make sure there are fiducials to expand.
            if not self.pjs.fiducials[theslices[i]]:
                continue

            theimage = self.pjs.slices[theslices[i]].copy()
            theimage = skimage.filters.gaussian(theimage, parameters['sigma'], multichannel=False)
            # Expand the seeds in the image.
            contour_list = rimutils.waterseed(theimage, numpy.asarray(self.pjs.fiducials[theslices[i]]))
            # Or for gradient-based segmentation:
            # import skimage.filters
            # contour_list = rimutils.waterseed(skimage.filters.sobel(self.pjs.slices[theslices[i]]),
            #                                               numpy.asarray(self.pjs.fiducials[theslices[i]]))

            # Add the contours to the list of annotations.
            for aContour in contour_list:
                self.pjs.addPolyline(aContour, theslices[i])

        self.pjs.statusbar.showMessage("Done!")

        return True

    def centerSeeds(self, distance, theslices, exclude_peripheral_seeds=False):
        """

        :param distance:
        :param theslices:
        :param exclude_peripheral_seeds: use the convex_hull?
        :return:
        """
        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        # For every slice ...
        for i in range(num_slices):
            thepolylines = [RUtils.qpolygonf2polygon(one_polyline) for one_polyline in self.pjs.polylines[theslices[i]]]

            # Find the concave hull for the fiducials
            if exclude_peripheral_seeds:
                fiducial_hull: numpy.ndarray = RUtils.concave_hull(numpy.asarray(self.pjs.fiducials[theslices[i]]),
                                                                   self.DEFAULT_ALPHA_CONCAVE_HULL)

                if fiducial_hull.size == 0:
                    fiducial_hull = ConvexHull(numpy.asarray(self.pjs.fiducials[theslices[i]]))
            # The problem is that polygons and fiducials are not stored in the same order. Aaaaarghh!
            # Or rather, they are in the same order, but the order is updated when polygons are deleted
            # after touching the edge?
            # An alternative is to find, for each fiducial, an enclosing polygon, and go from there.
            for idx_fiducial, one_fiducial in enumerate(self.pjs.fiducials[theslices[i]]):
                # If peripheral points must be excluded and this is one of them, then skip it.
                if exclude_peripheral_seeds and idx_fiducial in fiducial_hull:
                    continue

                oneShapelyFiducial = Point(one_fiducial)

                for one_polyline in thepolylines:
                    if one_polyline.contains(oneShapelyFiducial):
                        if oneShapelyFiducial.distance(one_polyline.exterior) < distance and \
                                RCBSegment._MIN_CELL_AREA < one_polyline.area < RCBSegment._MAX_CELL_AREA:
                            polycentroid = one_polyline.centroid
                            self.pjs.fiducials[theslices[i]][idx_fiducial][0] = int(polycentroid.x)
                            self.pjs.fiducials[theslices[i]][idx_fiducial][1] = int(polycentroid.y)

                        break

        return

    def expandNPropagateSeeds(self, parameters, theslices):

        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        self.pjs.statusbar.showMessage(f"Processing {num_slices} images ...")

        # For every slice ...
        for i in range(num_slices - 1):
            self.pjs.statusbar.showMessage(f"Processing image {i + 1}/{num_slices} ...")

            # Expand in the current time point.
            self.expandSeeds(parameters, theslices[i])

            # Center seeds.
            self.centerSeeds(RCBSegment.CENTER_SEEDS_CLOSER_TO_THE_EDGE, theslices[i], True)

            # Propagate to the next time point.
            self.propagateSeeds(parameters, theslices[i:i + 2])

        # Finally, expand in the last time point and center the seeds.
        self.pjs.statusbar.showMessage(f"Processing image {num_slices}/{num_slices} ...")

        self.expandSeeds(parameters, theslices[-1])

        # Center seeds.
        self.centerSeeds(RCBSegment.CENTER_SEEDS_CLOSER_TO_THE_EDGE, theslices[-1], True)

        self.pjs.statusbar.showMessage("Done!")

        return
