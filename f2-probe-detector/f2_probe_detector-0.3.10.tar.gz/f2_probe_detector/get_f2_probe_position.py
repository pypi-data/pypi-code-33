#!/usr/bin/env
# -*- coding: utf-8 -*-

import argparse
import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np

from astropy.io import fits
from astropy.visualization import ImageNormalize, LinearStretch, \
    PercentileInterval

from scipy import ndimage
from sys import exit

from .version import __version__


def main():

    pargs = _parse_arguments()

    get_f2_probe_position(
        list_of_files=pargs.files,
        save_plots=pargs.save_plots,
    )


def get_f2_probe_position(list_of_files, save_plots=False):

    table_header = ' {:40} {:10} {:10}'.format(
        'filename', 'x', 'y')

    print('\n {} {}'.format(__name__, __version__))
    print(' ' + len(table_header) * '-')
    print(table_header)
    print(' ' + len(table_header) * '-')

    for _file in list_of_files:

        array = get_array(_file)
        header = get_header(_file)

        # Pre-process data
        circle_mask = CircleMask()
        masked_array = circle_mask.mask_array(array)

        # Filter and mask
        probe_image = get_probe_head(masked_array)
        x, y = get_center_of_mass(probe_image)

        table_row = ' {:40s} {:10.5f} {:10.5f}'.format('...' + _file[-36:], x, y)

        print(table_row)

        if save_plots:

            norm = ImageNormalize(array, interval=PercentileInterval(95.),
                                  stretch=LinearStretch())

            fig = plt.figure()
            ax = fig.add_subplot(111)

            im = ax.imshow(array, origin='lower', norm=norm)
            ax.axvline(x, color='red', alpha=0.5)
            ax.axhline(y, color='red', alpha=0.5)

            fig.savefig(_file.replace('.fits','.png'))

            del fig
            del ax
            del im


def get_array(filename):
    """
    Read image data array.

    Parameters
    ----------
        filename : str

    Returns
    -------
        numpy.ndarray
    """
    hdul = fits.open(filename)

    if len(hdul) == 2:
        return hdul[1].data[0]
    elif len(hdul) == 1:
        return hdul[0].data[0]
    else:
        raise fits.VerifyError("Input file an unknown format. Verify it.")


def get_header(filename):
    """
    Read image header.

    Parameters
    ----------
        filename : str

    Returns
    -------
        fits.Header
    """

    hdul = fits.open(filename)

    if len(hdul) == 2:
        return hdul[1].header
    elif len(hdul) == 1:
        return hdul[0].header
    else:
        raise fits.VerifyError("Input file an unknown format. Verify it.")


def get_center_of_mass(image):
    """
    Measures center of the object using center the first image momenta
    M00, M01 and M10, defined by:

    M(p,q) = sum_p sum_q i^p * j*q * I(p, q)

    The object's center of mass is the defined by:

    <center_row> = M(1,0) / M(0,0)
    <center_col> = M(0,1) / M(0,0)

    Parameters
    ----------
        image : ndarray

    Returns
    -------
        tuple of floats
            x and y coordinates of the center of mass.
    """
    h, w = image.shape
    grid_row, grid_col = np.mgrid[0:h, 0:w]

    m_00 = image.sum()

    m_10 = (grid_col * image).sum()
    center_row = m_10 / m_00

    m_01 = (grid_row * image).sum()
    center_col = m_01 / m_00

    return center_row, center_col


def get_enclosed_circle(image):
    """
    Uses OpenCV minEnclosingCircle to find the minimum enclosing circle.
    As input, one needs to use the probe image obtained from the
    :func:`get_probe_head`.

    Parameters
    ----------
        probe_image : ndarray

    Returns
    -------
        x : float
        y : float
        radius : float

    """

    temp = np.ma.filled(image, 0)
    temp = np.array(temp / temp.max() * 255, dtype=np.uint8)

    ret, thresh = cv.threshold(temp, 127, 255, cv.THRESH_BINARY)
    image, contours, hierarchy = cv.findContours(thresh, 1, 2)

    (cx, cy), radius = cv.minEnclosingCircle(contours[0])

    return cx, cy, radius


def get_probe_head(image):
    """
    This method masks the image by subtracting the whole image by its median
    and inverting the grayscale by multiplying it by -1. Then it sets the values
    of the pixels that are below to 1/2 standard deviation to zero. The other pixels
    keep their original value.

    Finally, it applies `grey_opening` to eliminate eventual noisy pixels that does not
    belong to the probe.

    Parameters
    ----------
        image : ndarray
            Sliced and filtered 2D ndarray.

    Returns
    -------
        ndarray
            Masked array.
    """

    im_bias = np.ma.median(image)
    im_bias_corrected = - (image - im_bias)

    # fill mask
    temp = np.ma.filled(im_bias_corrected, 0)

    # filter noise
    temp = ndimage.median_filter(temp, 5)

    # convert data to be used with opencv
    temp = np.uint8((temp - temp.min()) / temp.ptp() * 255)

    # apply threshold
    ret, thresh = cv.threshold(src=temp, thresh=127, maxval=255,
                               type=cv.THRESH_BINARY + cv.THRESH_OTSU)

    # noise removal
    kernel = np.ones((3, 3), np.uint8)
    opening = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel, iterations=2)

    # sure background area
    sure_bg = cv.erode(opening, kernel, iterations=5)

    # canny edge detection
    temp = opening * sure_bg
    edges = cv.Canny(temp, np.median(temp), np.percentile(temp, 75.))

    _, contours, hierarchy = cv.findContours(edges, mode=cv.RETR_TREE,
                                             method=cv.CHAIN_APPROX_TC89_L1)

    area = 0
    contour = None
    for c in contours:
        c_area = cv.contourArea(c)
        if c_area > area:
            contour = c

    temp = cv.fillPoly(temp, contour, color=255)

    temp = cv.distanceTransform(temp, cv.DIST_L2, 5)
    temp = np.where(temp > 0.5 * temp.max(), temp, 0)
    temp = np.uint8(temp)

    return temp


def get_shifted_image(image, dx, dy):
    """
    Shift the image using `scipy.interpolation`.

    Parameters
    ----------
        image : ndarray
            2d ndarray containing the image
        dx : float
            shift size in x
        dy : float
            shift size in y

    Returns
    -------
        ndarray
            shifted image
    """
    return ndimage.shift(image, (dy, dx), order=5, mode='nearest')


def _parse_arguments():
    """
    Parse the argument given by the user in the command line.

    Returns
    -------
        pargs : Namespace
            A namespace containing all the parameters that will be used for
            the "detect_probe" function.
    """
    parser = argparse.ArgumentParser(
        description='Find the (x, y) position of the Flamingos 2 guide probe, '
            'also known as "On-Instrument Wavefront Sensor."',
        prog='get_f2_probe_position'
    )

    parser.add_argument('files', metavar='files', type=str, nargs='+',
                        help="input filenames.")

    parser.add_argument('--save-plots', action='store_true',
                        help="Save diagnose plots")

    parser.add_argument('-v', '--version', action='version',
                        version='{}'.format(__version__),
                        help="Print version and leave")

    return parser.parse_args()


class CircleMask:

    x = 1024
    y = 1024
    radius = 1000

    def mask_array(self, array):

        height, width = array.shape
        y_grid, x_grid = np.mgrid[0:height, 0:width]
        r_grid = np.sqrt((x_grid - self.x) ** 2 + (y_grid - self.y) ** 2)

        masked_array = np.ma.masked_where(r_grid > self.radius, array)

        return masked_array


if __name__ == '__main__':
    main()
