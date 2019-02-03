# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# ------------------------------------
# Authors:    Luis Miguel Sanchez Brea and Jesus del Hoyo
# Date:       2019/01/09 (version 1.0)
# License:    GPL
# -------------------------------------
"""
We present a number of functions for polarization using Jones framework:

**Light beams**
    * **from_elements**: Creates a Jones vector directly from $E_x$ and $E_y$.
    * **from_matrix**: Creates a Jones vector directly from a 2x1 matrix.
    * **from_Stokes**: Creates a Jones vector from a Stokes object. Take into account that only pure (totally polarized) Stokes vectors must be transformed to Jones vectors, and thet even for them, the global phase is unknown.
    * **linear_light**: Creates a state of linear polarization with the desired angle.
    * **circular_light**: Creates a state of circular polarization.
    * **eliptical_light**: Creates a state of eliptical polarization.
    * **general_azimuth_ellipticity**: Creates a Jones vector from the azimuth, ellipticity and amplitude parameters.
    * **general_carac_angles**: Creates a Jones vector from tthe caracteristic angles and amplitude parameters.

**Parameters**
    * **intensity**:         Calculates the intensity of the Jones vector.
    * **alpha**:             Calculates the ratio between amplitude of components Ex/Ey of electric field.
    * **azimuth**:           Calculates azimuth, that is, the orientation of major axis.
      **delay**:             Calculates the delay (phase shift) between Ex and Ey components of the electric field.
    * **ellipticity_angle**: Calculates the ellipticity angle.
    * **length_axes**:       Calculates the length of major and minor axis (a,b).

    * **get_all**:           Returns a dictionary with all the parameters of Jones vector.
"""

import warnings
from cmath import exp as cexp
from functools import wraps

from scipy import cos, exp, matrix, sin, sqrt

from . import degrees, np, num_decimals
from .drawings import draw_ellipse_jones
from .utils import (carac_angles_2_azimuth_elipt, put_in_limits, repair_name,
                    rotation_matrix_Jones)

warnings.filterwarnings('ignore', message='PendingDeprecationWarning')


