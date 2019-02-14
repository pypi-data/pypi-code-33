# -*- coding: utf-8 -*-
#
# This file contains a modified version of the skimage iradon transform,
# license under the modified BSD license.
#
# The iradon function has been modified so that the output agrees with 
# the output of an equivalent transform performed in MATLAB using the
# inbuilt iradon function.

from __future__ import division
import numpy as np
from scipy.fftpack import fft, ifft, fftfreq
from scipy.interpolate import interp1d
from warnings import warn


def iradon(radon_image, theta=None, output_size=None,
           filter="ramp", interpolation="linear", circle=None):
    """
    Inverse radon transform.
    Reconstruct an image from the radon transform, using the filtered
    back projection algorithm.
    Parameters
    ----------
    radon_image : array_like, dtype=float
        Image containing radon transform (sinogram). Each column of
        the image corresponds to a projection along a different angle. The
        tomography rotation axis should lie at the pixel index
        ``radon_image.shape[0] // 2`` along the 0th dimension of
        ``radon_image``.
    theta : array_like, dtype=float, optional
        Reconstruction angles (in degrees). Default: m angles evenly spaced
        between 0 and 180 (if the shape of `radon_image` is (N, M)).
    output_size : int
        Number of rows and columns in the reconstruction.
    filter : str, optional (default ramp)
        Filter used in frequency domain filtering. Ramp filter used by default.
        Filters available: ramp, shepp-logan, cosine, hamming, hann.
        Assign None to use no filter.
    interpolation : str, optional (default 'linear')
        Interpolation method used in reconstruction. Methods available:
        'linear', 'nearest', and 'cubic' ('cubic' is slow).
    circle : boolean, optional
        Assume the reconstructed image is zero outside the inscribed circle.
        Also changes the default output_size to match the behaviour of
        ``radon`` called with ``circle=True``.
        The default behavior (None) is equivalent to False.
    Returns
    -------
    reconstructed : ndarray
        Reconstructed image. The rotation axis will be located in the pixel
        with indices
        ``(reconstructed.shape[0] // 2, reconstructed.shape[1] // 2)``.
    References
    ----------
    .. [1] AC Kak, M Slaney, "Principles of Computerized Tomographic
           Imaging", IEEE Press 1988.
    .. [2] B.R. Ramesh, N. Srinivasa, K. Rajgopal, "An Algorithm for Computing
           the Discrete Radon Transform With Some Applications", Proceedings of
           the Fourth IEEE Region 10 International Conference, TENCON '89, 1989
    Notes
    -----
    It applies the Fourier slice theorem to reconstruct an image by
    multiplying the frequency domain of the filter with the FFT of the
    projection data. This algorithm is called filtered back projection.
    """
    if radon_image.ndim != 2:
        raise ValueError('The input image must be 2-D')
    if theta is None:
        m, n = radon_image.shape
        theta = np.linspace(0, 180, n, endpoint=False)
    else:
        theta = np.asarray(theta)
    if len(theta) != radon_image.shape[1]:
        raise ValueError("The given ``theta`` does not match the number of "
                         "projections in ``radon_image``.")
    interpolation_types = ('linear', 'nearest', 'cubic')
    if interpolation not in interpolation_types:
        raise ValueError("Unknown interpolation: %s" % interpolation)
    if not output_size:
        # If output size not specified, estimate from input radon image
        if circle:
            output_size = radon_image.shape[0]
        else:
            output_size = int(np.floor(np.sqrt((radon_image.shape[0]) ** 2
                                               / 2.0)))
    if circle is None:
        warn('The default of `circle` in `skimage.transform.iradon` '
             'will change to `True` in version 0.15.')
        circle = False
    if circle:
        radon_image = _sinogram_circle_to_square(radon_image)

    th = (np.pi / 180.0) * theta
    # resize image to next power of two (but no less than 64) for
    # Fourier analysis; speeds up Fourier and lessens artifacts
    projection_size_padded = \
        max(64, int(2 ** np.ceil(np.log2(2 * radon_image.shape[0]))))
    pad_width = ((0, projection_size_padded - radon_image.shape[0]), (0, 0))
    img = np.pad(radon_image, pad_width, mode='constant', constant_values=0)

    # Construct the Fourier filter
    n1 = np.arange(0, projection_size_padded / 2 + 1, dtype=np.int)
    n2 = np.arange(projection_size_padded / 2 - 1, 0, -1, dtype=np.int)
    n = np.concatenate((n1, n2))
    f = np.zeros(projection_size_padded)
    f[0] = 0.25
    f[1::2] = -1 / (np.pi * n[1::2])**2

    omega = 2 * np.pi * fftfreq(projection_size_padded)
    fourier_filter = 2 * np.real(fft(f))         # ramp filter
    if filter == "ramp":
        pass
    elif filter == "shepp-logan":
        # Start from first element to avoid divide by zero
        fourier_filter[1:] *= np.sin(omega[1:] / 2) / (omega[1:] / 2)
    elif filter == "cosine":
        freq = (0.5 * np.arange(0, projection_size_padded)
                / projection_size_padded)
        cosine_filter = np.fft.fftshift(np.sin(2 * np.pi * np.abs(freq)))
        fourier_filter *= cosine_filter
    elif filter == "hamming":
        hamming_filter = np.fft.fftshift(np.hamming(projection_size_padded))
        fourier_filter *= hamming_filter
    elif filter == "hann":
        hanning_filter = np.fft.fftshift(np.hanning(projection_size_padded))
        fourier_filter *= hanning_filter
    elif filter is None:
        fourier_filter[:] = 1
    else:
        raise ValueError("Unknown filter: %s" % filter)
    # Apply filter in Fourier domain
    projection = fft(img, axis=0) * fourier_filter[:, np.newaxis]
    radon_filtered = np.real(ifft(projection, axis=0))

    # Resize filtered image back to original size
    radon_filtered = radon_filtered[:radon_image.shape[0], :]
    reconstructed = np.zeros((output_size, output_size))
    # Determine the center of the projections (= center of sinogram)
    mid_index = np.ceil(radon_image.shape[0] / 2)

    [X, Y] = np.mgrid[1:output_size+1, 1:output_size+1]
    xpr = X - int(output_size) // 2
    ypr = Y - int(output_size) // 2
    
    # pad the filtered image
    padded_size = 2*np.ceil(output_size/np.sqrt(2)) + 1
    if radon_image.shape[0] < padded_size:
        num_extra_rows = padded_size - radon_image.shape[0]
        pad_width = ((int(np.ceil(num_extra_rows/2)),int(np.floor(num_extra_rows/2))), (0,0))
        radon_filtered = np.pad(radon_filtered, pad_width, mode='constant', constant_values=0)
        mid_index += np.ceil(num_extra_rows/2)

    # Reconstruct image by interpolation
    for i in range(len(theta)):
        t = ypr * np.cos(th[i]) - xpr * np.sin(th[i])
        x = np.arange(1, radon_filtered.shape[0]+1) - mid_index
        if interpolation == 'linear':
            backprojected = np.interp(t, x, radon_filtered[:, i],
                                      left=0, right=0)
        else:
            interpolant = interp1d(x, radon_filtered[:, i], kind=interpolation,
                                   bounds_error=False, fill_value=0)
            backprojected = interpolant(t)
        reconstructed += backprojected
    if circle:
        radius = output_size // 2
        reconstruction_circle = (xpr ** 2 + ypr ** 2) <= radius ** 2
        reconstructed[~reconstruction_circle] = 0.

    return reconstructed * np.pi / (2 * len(th))

def _sinogram_circle_to_square(sinogram):
    diagonal = int(np.ceil(np.sqrt(2) * sinogram.shape[0]))
    pad = diagonal - sinogram.shape[0]
    old_center = sinogram.shape[0] // 2
    new_center = diagonal // 2
    pad_before = new_center - old_center
    pad_width = ((pad_before, pad - pad_before), (0, 0))
    return np.pad(sinogram, pad_width, mode='constant', constant_values=0)