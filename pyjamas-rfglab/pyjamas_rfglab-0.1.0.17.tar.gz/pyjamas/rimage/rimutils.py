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

import numbers
from typing import Tuple

import cv2
import numpy
import matplotlib.path as mplpth
import matplotlib.pyplot as plt
from scipy import ndimage
import scipy.interpolate
from scipy.sparse.csgraph import csgraph_from_dense
from skimage import io
from skimage.measure import find_contours
from skimage.morphology import watershed
import warnings


class rimutils:
    # Default sigma to use for the gradient calculation if necessary. This is the same as in dipimage.
    GRADMAG_DEFAULT_SIGMA = 1.0

    # These are some simple functions, but used in different places in the codebase. To avoid having to change them
    # everywhere if, for instance, one day we decide to use a different method to read a stack, I created class methods
    # for them here.
    @classmethod
    def read_stack(cls, filename: str = None) -> numpy.ndarray:
        """
        Reads an image using skimage.io.imread.

        Open CV's imreadmulti can also do this:
        tmp = cv2.imreadmulti(filename, flags=-1)
        self.pjs.slices = np.asarray(tmp[1], dtype=np.uint16)
        But considering the time necessary for the import and the actual instructions to eventually get an ndarray,
        skimage is twice as fast (at least!).
        So now we use scikit-image
        There is a problem with this function, though: if the image is a multipage tiff, it will normally report the
        shape of the resulting ndarray as [Z, rows, cols]
        (http://scikit-image.org/docs/dev/user_guide/numpy_images.html). BUT, if the multipage tiff has 4 pages,
        it gets totally confused, thinks this is a single page colour image, and reads the shape as
        [row, cols, channels], messing everything up ...


        :param filename:
        :return:
        """
        return io.imread(filename)

    @classmethod
    def write_stack(cls, filename: str = None, im: numpy.ndarray = None) -> bool:
        # We use scikit-image. But scikit-image emits a warning with some fluorescence images that their contrast
        # is low. This bit supresses the warning (https://github.com/scikit-image/scikit-image/issues/543).
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            io.imsave(filename, im)

    @classmethod
    def mip(cls, im: numpy.ndarray = None) -> numpy.ndarray:
        return numpy.max(im, axis=0)

    @classmethod
    def makeGraph(cls, im: numpy.ndarray = None):
        rows = numpy.arange(im.shape[0])
        cols = numpy.arange(im.shape[1])
        therows, thecols = numpy.meshgrid(rows, cols)

        therows = numpy.reshape(therows, therows.size)
        thecols = numpy.reshape(thecols, thecols.size)

        all_pixels = numpy.array([(arow, acol) for arow, acol in zip(therows, thecols)])

        # Find one index per pixel.
        all_pixels_ind = rimutils.sub2ind(im.shape, all_pixels[:, 0], all_pixels[:, 1])

        # Declaration of the matrix that contains pairs of neighbouring nodes and the cost associated with that edge.
        weight_matrix = numpy.ones((all_pixels_ind.size, all_pixels_ind.size)) * numpy.inf

        # Now build the matrix.
        # For each pixel.
        for i, coords in enumerate(all_pixels):
            # Calculate the neighbours and find their pixel ids and coordinates.
            theneighbours = rimutils._N8_(coords[0], coords[1], im.shape)
            theneighbours_ind = rimutils.sub2ind(im.shape, theneighbours[:, 0],
                                                 theneighbours[:, 1])  # Convert all vertices once and use dictionary?
            isrc = rimutils.sub2ind(im.shape, numpy.array([coords[0]]), numpy.array([coords[1]]))
            # For each neighbour ...
            for j, idst in enumerate(theneighbours_ind):
                weight_matrix[isrc, idst] = im[theneighbours[j, 0], theneighbours[j, 1]]

        # And use the matrix to build the graph.
        graph_sparse = csgraph_from_dense(weight_matrix, null_value=numpy.inf)

        return graph_sparse, weight_matrix

    # 4 neighbours (removing pixels outside the image).
    @staticmethod
    def _N4_(row, col, imsize=(numpy.inf, numpy.inf)):
        # asarray vs array: The main difference is that array (by default) will make a copy of the object, while asarray will not unless necessary.
        initial = numpy.array([[row - 1, col], [row + 1, col], [row, col - 1], [row, col + 1]], dtype=numpy.int16)
        big_enough = numpy.intersect1d((initial[:, 0] >= 0).nonzero(), (initial[:, 1] >= 0).nonzero())
        small_enough = numpy.intersect1d((initial[:, 0] < imsize[0]).nonzero(), (initial[:, 1] < imsize[1]).nonzero())
        good_rows = numpy.intersect1d(big_enough, small_enough)

        final = initial[good_rows, :]

        return final

    # Diagonal neighbours (removing pixels outside the image).
    @staticmethod
    def _ND_(row, col, imsize=(numpy.inf, numpy.inf)):
        # asarray vs array: The main difference is that array (by default) will make a copy of the object, while asarray will not unless necessary.
        initial = numpy.array([[row - 1, col - 1], [row + 1, col - 1], [row + 1, col + 1], [row - 1, col + 1]],
                              dtype=numpy.int16)
        big_enough = numpy.intersect1d((initial[:, 0] >= 0).nonzero(), (initial[:, 1] >= 0).nonzero())
        small_enough = numpy.intersect1d((initial[:, 0] < imsize[0]).nonzero(), (initial[:, 1] < imsize[1]).nonzero())
        good_rows = numpy.intersect1d(big_enough, small_enough)

        final = initial[good_rows, :]

        return final

    # 8 neighbours (removing pixels outside the image)
    @staticmethod
    def _N8_(row, col, imsize=(numpy.inf, numpy.inf)):
        return numpy.vstack((rimutils._N4_(row, col, imsize), rimutils._ND_(row, col, imsize)))

    # # array_shape takes on the format [rows, cols]. Object methods slightly slowed (half a microsecond?) than static ones.
    # def sub2ind(self, rows, cols):
    #     array_shape = self.image_array.shape
    #     ind = rows * array_shape[1] + cols
    #
    #     if type(ind) == numpy.int:
    #         ind = numpy.array([ind])
    #
    #     bad_values = numpy.concatenate(((ind < 0).nonzero(), (ind >= numpy.prod(array_shape)).nonzero()))
    #
    #     ind[bad_values] = -1
    #
    #     return ind

    # array_shape takes on the format [rows, cols].
    @classmethod
    def sub2ind(cls, array_shape, rows, cols):
        ind = rows * array_shape[1] + cols

        if type(ind) == numpy.int:
            ind = numpy.array([ind])

        bad_values = numpy.concatenate(((ind < 0).nonzero(), (ind >= numpy.prod(array_shape)).nonzero()))

        ind[bad_values] = -1

        return ind

    @classmethod
    def ind2sub(cls, array_shape: Tuple[int, int], ind: numpy.ndarray) -> (numpy.ndarray, numpy.ndarray):
        bad_values = numpy.concatenate(((ind < 0).nonzero(), (ind >= numpy.prod(array_shape)).nonzero()))

        rows: numpy.ndarray = numpy.array(ind.astype('int') / array_shape[1], dtype=numpy.int)
        cols: numpy.ndarray = ind % array_shape[1]

        rows[bad_values] = -1
        cols[bad_values] = -1

        return rows, cols

    @classmethod
    def flow(cls, firstslice: numpy.ndarray, secondslice: numpy.ndarray,
             desired_step_sz: numpy.ndarray = numpy.array([16, 16]),
             window_sz: numpy.ndarray = numpy.array([64, 64]), plots: bool = False, gradient_flag: bool = False,
             border_width: numpy.int = 1, calculated_step_sz=None, filter_output: bool = False,
             min_normxcorr: numpy.double = 0.0) -> \
            (numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray):
        """
        Calculates the flow field between firstslice and secondslice.

        :param firstslice: source image (numpy.ndarray).
        :param secondslice: target image (numpy.ndarray).
        :param desired_step_sz: final desired resolution (pixel distance) of the vector field [row, col]. Interpolation
        will be used if desired_step_sz < window_sz. Alternatively, this parameter can be a two-column array specifying
        the (row, col) coordinates where the vector field will be interpolated (numpy.ndarray).
        :param window_sz: initial window size (row, col) to calculate cross-correlation between source and target
        images. If the calculated cross-correlation is smaller than min_normxcorr, then the target window size will be
        doubled until the correlation is greater than min_normxcorr or the window size is greater than the image size
        (numpy.ndarray).
        :param plots: plot the vector field or not (bool).
        :param gradient_flag: use the gradient magnitude or the pixel values for the cross-correlation calculations.
        :param border_width: how many rows and columns to remove (numpy.int).
        :param calculated_step_sz: distance between points in the source image where the cross-correlation will be
        calculated [row, col] (numpy.ndarray).
        :param filter_output: find and delete vectors too different from their neighbours (bool).
        :param min_normxcorr: minimum acceptable cross-correlation value (numpy.double).
        :rtype: (numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray)
        :return: (Xvaldesired, Yvaldesired, X0desired, Y0desired)
        Xvaldesired: X components of the flow field vectors (numpy.ndarray).
        Yvaldesired: Y components of the flow field vectors (numpy.ndarray).
        Xf: X coordinates where the flow field was calculated (numpy.ndarray).
        Yf: Y coordinates where the flow field was calculated (numpy.ndarray).

        @todo: Why isn't there downward movement in the center region between the very first two time points (as there is in SIESTA)?
               Things seem to improve with window size = 32.
               Try RectBivariateSpline?
        """

        if isinstance(window_sz, numbers.Number):
            window_sz = numpy.array([window_sz, window_sz])

        # points_flag indicates if the user wants to find the flow field at
        # specific points. In that case, one can speed up the analysis a bit.
        points_flag: bool = False

        if isinstance(desired_step_sz, numbers.Number):
            desired_step_sz = numpy.array([desired_step_sz, desired_step_sz])
            points_flag = False
        elif isinstance(desired_step_sz, numpy.ndarray) and desired_step_sz.ndim == 2 and desired_step_sz.shape[0] > 1:
            points_flag = True

        if isinstance(calculated_step_sz, numbers.Number):
            calculated_step_sz = numpy.array([calculated_step_sz, calculated_step_sz])
        elif calculated_step_sz is None:
            calculated_step_sz = numpy.int16(numpy.round(window_sz / 2.))

        if gradient_flag:
            firstimage = ndimage.gaussian_gradient_magnitude(firstslice, sigma=rimutils.GRADMAG_DEFAULT_SIGMA)
            secondimage = ndimage.gaussian_gradient_magnitude(secondslice, sigma=rimutils.GRADMAG_DEFAULT_SIGMA)
        else:
            firstimage = firstslice
            secondimage = secondslice

        sz = firstimage.shape

        ws0 = window_sz  # Store the original window size in case the pyramidal approach is used.

        # First we calculate the flow field using window_sz as window size, and then we interpolate to achieve
        # desired_step_sz.
        Xval: numpy.ndarray = numpy.nan * numpy.ones([int(firstslice.shape[0] / calculated_step_sz[0]), int(
            firstslice.shape[1] / calculated_step_sz[1])])  # Flow field coordinates at window_sz resolution.
        Yval: numpy.ndarray = numpy.nan * numpy.ones(
            [int(firstslice.shape[0] / calculated_step_sz[0]), int(firstslice.shape[1] / calculated_step_sz[1])])
        #Xval: numpy.ndarray = numpy.nan * numpy.ones(firstimage.shape)
        #Yval: numpy.ndarray = numpy.nan * numpy.ones(firstimage.shape)

        for ii in range(0, sz[0], calculated_step_sz[0]):  # Rows
            for jj in range(0, sz[1], calculated_step_sz[1]):  # Columns
                # Ideally, what follows would be a do ... while ... end loop. Alas, Python (like Matlab) does not have
                # that conditional loop, and that forces me to do some pretty unelegant things ...

                # Initialize to -1 to go into the while loop at least once per pixel.
                max_normxcorr: numpy.double = -1.0

                # The first thing done in the while loop is to double the window size (in case) we come from a previous
                # iteration where the window size was not enough. So before going into the loop, I divide the window
                # size by two. This also needs the 2*window_sz in the condition in the while loop.
                window_sz = ws0 / 2.

                # If the minimum cross-correlations has not been attained and the window size still is small enough ...
                while max_normxcorr < min_normxcorr and 2 * window_sz[0] < sz[0] and 2 * window_sz[1] < sz[1]:
                    # Double interrogation window size.
                    window_sz = window_sz * 2.

                    # Search window size is twice the size of the interrogation window (+1 so that there is a central
                    # pixel).
                    search_ws = 2 * window_sz + 1

                    # Interrogation window (aka. the template).
                    minrowi = int(max(0, ii - numpy.floor(window_sz[0] / 2)))
                    maxrowi = int(min(sz[0] - 1, ii + numpy.floor(window_sz[0] / 2)))
                    mincoli = int(max(0, jj - numpy.floor(window_sz[1] / 2)))
                    maxcoli = int(min(sz[1] - 1, jj + numpy.floor(window_sz[1] / 2)))
                    im1 = firstimage[minrowi:maxrowi+1, mincoli:maxcoli+1]

                    # If the user wants to interpolate the vector field in specific points, and none of those points is
                    # in a given interrogation window, just skip the window by leaving the while loop.
                    thewindow = mplpth.Path(
                        numpy.array([[mincoli, minrowi], [mincoli, maxrowi], [maxcoli, maxrowi], [maxcoli, minrowi],
                                     [mincoli, minrowi]]),
                        closed=True)
                    if points_flag and numpy.count_nonzero(thewindow.contains_points(desired_step_sz)) == 0:
                        max_normxcorr = -1.0
                        break
                    # This code block is commented out, as it results in the presence of nans in the vector field,
                    # and scipy.interpolate.RectBivariateSpline, the superfast method that we use to interpolate the
                    # vector field, cannot handle nans. interp2d can, but it is much slower.

                    # Do this only for the windows that we are interested
                    # in (otherwise everything slows down dramatically).
                    # (@todo: that may not be true for the opencv implementation, which is FAAAAAAST!)
                    # First condition: normxcorr2 in Matlab would crash if all the values in the template were equal.
                    # Second condition:  make sure that at least 50% of the
                    # pixels are non-zero (this happens, for instance, when
                    # the images have been rotated). The results are much
                    # better than without this test.
                    if numpy.unique(im1).size == 1 or numpy.count_nonzero(im1) / numpy.prod(im1.shape) < 0.5:
                        continue

                    # Search window (twice as large as the interrogation window).
                    minrows = int(max(0, ii - numpy.floor(search_ws[0] / 2)))
                    maxrows = int(min(sz[0] - 1, ii + numpy.floor(search_ws[0] / 2)))
                    mincols = int(max(0, jj - numpy.floor(search_ws[1] / 2)))
                    maxcols = int(min(sz[1] - 1, jj + numpy.floor(search_ws[1] / 2)))
                    im2 = secondimage[minrows:maxrows+1, mincols:maxcols+1]

                    # Calculate and save the crosscorrelation. Converting the images to float32 is a requirement
                    # of cv2.matchTemplate, which will only work with uint8 or float32 images. Even with that
                    # conversion, this is 30X faster than skimage.features.match_template. In fact,
                    # rather than doing a paired cross-correlation, if you simply found im1 in secondimage it would be
                    # three times faster than using skimage with paired cross-correlation ... but ten times slower
                    # than the paired approach implemented in open cv.
                    # I tried all possible comparison methods, and TM_CCOEFF_NORMED provides the greatest dynamic range
                    # to distinguish between high an low correlations.
                    cc = cv2.matchTemplate(im2.astype(numpy.float32), im1.astype(numpy.float32), cv2.TM_CCOEFF_NORMED)

                    # Find the maximum cross-correlation. max_loc contains the (x, y) coordinates (not row, col) where
                    # the upper-left corner of the interrogation window maximizes cross-correlation.
                    _, max_normxcorr, _, max_loc = cv2.minMaxLoc(cc)

                    # Limit travelled distance: if the maximum cross-correlation is too far (e.g. on one of the corners,
                    # this can happen if there are black pixels in the image introduced when rotating them), repeat with
                    # a larger window size.
                    if numpy.linalg.norm(numpy.array([mincols + max_loc[0] - mincoli, minrows + max_loc[1] - minrowi]),
                                         2) >= numpy.mean(window_sz) / 2:
                        max_normxcorr = -1

                # If the cross-correlation was sufficient, ...
                if max_normxcorr >= min_normxcorr:
                    # We subtract the position of the top left corner of the interrogation window (mincoli, minrowi)
                    # from the position where placing the top-left corner of the interrogation window (with respect
                    # to the search window) produced the maximum cross-correlation
                    # (mincols+max_loc[0], minrows+max_loc[1]).
                    Xval[int(numpy.floor(ii / calculated_step_sz[0])), int(
                        numpy.floor(jj / calculated_step_sz[1]))] = mincols + max_loc[0] - mincoli
                    Yval[int(numpy.floor(ii / calculated_step_sz[0])), int(
                        numpy.floor(jj / calculated_step_sz[1]))] = minrows + max_loc[1] - minrowi
                    #Xval[ii, jj] = mincols + max_loc[0] - mincoli
                    #Yval[ii, jj] = minrows + max_loc[1] - minrowi
                else:
                    Xval[int(numpy.floor(ii / calculated_step_sz[0])), int(
                        numpy.floor(jj / calculated_step_sz[1]))] = numpy.nan
                    Yval[int(numpy.floor(ii / calculated_step_sz[0])), int(
                        numpy.floor(jj / calculated_step_sz[1]))] = numpy.nan
                    #Xval[ii, jj] = numpy.nan
                    #Yval[ii, jj] = numpy.nan

                #print(f"({int(numpy.floor(ii / calculated_step_sz[0]))}, {int(int(numpy.floor(jj / calculated_step_sz[1])))}) -> {Xval[int(numpy.floor(ii / calculated_step_sz[0])), int(numpy.floor(jj / calculated_step_sz[1]))]}")
                #print("")

        # Remove border measurements to avoid boundary effects.
        Xval = Xval[border_width:-border_width, border_width:-border_width]
        Yval = Yval[border_width:-border_width, border_width:-border_width]

        # Generate the coordinates of all the centers of the windows of size window_sz.
        X0, Y0 = numpy.meshgrid(numpy.arange(0, sz[1], calculated_step_sz[1]),
                                numpy.arange(0, sz[0], calculated_step_sz[0]))
        # Remove border measurements to avoid boundary effects.
        X0 = X0[border_width:-border_width, border_width:-border_width]
        Y0 = Y0[border_width:-border_width, border_width:-border_width]

        if filter_output: # Needs checking - straight from Matlab rflow.
            # Filter the output data trying to remove outliers using a normalized median test (see Raffel et al., Chapter 6.1.5).
            mag = numpy.sqrt(Xval * Xval + Yval * Yval)  # Vector magnitude.
            sk = 1  # Filter radius.
            kernel = numpy.ones([2 * sk + 1, 2 * sk + 1])
            kernel[
                sk, sk] = 0  # This is a kernel where all pixels are set to one except for the central pixel, set to zero.

            medians = numpy.nan * numpy.zeros(mag.shape)
            residuals = numpy.nan * numpy.zeros(mag.shape)
            normresiduals = numpy.nan * numpy.zeros(mag.shape)

            # This moves a 3x3 kernel through the "mag" matrix.
            for ii in range(mag.shape[0]):
                miny = max(0, ii - sk)  # Y coordinates.
                maxy = min(mag.shape[0], ii + sk + 1)
                for jj in range(mag.shape[1]):
                    minx = max(0, jj - sk)  # X coordinates.
                    maxx = min(mag.shape[1], jj + sk + 1)

                    tmp, mag[ii, jj] = mag[ii, jj], numpy.nan
                    subw = mag[miny:maxy, minx:maxx]
                    medians[ii, jj] = numpy.nanmedian(subw)
                    mag[ii, jj] = tmp
                    residuals[ii, jj] = numpy.abs(mag[ii, jj] - medians[ii, jj])

            # This moves a 3x3 kernel through the "residuals" matrix, calculated in the previous convolution.
            for ii in range(residuals.shape[0]):
                miny = max(0, ii - sk)  # Y coordinates.
                maxy = min(residuals.shape[0], ii + sk + 1)
                for jj in range(residuals.shape[1]):
                    minx = max(0, jj - sk)  # X coordinates.
                    maxx = min(residuals.shape[1], jj + sk + 1)

                    tmp, residuals[ii, jj] = residuals[ii, jj], numpy.nan
                    subw = residuals[miny:maxy, minx:maxx]
                    medianresidual = numpy.nanmedian(subw)
                    residuals[ii, jj] = tmp
                    normresiduals[ii, jj] = residuals[ii, jj] / (
                                medianresidual + .15)  # Magic number from Raffel et al. Prevents divisions by 0 in static regions.

            # Threshold for small normalized residuals is the value under which 95% of the normalized residuals
            # are included. "histogram" flattens the array.
            thehisto, _ = numpy.histogram(normresiduals, numpy.arange(0, numpy.amax(normresiduals), .5))
            thehisto = thehisto / numpy.prod(normresiduals.shape)  # Histogram of normalized residuals.
            thecumsum = numpy.cumsum(thehisto)  # Cumulative distribution function of residuals.
            th_ind = numpy.argmin(numpy.abs(thecumsum - .95))  # argmin returns the index of the min.
            eps_th = th_ind * .5

            Y_remove, X_remove = numpy.where(normresiduals > eps_th)
            # Xval[Y_remove, X_remove] = numpy.nan
            # Yval[Y_remove, X_remove] = numpy.nan

            # Replace the bad vectors using bivariate spline interpolation (see Raffel et al., 6.2).
            # RectBivariateSpline creates an object that can be called with a couple of coordinates (implements
            # the __call__ method).
            interpXfield = scipy.interpolate.RectBivariateSpline(Y0[:, 0], X0[0, :], Xval)
            interpYfield = scipy.interpolate.RectBivariateSpline(Y0[:, 0], X0[0, :], Yval)

            Xval[Y_remove, X_remove] = interpXfield(Y_remove, X_remove, grid=False)
            Yval[Y_remove, X_remove] = interpYfield(Y_remove, X_remove, grid=False)

        # Generate the origin coordinates for the flow field with the appropriate resolution or use the points given by
        # the user. desired_step_sz == 2 when there is only one row in the size vector.
        if desired_step_sz.size == 2:
            Xf = numpy.arange(0, sz[1], desired_step_sz[1])
            Yf = numpy.arange(0, sz[0], desired_step_sz[0])

        else:
            Xf = desired_step_sz[:, 1]
            Yf = desired_step_sz[:, 0]

        xval = Xval.ravel()
        good_indices = numpy.nonzero(numpy.invert(numpy.isnan(xval)))
        xval = list(xval[good_indices])
        yval = Yval.ravel()
        yval = list(yval[good_indices])
        y0 = Y0.ravel()
        y0 = list(y0[good_indices])
        x0 = X0.ravel()
        x0 = list(x0[good_indices])

        # Linear interpolation here is marginally better than the default multiquadratic ...
        # based on limited testing!
        from scipy.interpolate import Rbf
        rbfi_x = Rbf(y0, x0, xval, function='linear')
        rbfi_y = Rbf(y0, x0, yval, function='linear')
        interpXfield = rbfi_x(Xf, Yf)
        interpYfield = rbfi_y(Xf, Yf)

        Xvaldesired = interpXfield
        Yvaldesired = interpYfield

        if plots:
            # Calculate the end point of the flow field vector.
            fig, ax = plt.subplots(1, 1)
            plt.imshow(firstslice)
            #ax.quiver(Y0[:, 0], X0[0, :], Xval, -Yval)
            ax.quiver(Yf, Xf, Xvaldesired, -Yvaldesired)
            # ax.set_ylim(ax.get_ylim()[::-1])
            # ax.set_ylim(ax[1].get_ylim()[::-1])

            plt.show()

        return Xvaldesired, Yvaldesired, Xf, Yf

    @classmethod
    def waterseed(cls, image: numpy.ndarray, seeds: numpy.ndarray) -> list:
        """
        Marker-based segmentation of the image. Uses the watershed, region growing algorithm as implemented in
        skimage.morphology.

        :param image: image to segment (numpy.ndarray).
        :param seeds: (X, Y) coordinates of the seed points (numpy.ndarray).
        :return: list of contours determined by the watershed lines (list). Only polygons not touching the image
        borders are returned.
        """
        contour_list = list([])

        # Build seed image.
        seed_image = numpy.zeros(image.shape)

        try:
            for label, seed_xy in enumerate(seeds):
                seed_image[seed_xy[1], seed_xy[0]] = label
        except:
            print('There seems to be an issue with the ' + str(
                label) + 'th of your watershed seeds being too close to or outside the image limits.')
            return contour_list

        # Run watershed.
        labels = watershed(image, seed_image, connectivity=2)  # , mask=image)

        # Extract contours.
        thelabels = numpy.unique(labels)
        for aLabel in thelabels:
            bin_mask = numpy.asarray(labels == aLabel,
                                     dtype=int)  # skimage.segmentation.find_boundaries can also be used for this.
            aContour = find_contours(bin_mask, 0)
            aContour = aContour[0]

            # Add polygon only if not touching edge.
            if numpy.all((aContour[:, 0] > 0) & (aContour[:, 0] < image.shape[0] - 1) & (aContour[:, 1] > 0) &
                         (aContour[:, 1] < image.shape[1] - 1)):
                aContour = (numpy.asarray(aContour)[:, ::-1]).tolist()
                contour_list.append(aContour)

        return contour_list

    @classmethod
    def generate_subimages(cls, image: numpy.ndarray, subimage_sz: Tuple[int, int], step_sz: Tuple[int, int]) \
            -> Tuple[numpy.ndarray, int, int]:
        if image is False or image is None or subimage_sz is False or subimage_sz is None or step_sz is False or \
                step_sz is None:
            return numpy.empty((1, 0), None, None)

        row_rad = int(numpy.floor(subimage_sz[0] / 2))
        col_rad = int(numpy.floor(subimage_sz[1] / 2))
        max_row_range = image.shape[0] - row_rad
        if subimage_sz[0] % 2 == 0:
            max_row_range += 1
        max_col_range = image.shape[1] - col_rad
        if subimage_sz[1] % 2 == 0:
            max_col_range += 1

        for row in range(row_rad, max_row_range, step_sz[0]):
            for col in range(col_rad, max_col_range, step_sz[1]):
                minrow = row - row_rad
                maxrow = row + row_rad
                if subimage_sz[0] % 2 == 1:
                    maxrow += 1

                mincol = col - col_rad
                maxcol = col + col_rad
                if subimage_sz[1] % 2 == 1:
                    maxcol += 1

                yield image[minrow:maxrow, mincol:maxcol], row, col