class Jones_vector(object):
    """Class for Jones vectors

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
        self.M = np.matrix(np.array([[0], [0]]))
        self.parameters = Parameters_Jones_Vector(self.M, self.name)

    def __add__(self, other):
        """Adds two Jones vectors.

        Parameters:
            other (Jones): 2nd Jones vector to add

        Returns:
            JOnes: `s3 = s1 + s2`
        """

        j3 = Jones_vector()
        j3.from_matrix(self.M + other.M)
        j3.name = self.name + " + " + other.name
        j3.update()

        return j3

    def __sub__(self, other):
        """Substracts two Jones vectors.

        Parameters:
            other (Jones): 2nd Jones vector to add

        Returns:
            Jones: `s3 = s1 - s2`
        """

        j3 = Jones_vector()
        j3.from_matrix(self.M - other.M)
        j3.name = self.name + " - " + other.name
        j3.update()

        return j3

    def __mul__(self, other):
        """Multiplies a Jones vectors by a number.

        Parameters:
            other (Mueller): number to multiply

        Returns:
            Stokes: `s3 = number * s2`
        """
        M3 = Jones_vector()

        if isinstance(other, (int, float, complex)):
            M3.M = self.M * other
        else:
            raise ValueError('other is Not number')
        M3.update()
        return M3

    def __rmul__(self, other):
        """Multiplies a Jones vectors by a number.

        Parameters:
            other (Mueller): number to multiply

        Returns:
            Stokes: `s3 =  s2 * number`
        """
        # INFO: quito r_mul pues da problems con
        M3 = Jones_vector()

        if isinstance(other, (int, float, complex)):
            M3.M = other * self.M
        # elif isinstance(other, Jones_matrix):
        #     print("in __rmul__ jones vector")
        #     M3.M = other.M * self.M
        else:
            raise ValueError('other is Not number')
        M3.update()
        return M3

    def __repr__(self):
        """
        represents jones vector with print()
        """
        # TODO: si J1 = [+0.500-0.500j; +0.500+0.500j]' cambiar a más visible
        M = np.array(self.M).squeeze()
        M = np.round(M, num_decimals)
        l_name = "{} = ".format(self.name)
        difference = abs(M.round() - M).sum()

        l0 = "[{}; {}]'".format(M[0], M[1])
        # if M[0] > 0 and M[1] > 0:
        #     if difference > eps:
        #         l0 = "[{:1.3f}; {:1.3f}]'".format(M[0], M[1])
        #     else:
        #         l0 = "[{:1.0f}; {:1.0f}]'".format(M[0], M[1])
        #
        #     if difference > eps:
        #         l0 = "[{:+1.3f}; {:+1.3f}]'".format(M[0], M[1])
        #     else:
        #         l0 = "[{:+1.0f}; {:+1.0f}]'".format(M[0], M[1])
        # else:
        #     if difference > eps:
        #         l0 = "[{:+1.3f}; {:+1.3f}]'".format(M[0], M[1])
        #     else:
        #         l0 = "[{:+1.0f}; {:+1.0f}]'".format(M[0], M[1])
        #
        #     if difference > eps:
        #         l0 = "[{:+1.3f}; {:+1.3f}]'".format(M[0], M[1])
        #     else:
        #         l0 = "[{:+1.0f}; {:+1.0f}]'".format(M[0], M[1])

        return l_name + l0

    def update(self):
        # print("inside update")
        self.parameters.M = self.M
        self.parameters.name = self.name
        self.parameters.get_all()

    def get(self):
        return self.M

    @_actualize_
    def check(self, verbose=False):
        """Verifies that is a Jones vector is properly defined
        References:
            R. Martinez-Herrero, P.M. Mejias, G.Piquero "Characterization of partially polarized light fields" Springer series in Optical sciences (2009) ISBN 978-3-642-01326-3, page 3, eqs. 1.4a and 1.4b.
        """
        det1 = np.linalg.det(self.M)
        trace1 = np.trace(self.M * self.M.H)
        condition1 = np.abs(det1)**2 <= 1  # eq. 1.4a
        condition2 = trace1 >= 0 and trace1 <= 2

        if verbose is True:
            print("condition 1: {0}".format(condition1))
            print("condition 2: {0}".format(condition2))

        return condition1 * condition2

    @_actualize_
    def rotate(self,
               angle=0 * degrees,
               keep=True,
               returns_matrix=False,
               is_repair_name=True):
        """Rotates a jones_matrix a certain angle

        M_rotated = rotation_matrix_Jones(-angle) * self.M

        Parameters:
            angle (float): angle of rotation in radians.
            keep (bool): if True self.M is updated. If False, it returns matrix and it is not updated in self.M.
            returns_matrix (bool): if True returns a matrix, else returns an instance to object
            is_repair_name (bool): if True tries to repair name with @ rot @ rot -> @ 2*rot
        """

        if angle != 0:
            M_rotated = rotation_matrix_Jones(-angle) * self.M
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
            j3 = Jones_vector()
            j3.M = M_rotated
            j3.name = self.name
            if angle != 0:
                j3.name = j3.name + " @{:1.2f}º".format(angle / degrees)
                if is_repair_name is True:
                    j3.name = repair_name(j3.name)
            j3.update()
            return j3

    def draw(self, filename='', size=''):
        """Draws polarization ellipse of Jones vector.

        Arguments:
            filename (str): name of filename to save the figure.
            size (float): size for drawing. If empty it is obtained from amplitudes.


        Returns:
            ax (handle): handle to axis.
            fig (handle): handle to figure.
        """

        ax, fig = draw_ellipse_jones(self, filename='', size='')
        return ax, fig

    @_actualize_
    def clear(self):
        """Removes data and name form Jones vector.
        """
        self.from_elements(0, 0)
        self.name = ''
        return self.M

    @_actualize_
    def from_elements(self, v0, v1):
        """2x1 Custom Jones vector (v0, v1)

        Parameters:
            v0 (float): first element v[0]
            v1 (float): first element v[1]

        Returns:
            (numpy.matrix) 2x1 matrix
        """

        self.M = matrix([[v0], [v1]])
        return self.M

    @_actualize_
    def from_matrix(self, M):
        """Create a Jones vector from an external matrix.

        Parameters:
            M (2x1 numpy matrix): New matrix

        Returns:
            (numpy.matrix) 2x1 matrix
        """
        self.M = M
        return self.M

    @_actualize_
    def from_Stokes(self, S, disable_warning=False):
        """Create a Jones vector from a Stokes vector. This operation is
        ambiguous, as many Jones vectors corresponds to a single pure Stokes
        vector (all of them with a global phase difference up to 2*pi). Also,
        this operation is only meaningful for pure (totally polarized) Stokes
        vectors. For the rest of them, only the polarized part is transformed,
        and a warning is printed.

        Parameters:
            S (Stokes object): Stokes vector
            disable_warning (bool): When a partial-polarized beam is used, the
                method prints a warning. If this parameter is set to False, no
                warnings are printed.

        Returns:
            j (numpy 2x1 matrix): Jones vector.
        """
        # If the vector is not a pure vector, show a # WARNING.
        DOP = S.parameters.degree_polarization()
        if DOP < 1 and not disable_warning:
            warnings.warn(
                'Non-pure Stokes vector transformed into a Jones vector')
        # Extract the matrix from the polarized part of the vector
        if DOP < 1:
            Smat, _ = S.parameters.polarized_unpolarized()
            S.from_matrix(Smat)
        # Calculate amplitude, azimuth and ellipticity of the vector
        amplitude = sqrt(S.parameters.intensity())
        az = S.parameters.azimuth()
        el = S.parameters.ellipticity_angle()
        # Generate a Jones vector from those parameters
        self.general_azimuth_ellipticity(az, el, amplitude)

        return self.M

    # @_actualize_
    # def to_Stokes(self, p=1):
    #     """Function that converts Jones light states to Stokes states.
    #     Parameters:
    #         p (float or 1x2 float): Degree of polarization, or
    #             [linear, circular] degrees of polarization.
    #     Returns:
    #         S (Stokes object): Stokes state."""
    #     # Check if we are using linear/circular or global polarization degree
    #
    #     if np.size(p) T 1:
    #         (p1, p2) = (p, p)
    #     else:
    #         (p1, p2) = (p[0], p[1])
    #
    #     E = self.M
    #     # Calculate the vector
    #     (Ex, Ey) = (E[0], E[1])
    #     S = np.zeros([1, 4])
    #     s0 = abs(Ex)**2 + abs(Ey)**2
    #     s1 = (abs(Ex)**2 - abs(Ey)**2) * p1
    #     s2 = 2 * np.real(Ex * np.conj(Ey)) * p1
    #     s3 = -2 * np.imag(Ex * np.conj(Ey)) * p2
    #
    #     S1 = Stokes(self.name)
    #     S1.from_elements(s0, s1, s2, s3)
    #     return S1

    @_actualize_
    def linear_light(self, amplitude=1, angle=0 * degrees):
        """2x1 Jones vector for polarizer linear light

        Parameters:
            angle (float): angle of polarization (azimuth).

        Returns:
            (numpy.matrix) 2x1 matrix
        """

        self.M = amplitude * matrix([[cos(angle)], [sin(angle)]])
        return self.M

    @_actualize_
    def circular_light(self, amplitude=1, kind='d'):
        """2x1 Jones vector for polarizer circular light

        Parameters:
            kind (str): 'd','r' - right, dextro, derecha.
                        'l', 'i' - left, levo, izquierda.

        Returns:
            (numpy.matrix) 2x1 matrix
        """
        # Definicion del vector de Jones a dextrogiro o levogiro
        a0 = amplitude / sqrt(2)
        if kind in 'dr':  # derecha, right
            self.M = np.matrix([[a0], [a0 * 1j]])
        elif kind in 'il':  # izquierda, left
            self.M = np.matrix([[a0], [-a0 * 1j]])
        return self.M

    @_actualize_
    def elliptical_light(self, a=1, b=1, phase=0, angle=0):
        """2x1 Jones vector for polarizer elliptical light

        Parameters:
            a (float): amplitude of x axis
            b (float): amplitude of y axis
            phase (float): phase shift between axis
            angle (float): rotation_matrix_Jones angle respect to x axis

        Returns:
            (numpy.matrix) 2x1 matrix
        """

        # Definicion del vector de Jones
        M = matrix([[a], [b * exp(1j * phase)]], dtype=complex)
        self.M = rotation_matrix_Jones(angle) * M
        return self.M

    @_actualize_
    def general_azimuth_ellipticity(self, az=0, el=0, amplitude=1):
        """2x1 Jones vector from azimuth, ellipticity angle and amplitude parameters.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016),     pp 6.

        Parameters:
            az (float): [0, pi]: azimuth.
            el (float): [-pi/4, pi/4]: ellipticity angle.
            amplitude (float): field amplitude

        Returns:
            (numpy.matrix) 2x1 matrix
        """

        if az is np.nan and el is np.nan:
            raise ValueError(
                "general_azimuth_ellipticity: need total polarized light ")
        elif az is np.nan:
            j1 = 1 / np.sqrt(2)
            j2 = 1j * np.sign(el) / np.sqrt(2)
        else:
            j1 = cos(el) * cos(az) - 1j * sin(el) * sin(az)
            j2 = cos(el) * sin(az) + 1j * sin(el) * cos(az)
        self.M = amplitude * np.matrix(np.array([[j1], [j2]]))
        return self.M

    @_actualize_
    def general_carac_angles(self, alpha=0, delay=0, amplitude=1):
        """2x1 Jones vector from caracteristic angles and amplitude parameters.

        References:
        J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016), pp 137.

        Parameters:
            alpha (float):
            delta (float):
            amplitude (float): field amplitude

        Returns:
            numpy.matrix: 2x1 matrix
        """
        j1 = cos(alpha) * cexp(-1j * delay / 2)
        j2 = sin(alpha) * cexp(1j * delay / 2)
        self.M = amplitude * np.matrix(np.array([[j1], [j2]]))
        return self.M


