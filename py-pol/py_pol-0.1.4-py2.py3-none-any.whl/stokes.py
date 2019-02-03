# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# ------------------------------------
# Authors:    Luis Miguel Sanchez Brea and Jesus del Hoyo
# Date:       2019/01/09 (version 1.0)
# License:    GPL
# -------------------------------------
"""
We present a number of functions for polarization using Stokes framework:

**Light beams**
    * **from_elements**: Creates a 4x1 Stokes vector directly from the 4 elements [s0, s1, s2, s3].
    * **from_matrix**: Creates a 4x1 Stokes vector from an external matrix.
    * **from_Jones**: Creates a 4x1 Stokes vector from a 2x1 Jones vector.
    * **linear_light**: Creates a 4x1 Stokes vector for pure linear polarizer light.
    * **circular_light**: Creates a 4x1 Stokes vector for pure circular polarizer light.
    * **elliptical_light** Creates a 4x1 Stokes vector for polarizer elliptical light.
    * **general_carac_angles** Creates a 4x1 Stokes vector given by their caracteristic angles.
    * **general_azimuth_ellipticity** Creates a 4x1 Stokes vector given by their azimuth and ellipticity.

**Methods**
    * **check**: Checks that Stokes vector stored in .M is a correct 4x1 matrix.
    * **rotate**: Rotates the Stokes vector.
    * **depolarize**. Depolarize the Stokes vector stored in .M.

**Properties**
    * **intensity**:   Calculates the intensity of the Stokes vector.
    * **degree_pol**:   Calculates the degree of polarization (DOP) of the Stokes vector.
    * **degree_linear_pol**:     Calculates the degree of linear polarization (DOLP) of the Stokes vector.
    * **degree_circular_pol**:     Calculates the degree of circular polarization (DOCP) of the Stokes vector.
    * **ellipticity**:            When the beam is *fully polarized*, calculates the ellipticity, that is, the ratio between semi-axis.
    * **azimuth**:     When the beam is *fully polarized*, calculates the orientation of major axis. If S is not fully polarized, ellipticity is computed on Sp
    * **eccentricity**:     When the beam is *fully polarized*, calculates the eccentricity of Stokes vector. If S is not fully polarized, ellipticity is computed on Sp.
    * **ellipse_parameters**:     Calculates the three parameters: ellipticity, azimuth, eccentricity at the same time.
    * **polarized_unpolarized**:     Divides the Stokes vector in Sp+Su, where Sp is fully-polarized and Su fully-unpolarized
"""
from functools import wraps

import numpy as np
from numpy import arctan2, array, cos, matrix, pi, sin, sqrt

from . import eps, num_decimals
from .drawings import draw_ellipse_stokes, draw_poincare_sphere
from .jones_vector import Jones_vector
from .utils import (azimuth_elipt_2_carac_angles, put_in_limits, repair_name,
                    rotation_matrix_Mueller)

degrees = pi / 180.
stokes_0 = np.matrix(np.zeros((4, 1)), dtype=float)

# TODO: función para luz eliptica (a, b, angulo, polarización)? No sabía hacer


# define Python user-defined exceptions
class Error(Exception):
    """Base class for other exceptions"""
    pass


class CustomError(Error):
    """Raised when a custom error is produced"""
    pass