class Parameters_Jones_Vector(object):
    """Class for Jones vector Parameters

    Parameters:
        jones_vector (Jones_vector): Jones Vector

    Attributes:
        self.M (Jones_vector)
    """

    def __init__(self, Jones_vector, name=''):
        self.M = Jones_vector
        self.name = name
        self.dict_params = {}
        self.dict_params['E0x'] = float(np.abs(self.M[0]))
        self.dict_params['E0y'] = float(np.abs(self.M[1]))
        self.dict_params['delay'] = float(np.angle(self.M[1])) - float(
            np.angle(self.M[0]))

    def __repr__(self):
        """print all parameters"""
        self.get_all()
        a, b = self.length_axes()
        text = "parameters of {}:\n".format(self.name)
        text = text + "    intensity        : {:2.3f} arb.u\n".format(
            self.dict_params['intensity'])
        text = text + "    alpha            : {:2.3f}º\n".format(
            self.dict_params['alpha'] / degrees)
        text = text + "    delay            : {:2.3f}º\n".format(
            self.dict_params['delay'] / degrees)
        text = text + "    azimuth          : {:2.3f}º\n".format(
            self.dict_params['azimuth'] / degrees)
        text = text + "    ellipticity angle: {:2.3f}º\n".format(
            self.dict_params['ellipticity_angle'] / degrees)
        text = text + "    a, b             : {:2.3f}  {:2.3f}\n".format(a, b)
        return text

    def get_all(self):
        """Returns a dictionary with all the parameters of Jones vector."""
        self.dict_params['E0x'] = float(np.abs(self.M[0]))
        self.dict_params['E0y'] = float(np.abs(self.M[1]))
        self.dict_params['intensity'] = self.intensity()
        self.dict_params['alpha'] = self.alpha()
        self.dict_params['delay'] = self.delay()
        self.dict_params['azimuth'] = self.azimuth()
        self.dict_params['ellipticity_angle'] = self.ellipticity_angle()
        self.dict_params['length_axes'] = self.length_axes()

    def intensity(self, verbose=False):
        """Calculates the intensity of the Jones vector.

        Parameters:
            verbose (bool): if True prints the intensity

        Returns:
            (float): intensity
        """
        E0x = float(np.abs(self.M[0]))
        E0y = float(np.abs(self.M[1]))
        i1 = float(E0x**2 + E0y**2)

        if verbose:
            print("Intensity: {} arb. u.".format(i1))

        return i1

    # def irradiance_proposal(self):
    #     # TODO: (Jesus) Futuro.
    #     pass

    def alpha(self):
        """Calculates the ratio between amplitude of components Ex/Ey of electric field.

        References:
            D. Golstein "Polarized light" 2nd ed Marcel Dekker (2003), 3.4 eq.3-35

        Returns:
            (float): alpha ratio

        """
        E0x = float(np.abs(self.M[0]))
        E0y = float(np.abs(self.M[1]))
        alpha = np.arctan2(E0y, E0x)
        alpha = put_in_limits(alpha, 'alpha')
        return alpha

    def azimuth(self):
        """Calculates azimuth, that is, the orientation of major axis.

        References:
            D. Golstein "Polarized light" 2nd ed Marcel Dekker (2003), 3.4 eq.3-33b

        Returns:
            (float): azimuth
        """

        E0x = float(np.abs(self.M[0]))
        E0y = float(np.abs(self.M[1]))
        delay = self.delay()

        psi = np.arctan2(2 * E0x * E0y * cos(delay), E0x**2 - E0y**2) / 2
        psi = put_in_limits(psi, 'azimuth')

        return psi

    def delay(self):
        """Calculates the delay (phase shift) between Ex and Ey components of the electric field.

        References:
            D. Golstein "Polarized light" 2nd ed Marcel Dekker (2003), 3.4 eq.3-33b

        Returns:
            (float): delay
        """
        delta = float(np.angle(self.M[1])) - float(np.angle(self.M[0]))
        delta = put_in_limits(delta, 'delta')

        return delta

    def ellipticity_angle(self):
        """Calculates the ellipticity angle.

        References:
            J. J. Gil, "Polarized light and the Mueller Matrix approach", pp 137 and 154.

        Returns:
            (float): Ellipticity_angle
        """
        alpha = self.alpha()
        delta = self.delay()
        az, el = carac_angles_2_azimuth_elipt(alpha, delta)
        el = put_in_limits(el, 'ellipticity')

        return el

    def length_axes(self):
        """Calculates the length of major and minor axis (a,b)

        References:
            D. Golstein "Polarized light" 2nd ed Marcel Dekker (2003), 3.4 eq.3-30a and 3-30b

        Returns:
            (float, float): (a,b) length of major and minor axis
        """
        E0x = float(np.abs(self.M[0]))
        E0y = float(np.abs(self.M[1]))
        delay = self.delay()
        az = self.azimuth()

        a2 = E0x**2 * cos(az)**2 + E0y**2 * sin(az)**2 + 2 * E0x * E0y * cos(
            az) * sin(az) * cos(delay)
        b2 = E0x**2 * sin(az)**2 + E0y**2 * cos(az)**2 - 2 * E0x * E0y * cos(
            az) * sin(az) * cos(delay)

        a = np.sqrt(a2)
        b = np.sqrt(b2)

        return a, b