class Stokes(object):
    """Class for Stokes vectors

    Parameters:
        name (str): name of vector for string representation

    Attributes:
        self.M (numpy.matrix): 4x1 array
        self.parameters (class): parameters of stokes
    """

    def _actualize_(f):
        @wraps(f)
        def wrapped(inst, *args, **kwargs):
            result = f(inst, *args, **kwargs)
            inst.update()
            return result

        return wrapped

    def __init__(self, name='J'):
        self.name = name
        self.M = np.matrix(np.zeros((4, 1), dtype=float))
        self.parameters = Parameters_Stokes_vector(self.M)

    def __add__(self, other):
        """Adds two Stokes vectors considering that are mutually incoherent

        Parameters:
            other (Stokes): 2nd Stokes vector to add

        Returns:
            Stokes: `s3 = s1 + s2`
        """
        # self.parameters.M = self.M
        # # Calculate I and V parameters of the new Stokes vector, that are easy
        # s0 = sqrt(np.float(self.M[0]**2 + other.M[0]**2))
        # s3 = sqrt(np.float(self.M[3]**2 + other.M[3]**2))
        # # Extract "norm" of linear part of vectors
        # norm1 = self.parameters.degree_linear_polarization()
        # norm2 = other.parameters.degree_linear_polarization()
        # # Extract "angle" of linear part of vectors
        # az1 = self.parameters.azimuth()
        # az2 = other.parameters.azimuth()
        # # Add them as vectors
        # v1 = np.array([norm1 * cos(az1), norm1 * sin(az1)])
        # v2 = np.array([norm2 * cos(az2), norm2 * sin(az2)])
        # v3 = v1 + v2
        # # Calculate norm and angle of final vector
        # norm3 = np.linalg.norm(v3)
        # if norm3 == 0:
        #     (s1, s2) = (0, 0)
        # else:
        #     az3 = arccos(v3[0] / norm3)
        #     s1 = norm3 * cos(2 * az3)
        #     s2 = norm3 * sin(2 * az3)
        # # Put the new result in M3
        M3 = Stokes()
        M3.from_matrix(self.M + other.M)
        M3.name = self.name + " + " + other.name
        M3._actualize_()

        return M3

    def __sub__(self, other):
        """Substracts two Stokes vectors considering that are mutually incoherent

        Parameters:
            other (Stokes): 2nd Stokes vector to add

        Returns:
            Stokes: `s3 = s1 - s2`
        """
        M3 = Stokes()
        M3.from_matrix(self.M - other.M)
        M3.name = self.name + " - " + other.name
        M3._actualize_()

        return M3

    def __mul__(self, other):
        """Multiplies vector * number.

        Parameters:
            other (number): number to multiply

        Returns:
            Stokes: `s3 = number * s1`
        """
        M3 = Stokes()

        if isinstance(other, (int, float, complex)):
            M3.M = self.M * other
        else:
            raise ValueError('other is Not number')
        M3._actualize_()
        return M3

    def __rmul__(self, other):
        """Multiplies vector * number.

        Parameters:
            other (number): number to multiply

        Returns:
            Stokes: `s3 =  s1 * number`
        """
        M3 = Stokes()

        if isinstance(other, (int, float, complex)):
            M3.M = other * self.M

        else:
            raise ValueError('other is Not number')
        M3._actualize_()
        return M3

    def __repr__(self):
        M = np.array(self.M).squeeze()
        M = np.round(M, num_decimals)
        l_name = "{} = ".format(self.name)
        difference = abs(self.M.round() - self.M).sum()
        if difference > eps:
            l0 = "[{:+3.3f}; {:+3.3f}; {:+3.3f}; {:+3.3f}]\n".format(
                M[0], M[1], M[2], M[3])
        else:
            l0 = "[{:+3.0f}; {:+3.0f}; {:+3.0f}; {:+3.0f}]\n".format(
                M[0], M[1], M[2], M[3])
        return l_name + l0

    # def sum_coherent_proposal(self, params):
    #     """
    #     proposal of function that sums Stokes vector when their coherent part
    #     is mutually coherent.
    #
    #     steps:
    #         * Separate coherent and incoherent parts
    #         * pass coherent parts to Jones_vector
    #         * sum Jones vectors
    #         * pass to Stokes
    #     """
    # s1 = np.float(self.M[3] + other.M[3])
    # s3 = np.float(self.M[3] + other.M[3])
    # s0 = np.sqrt(np.float(self.M[0]**2 + other.M[0]**2))
    # s3 = np.sqrt(np.float(self.M[3]**2 + other.M[3]**2))
    #
    # # Extract "norm" of linear part of vectors
    # norm1 = self.parameters.degree_linear_polarization()
    # norm2 = other.parameters.degree_linear_polarization()
    # # Extract "angle" of linear part of vectors
    # az1 = self.parameters.azimuth()
    # az2 = other.parameters.azimuth()
    # # Add them as vectors
    # v1 = np.array([norm1 * cos(az1), norm1 * sin(az1)])
    # v2 = np.array([norm2 * cos(az2), norm2 * sin(az2)])
    # v3 = v1 + v2
    # # Calculate norm and angle of final vector
    # norm3 = np.linalg.norm(v3)
    # if norm3 == 0:
    #     (s1, s2) = (0, 0)
    # else:
    #     az3 = arccos(v3[0] / norm3)
    #     s1 = norm3 * cos(2 * az3)
    #     s2 = norm3 * sin(2 * az3)
    # # Put the new result in M3
    # M3 = Stokes(self.name + " + " + other.name)
    # M3.from_elements(s0, s1, s2, s3)
    # return M3
    # pass

    def update(self):
        """actualizes self.parameters.M = self.M"""
        # print("inside set")
        self.parameters.M = self.M
        self.parameters.name = self.name
        # print(self.parameters.M)

    def get(self):
        """get self.M stokes vector"""
        return self.M

    def check(self, verbose=False):
        """
        verifies that (s0,s1,s2,s3) Stokes vector is properly defined
        verifies that is a 4x1 numpy.matrix
        """

        s0 = np.asscalar(self.M[0])
        s1 = np.asscalar(self.M[1])
        s2 = np.asscalar(self.M[2])
        s3 = np.asscalar(self.M[3])

        # intensity >0
        condition1 = s0 >= 0

        condition2 = s0**2 >= s1**2 + s2**2 + s3**2

        if verbose is True:
            print("s0 >= 0:                         {0}".format(condition1))
            print("s0**2 >= s1**2 + s2**2 + s3**2:  {0}".format(condition2))

        return condition1 * condition2

    @_actualize_
    def rotate(self,
               angle=0 * degrees,
               keep=True,
               returns_matrix=False,
               is_repair_name=True):
        """Rotation of a Stokes vector

        M_rotated= rotation_matrix_Jones(-angle) * M

        Parameters:
            angle (float): angle of rotation_matrix_Jones in radians.
            keep (bool): if True self.M is updated. If False, it returns matrix and it is not updated in self.M.
            returns_matrix (bool): if True returns a matrix, else returns an instance to object
            is_repair_name (bool): if True tries to repair name with @ rot @ rot -> @ 2*rot
        """

        if angle != 0:
            M_rotated = rotation_matrix_Mueller(-angle) * self.M
        else:
            M_rotated = self.M

        if keep is True:
            if angle != 0:
                self.name = self.name + " @{:1.2f}º".format(angle / degrees)
                if is_repair_name is True:
                    self.name = repair_name(self.name)
            self.M = M_rotated
            # return ?

        if returns_matrix is True:
            return M_rotated
        else:
            j3 = Stokes()
            j3.M = M_rotated
            j3.name = self.name
            if angle != 0:
                j3.name = j3.name + " @{:1.2f}º".format(angle / degrees)
                if is_repair_name is True:
                    j3.name = repair_name(j3.name)
            j3.update()
            return j3

    @_actualize_
    def rotate_deprecated(self, angle=0 * degrees, keep=True):
        """Rotation of a Stokes vector

        M_rotated= rotation_matrix_Jones(-angle) * M

        Parameters:
            angle (float): angle of rotation_matrix_Jones in radians.
            keep (bool): if True self.M is updated. If False, it returns matrix and it is not updated in self.M.

        """
        if angle != 0:
            M_rotated = rotation_matrix_Mueller(-angle) * self.M
            self.name = self.name + " @{:1.2f}º".format(angle / degrees)
            # self.name = repair_name(self.name)
        else:
            M_rotated = self.M

        if keep is True:
            self.M = M_rotated

        return M_rotated

    @_actualize_
    def depolarize(self, pol_degree, keep=True):
        """Function that reduces de polarization degree of a Stokes vector
        homogeneously.

        Returns:
            S (4x1 numpy matrix): Stokes state."""

        S = np.matrix(np.zeros((4, 1), dtype=float))

        S[0] = self.M[0]
        S[1] = pol_degree * self.M[1]
        S[2] = pol_degree * self.M[2]
        S[3] = pol_degree * self.M[3]
        if keep is True:
            self.from_matrix(S)
        return S

    @_actualize_
    def clear(self):
        """Removes data and name from stokes vector.
        """
        self.from_elements(0, 0, 0, 0)
        self.name = ''

    @_actualize_
    def from_elements(self, s0, s1, s2, s3):
        """Creates a 4x1 Stokes vector directly from the 4 elements [s0, s1, s2, s3]

        Parameters:
            s0 (float): intensity
            s1 (float): linear 0º-90º polarization
            s2 (float): linear 45º-135º polarization
            s3 (float): circular polarization

        Returns:
            S (4x1 numpy.matrix): Stokes vector.
        """

        a = np.matrix(np.zeros((4, 1), dtype=float))
        a[0] = s0
        a[1] = s1
        a[2] = s2
        a[3] = s3

        self.M = a
        return self.M

    @_actualize_
    def from_matrix(self, M):
        """Creates a 4x1 Stokes vector from an external matrix.

        Parameters:
            M (4x1 numpy matrix): New matrix

        Returns:
            np.matrix 4x1 numpy.matrix
        """
        self.M = M
        return self.M

    @_actualize_
    def from_Jones(self, j, pol_degree=1):
        """Creates a 4x1 Stokes vector from a 2x1 Jones vector.

        Parameters:
            j (Jones_vector object): Jones vector
            p (float or 1x2 float): Degree of polarization, or
                [linear, circular] degrees of polarization.

        Returns:
            S (4x1 numpy.matrix): Stokes vector.
        """

        if np.size(pol_degree) == 1:
            (p1, p2) = (pol_degree, pol_degree)
        else:
            (p1, p2) = (pol_degree[0], pol_degree[1])

        E = j.M
        # Calculate the vector
        (Ex, Ey) = (E[0], E[1])
        s0 = abs(Ex)**2 + abs(Ey)**2
        s1 = (abs(Ex)**2 - abs(Ey)**2) * p1
        s2 = 2 * np.real(Ex * np.conj(Ey)) * p1
        s3 = -2 * np.imag(Ex * np.conj(Ey)) * p2

        self.from_elements(s0, s1, s2, s3)

    # @_actualize_
    # def to_Jones(self):
    #     """Function that converts Stokes light states to Jones states.
    #
    #     Returns:
    #         j (Jones_vector object): Stokes state."""
    #     j = Jones_vector(self.name)
    #     j.from_Stokes(self)
    #     return j

    @_actualize_
    def linear_light(self, angle=0, intensity=1):
        """Creates a 4x1 Stokes vector for pure linear polarizer light.

        Parameters:
            angle (float): angle of polarization axis with respect to 0º.
            intensity (float): Intensity of the light

        Returns:
            np.matrix 4x1 Stokes parameters
        """
        self.general_azimuth_ellipticity(
            intensity=intensity, az=angle, el=0, pol_degree=1)
        return self.M

    @_actualize_
    def circular_light(self, kind='d', intensity=1):
        """Creates a 4x1 Stokes vector for pure circular polarizer light

        Parameters:
            kind (str): 'd','r' - right, dextro, derecha.
                        'l', 'i' - left, levo, izquierda.
            intensity (float): Intensity of the light

        Returns:
            np.matrix 4x1 Stokes parameters
        """
        # TODO: LM - no funciona esta definción en tests
        if kind in 'dr':  # derecha, right
            self.general_carac_angles(
                alpha=45 * degrees,
                delay=90 * degrees,
                intensity=1,
                pol_degree=1)

        elif kind in 'il':  # izquierda, left
            self.general_carac_angles(
                alpha=-45 * degrees,
                delay=90 * degrees,
                intensity=1,
                pol_degree=1)
        else:
            print("Not d, r, l, i in kind")

    @_actualize_
    def elliptical_light(self, a=1, b=1, phase=0, angle=0, pol_degree=1):
        """Creates a 4x1 Stokes vector for polarizer elliptical light

        Parameters:
            a (float): amplitude of x axis
            b (float): amplitude of y axis
            phase (float): phase shift between axis
            angle (float): rotation_matrix_Jones angle respect to x axis
            pol_degree (float): [0, 1]: polarization degree.

        Returns:
            np.matrix 4x1 numpy.matrix
        """
        # Calculate it as Jones vector (easier)
        j = Jones_vector()
        j.elliptical_light(a, b, phase, angle)
        # Transform it to Stokes
        self.from_Jones(j)
        # Depolarize
        self.depolarize(pol_degree)
        return self.M

    @_actualize_
    def general_carac_angles(self,
                             alpha=0,
                             delay=0,
                             intensity=1,
                             pol_degree=1,
                             is_depolarization=False):
        """Creates a 4x1 Stokes vector given by their caracteristic angles.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016),pp 137.

        Parameters:
            alpha (float): [0, pi]: tan(alpha) is the ratio between field
                amplitudes of X and Y components.
            delay (float): [0, 2*pi]: phase difference between X and Y field
                components.
            intensity (float): total intensity.
            pol_degree (float): [0, 1]: polarization degree.
            pol (bool): [Default: False] If true, pol_degree is depolarization
                degree instead.

        Returns:
            S (4x1 numpy.matrix): Stokes vector.
        """
        # Change depolarization to polarization degree if required
        if is_depolarization:
            pol_degree = 1 - pol_degree
        # Initialize S
        S = np.matrix(np.array([[1.0], [0.0], [0.0], [0.0]]))
        # Calculate the other three parameters
        S[1] = pol_degree * cos(2 * alpha)
        S[2] = pol_degree * sin(2 * alpha) * cos(delay)
        S[3] = pol_degree * sin(2 * alpha) * sin(delay)
        # Normalize by intensity and return
        self.M = intensity * S
        return self.M

    @_actualize_
    def general_azimuth_ellipticity(self,
                                    az=0,
                                    el=0,
                                    intensity=1,
                                    pol_degree=1,
                                    is_depolarization=False):
        """Creates a 4x1 Stokes vector given by their azimuth and ellipticity.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016), pp 137.

        Parameters:
            az (float): [0, pi]: azimuth.
            el (float): [-pi/4, pi/4]: ellipticity.
            intensity (float): total intensity.
            pol_degree (float): [0, 1]: polarization degree.
            pol (bool): [Default: False] If true, pol_degree is depolarization
                degree instead.

        Returns:
            S (4x1 numpy.matrix): Stokes vector.
        """
        # Change depolarization to polarization degree if required
        if is_depolarization:
            pol_degree = 1 - pol_degree
        # Initialize S
        S = np.matrix(np.array([[1.0], [0.0], [0.0], [0.0]]))
        # Calculate the other three parameters
        if az is np.nan and el is np.nan:
            # total depolarization
            S[1] = 0
            S[2] = 0
            S[3] = 0
        elif az is np.nan:
            # circular polarization
            S[1] = 0
            S[2] = 0
            S[3] = pol_degree * sin(2 * el)
        else:
            S[1] = pol_degree * cos(2 * az) * cos(2 * el)
            S[2] = pol_degree * sin(2 * az) * cos(2 * el)
            S[3] = pol_degree * sin(2 * el)

        # Normalize by intensity and return
        self.M = intensity * S
        return self.M

    def draw_poincare(self,
                      angle_view=[30 * degrees, -60 * degrees],
                      label='s0',
                      filename=''):
        """"Draws stokes vector

            Arguments:
                angle_view (float, float): elevation, azimuth
                label (str): text for label of plot
                filename (str): is not empty saves figure
        """
        ax, fig = draw_poincare_sphere(
            stokes_points=self,
            angle_view=angle_view,
            kind='scatter',
            color='r',
            label=label)

        if filename not in ['', None]:
            fig.savefig(filename)

    def draw_ellipse(self, kind='', size='', has_line=True, filename=''):
        """ Draws polarization ellipse in stokes vector. If unpolarized light is present, a distribution of probability is given.

        Arguments:
            stokes_0 (Stokes): Stokes vector
            kind (str): 'line' 'map'. 'Line': polarized + unpolarized ellipses. 'Map' is for unpolarized. Provides probabilities'
            size (float): size for drawing. If empty itis obtained from ampltiudes
            has_line (bool or float): If True  draws polarized and 0.1 probability lines. If it is a number draws that probability.
            filename (str): if filled, name for drawing

        Returns:
            ax (handle): handle to axis.
            fig (handle): handle to fig
        """

        ax, fig = draw_ellipse_stokes(self, kind, size, has_line, filename)
        return ax, fig


class Parameters_Stokes_vector(object):
    """Class for Stokes vector Parameters

    Parameters:
        Stokes_vector (Stokes_vector): Stokes Vector

    Attributes:
        self.M (Stokes_vector)
        self.dict_params (dict): dictionary with parameters
    """

    def __init__(self, Stokes_vector=stokes_0, name=''):
        self.M = Stokes_vector
        self.name = name
        self.dict_params = {}

    def __repr__(self):
        """print all parameters
        """

        self.get_all()
        polarized, unpolarized = self.polarized_unpolarized()
        E0x, E0y, E0_unpol = self.dict_params['amplitudes']

        text = "parameters of {}:\n".format(self.name)
        text = text + "    intensity             : {:2.3f} arb. u.\n".format(
            self.dict_params['intensity'])
        text = text + "    amplitudes            : E0x {:2.3f}, E0y {:2.3f}, E0_unpol {:2.3f} \n".format(
            E0x, E0y, E0_unpol)
        text = text + "    degree polarization   : {:2.3f}\n".format(
            self.dict_params['degree_pol'])
        text = text + "    degree linear pol.    : {:2.3f}\n".format(
            self.dict_params['degree_linear_pol'])
        text = text + "    degree   circular pol.: {:2.3f}\n".format(
            self.dict_params['degree_circular_pol'])
        text = text + "    alpha                 : {:2.3f}º\n".format(
            self.dict_params['alpha'] / degrees)
        text = text + "    delay                 : {:2.3f}º\n".format(
            self.dict_params['delay'] / degrees)
        text = text + "    azimuth               : {:2.3f}º\n".format(
            self.dict_params['azimuth'] / degrees)
        text = text + "    ellipticity  angle    : {:2.3f}º\n".format(
            self.dict_params['ellipticity_angle'] / degrees)
        text = text + "    ellipticity  param    : {:2.3f}\n".format(
            self.dict_params['ellipticity_param'])
        text = text + "    eccentricity          : {:2.3f}\n".format(
            self.dict_params['eccentricity'])
        text = text + "    polarized vector      : [{:+3.3f}; {:+3.3f}; {:+3.3f}; {:+3.3f}]'\n".format(
            np.asscalar(polarized[0]), np.asscalar(polarized[1]),
            np.asscalar(polarized[2]), np.asscalar(polarized[3]))
        text = text + "    unpolarized vector    : [{:+3.3f}; {:+3.3f}; {:+3.3f}; {:+3.3f}]'\n".format(
            np.asscalar(unpolarized[0]), np.asscalar(unpolarized[1]),
            np.asscalar(unpolarized[2]), np.asscalar(unpolarized[3]))
        return text

    def help(self):
        """prints help about dictionary"""

        text = "Here we explain the meaning of parameters.\n"
        text = text + "    intensity: intensity of the light beam.\n"
        text = text + "    TODO"
        print(text)

    def get_all(self):
        """returns a dictionary with all the parameters of Stokes vector"""
        self.dict_params['intensity'] = self.intensity()
        self.dict_params['amplitudes'] = self.amplitudes()
        self.dict_params['degree_pol'] = self.degree_polarization()
        self.dict_params[
            'degree_linear_pol'] = self.degree_linear_polarization()
        self.dict_params[
            'degree_circular_pol'] = self.degree_circular_polarization()
        self.dict_params['alpha'] = self.alpha()
        self.dict_params['delay'] = self.delay()
        self.dict_params['ellipticity_param'] = self.ellipticity_param()
        self.dict_params['ellipticity_angle'] = self.ellipticity_angle()
        self.dict_params['azimuth'] = self.azimuth()
        self.dict_params['eccentricity'] = self.eccentricity()
        polarized, unpolarized = self.polarized_unpolarized()
        self.dict_params['polarized'] = np.squeeze(
            np.asarray(polarized)).tolist()
        self.dict_params['unpolarized'] = np.squeeze(
            np.asarray(unpolarized)).tolist()
        return self.dict_params

    def intensity(self):
        """
        Calculates the intensity of the Stokes vector.

        References:
            Handbook of Optics vol 2. 22.16 (eq.2)

        Parameters:
            S (array): Stokes vector (s0,s1,s2,s3)

        Returns:
            (float): s0
        """

        return np.asscalar(self.M[0])

    def degree_polarization(self):
        """Calculates the degree of polarization (DOP) of the Stokes vector.


        References:
            Handbook of Optics vol 2. 22.16 (eq.3)

        Parameters:
            S (array): Stokes vector (s0,s1,s2,s3)

        Returns:
            (float): polarization degree P=sqrt(s1**2+s2**2+s3**2)/s0
        """

        s0, s1, s2, s3 = np.array(self.M).flat
        if s0 == 0:
            return np.nan
        else:
            return sqrt(s1**2 + s2**2 + s3**2) / s0

    def degree_linear_polarization(self):
        """Calculates the degree of linear polarization (DOLP) of the Stokes vector.

        References:
            Handbook of Optics vol 2. 22.16 (eq.4)

        Parameters:
            S (array): Stokes vector (s0,s1,s2,s3)

        Returns:
            (float): polarization degree P=sqrt(s1**2+s2**2)/s0
        """

        s0, s1, s2, s3 = np.array(self.M).flat
        if s0 == 0:
            return np.nan
        else:
            return sqrt(s1**2 + s2**2) / s0

    def degree_circular_polarization(self):
        """Calculates the degree of circular polarization (DOCP) of the Stokes vector.
        I have included abs(P) so that it is between (0-1)


        References:
            Handbook of Optics vol 2. 22.16 (eq.5)


        Parameters:
            S (array): Stokes vector (s0,s1,s2,s3)

        Returns:
            (float): polarization degree P=sqrt(s1**2+s2**2)/s0
        """

        s0, s1, s2, s3 = np.array(self.M).flat
        if s0 == 0:
            return np.nan
        else:
            return abs(s3 / s0)

    def alpha(self):
        az = self.azimuth()
        el = self.ellipticity_angle()
        alpha1, delta1 = azimuth_elipt_2_carac_angles(az, el)
        return alpha1

    def delay(self):
        """phase shift between Ex and Ey components.

        Returns:
            (float): delta2-delta1, phase shift
        """
        az = self.azimuth()
        el = self.ellipticity_angle()
        alpha1, delta1 = azimuth_elipt_2_carac_angles(az, el)
        return delta1

    def delta(self):
        """phase shift between Ex and Ey components. Equivalnet to delay

        Returns:
            (float): delta2-delta1, phase shift
        """
        return self.delay()

    def ellipticity_param(self):
        """When the beam is *fully polarized*, calculates the ellipticity, that is, the ratio between semi-axis.

        It's 0 for linearly polarized light and 1 for circulary polarized light

        If S is not fully polarized, ellipticity is computed on Sp

        References:
            Handbook of Optics vol 2. 22.16 (eq.7)

        Parameters:
            S (array): Stokes vector (s0,s1,s2,s3)

        Returns:
            (float): e, ellipticity_param
        """
        S = self.M

        DOP = self.degree_polarization()
        if DOP == 1:
            Sp = S
        else:
            Sp, Su = self.polarized_unpolarized()

        s0, s1, s2, s3 = np.array(Sp).flat
        if s0 == 0 or np.sqrt(s1**2 + s2**2 + s3**2) == 0:
            return np.nan
        else:
            e = s3 / (s0 + np.sqrt(s1**2 + s2**2))

        return e

    def ellipticity_angle(self):
        """Calculates the ratio between the major and minor axis length.

        """
        return np.arctan(self.ellipticity_param())

    def azimuth(self):
        """When the beam is *fully polarized*, calculates the orientation of major axis
        If S is not fully polarized, azimuth is computed on Sp.

        References:
            Handbook of Optics vol 2. 22.16 (eq.8)

        Parameters:
            S (array): Stokes vector (s0,s1,s2,s3)

        Returns:
            (float): azimuth, orientation of major axis
        """

        S = self.M
        DOP = self.degree_polarization()
        if DOP == 1:
            Sp = S
        else:
            Sp, Su = self.polarized_unpolarized()

        s0, s1, s2, s3 = np.array(Sp).flat
        if np.linalg.norm(s1 - 0.) < eps and s2 > 0:
            azimuth = np.pi / 4
        elif np.linalg.norm(s1 - 0.) < eps and s2 < 0:
            azimuth = -np.pi / 4
        elif np.linalg.norm(s1 - 0.) < eps and s2 == 0:
            azimuth = np.nan
        else:
            azimuth = 0.5 * arctan2(s2, s1)

        azimuth = put_in_limits(azimuth, 'azimuth')
        return azimuth

    # def psi(self):
    #     """angle of rotation of the polarization ellipse. Angle of the major axis**
    #     References:
    #         Goldstein Polrized light 2ed (2003) - ec. 3-37
    #         JJ Gil (eq. 1.6)
    #
    #     returns:

    def eccentricity(self):
        """When the beam is *fully polarized*, calculates the eccentricity of Stokes vector.
        If S is not fully polarized, ellipticity_param is computed on Sp


        It is 0 for circular polarized light and 1 for linear polarized light.

        If S is not fully polarized, ellipticity_param is computed on Sp

        References:
            Handbook of Optics vol 2. 22.16 (eq.8)

        Parameters:
            S (array): Stokes vector (s0,s1,s2,s3)

        Returns:
            (float): azimuth, orientation of major axis
        """

        e = self.ellipticity_param()

        return sqrt(1 - e**2)

    def polarized_unpolarized(self):
        """Divides the Stokes vector in Sp+Su, where Sp is fully-polarized and Su fully-unpolarized

        References:
            Handbook of Optics vol 2. 22.16 (eq.6)

        Parameters:
            S (array): Stokes vector (s0,s1,s2,s3)

        Returns:
            (numpy.array): Sp, fully-polarized Stokes vector
            (numpy.array): Su, fully-unpolarized Stokes vector
        """

        DOP = self.degree_polarization()
        s0, s1, s2, s3 = np.array(self.M).flat
        Sp = matrix(array([[s0 * DOP], [s1], [s2], [s3]]))
        Su = matrix(array([[s0 * (1 - DOP)], [0], [0], [0]]))

        return Sp, Su

    def amplitudes(self):
        """Determines the maximum amplitudes of the electric vectors for the polarized and unpolarized part.
        It is useful for drawing

        Returns:
            (float): E0x for the polarized field.
            (float): E0y for the unpolarized field.
            (float): E0_unpol for the unpolarized field
        """
        Sp, Su = self.polarized_unpolarized()
        s0_pol = np.array(Sp[0]).squeeze()
        s0_unpol = np.array(Su[0]).squeeze()
        alpha = self.alpha()
        u0_pol = np.sqrt(s0_pol)
        E0x = u0_pol * np.cos(alpha) + eps
        E0y = u0_pol * np.sin(alpha) + eps
        E0_unpol = np.sqrt(s0_unpol)

        return E0x, E0y, E0_unpol
