# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# ------------------------------------
# Authors:    Luis Miguel Sanchez Brea and Jesus del Hoyo
# Date:       2019/01/09 (version 1.0)
# License:    GPL
# -------------------------------------
"""
We present a number of functions for Mueller matrices:


**Polarizers**

    * **from_elements**: Creates a Mueller matrix directly from the 16 mij elements.
    * **from_matrix**: Creates a Mueller matrix directly from a 2x2 matrix.
    * **vacuum**:  Creates the matrix for vacuum.
    * **filter_amplifier**: Creates the matrix for a neutral filter or amplifier element
    * **polarizer_linear**: Creates a perfect linear polarizer.
    * **diattenuator_linear**: Creates a real polarizer with perpendicular axes.
    * **retarder_linear**: Creates a retarder using delay.
    * **retarder_material**: Creates a retarder using physical properties of a anisotropic material.
    * **diattenuator_retarder_linear**: Creates a linear diattenuator retarder with the same axes for diattenuation and retardance.
    * **diattenuator_carac_angles**: Creates the most general diattenuator with orthogonal eigenstates from the caracteristic angles of the main eigenstate.
    * **diattenuator_azimuth_ellipticity**: Creates the general diattenuator with orthogonal eigenstates from the caracteristic angles of the main eigenstate.

**Methods**
    * **rotate**: Rotates the Jones vector.
    * **divide_in_blocks**: Method that divides a mueller matrix in their blocks D, P, m, m00 components.
    * **check**: Checks that the matrix stored in .M is a correct 2x1 matrix.
    * **clear**: Removes data and name from Jones matrix.


**Polarization properties**

    * **mean_transmission**:  Calculates the mean transmission coefficient.
    * **inhomogeneity**:   Calculates the inhomogeneity parameter.
    * **diattenuation**:     Calculates the diattenuation of a Mueller matrix.
    * **diattenuation_linear**:     Calculates the linear diattenuation of a Mueller matrix.
    * **diattenuation_circular**:    Calculates the circular diattenuation of a Mueller matrix.
    * **polarizance**:   Calculates the polarizance of a Mueller matrix.
    * **polarizance_linear**:  Calculates the linear polarizance of a Mueller matrix.
    * **polarizance_circular**:  Calculates the delay of the matrix.
    * **polarizance_degree**:  Calculates the degree of polarizance.
    * **spheric_purity**:  Calculates the spheric purity grade.
    * **delay**:    Calculates the delay of the Mueller matrix of a pure retarder.
    * **retardance**:    Calculates the retardance vector of the Mueller matrix of a retarder.
    * **polarimetric_purity**:  Calculates the degree of polarimetric purity of a Mueller matrix.
    * **depolarization_degree**: Calculates the depolarization degree of a Mueller matrix.
    * **depolarization_factors**:     Calculates the Euclidean distance and depolarization factor.
    * **polarimetric_purity_indices**:     Calculates the polarimetric purity indices of a Mueller matrix.
    * **diattenuator**:   Calculates all the parameters from the Mueller Matrix of a  diattenuator.
    * **retarder**:  Calculates all the parameters from the Mueller Matrix of a  diattenuator.

**Check consistency of Mueller Matrices

Several parameters can be measured from a Mueller Matrix. They are implemented in the independent class Check_Mueller, which is stored in the *Check* field of Mueller class.

    * **is_real**:  Conditions of physical realizability.
    * **is_non_depolarizing**: Checks if matrix is non-depolarizing (the degree of polarimetric purity must be 1).
    * **is_homogeneous**: Checks if the matrix is homogeneous. The inhomogeneity parameter must be 0 if M is homogeneous.
    * **is_homogeneous2**: Checks if the matrix is homogeneous. A matrix is homogeneous if P == D (vectors).It can be measured from the inhomogeneity parameter.
    * **is_retarder**: Checks if the matrix M corresponds to a pure retarder.
    * **is_diattenuator**: Checks if the matrix M corresponds to a pure homogeneous diattenuator. The condition is M = M^T.
    * **is_singular**: Checks if the matrix is singular. A matrix is homogeneous if det(M) = 0.
    * **is_singular2**: Checks if the matrix is singular. A matrix is singular if any of its eigenvalues is 0.

**Analysis of Mueller Matrices**
Several analysis can be performed from a Mueller Matrix. They are implemented in the independent class Analysis_Mueller, which is stored in the *Analysis* field of Mueller class.

    * **filter_reality_conditions**: Function that filters experimental errors by forcing the Mueller matrix M to fulfill the conditions necessary for a matrix to be real.
    * **decompose_pure**: Polar decomposition of a pure Mueller matrix in a retarder and a diattenuator.
    * **decompose_polar**: Polar decomposition of a general Mueller matrix in a partial depolarizer, retarder and a diattenuator.

    """

from functools import wraps

import numpy as np
from numpy import arctan2, array, cos, exp, matrix, pi, sin, sqrt
from numpy.linalg import inv
from sympy.functions.special.tensor_functions import Eijk

from . import degrees, eps, num_decimals
from .jones_matrix import Jones_matrix
from .stokes import Stokes
from .utils import (azimuth_elipt_2_carac_angles, carac_angles_2_azimuth_elipt,
                    delta_kron, divide_in_blocks, iscolumn, isrow, limAlpha,
                    limDelta, order_eig, put_in_limits, repair_name,
                    rotation_matrix_Mueller)

tol_default = 0.01
counter_max = 20

zero_mueller = np.matrix(np.zeros((4, 4), dtype=float))
# TODO: (Jesus) Revisar ayudas, en especial argumentos de entrada.

# Create a list with the base of matrices
S = [
    np.matrix(np.eye(2)),
    np.matrix(array([[1, 0], [0, -1]])),
    np.matrix(array([[0, 1], [1, 0]])),
    np.matrix(array([[0, -1j], [1j, 0]]))
]


def inverse_covariance(H):
    """Calculates the Mueller matrix from the covariance matrix.

    References:
        J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016)

    Parameters:
        H (numpy.matrix 4x4): Covariance matrix.

    Returns:
        m_obj (Mueller object): Mueller element.

    Warning:
        The base of matrices S is used in an uncommon order.

    Warning:
        In order to obtain the same result as in the book, the formula must be:
        .. math:: H=0.25\sum(m[i,j]\,kron\left[S(i),S(j)^{*}\right].
    """

    m_obj = Mueller()
    M = np.zeros((4, 4), dtype=complex)
    for i in range(4):
        for j in range(4):
            elem = np.trace(np.kron(S[i], np.conj(S[j])) * H)
            # print(elem)
            # print(np.kron(S[i], np.conj(S[j])) * H)
            M[i, j] = elem
            # print([i, j, np.kron(S[i], S[j])])
    m_obj.from_matrix(M)
    return m_obj


class Mueller(object):
    """Class for Mueller matrices

    Parameters:
        name (str): name of Mueller matrix, for string representation

    Attributes:
        self.M (numpy.matrix): 4x4 matrix
        self.parameters (class): parameters of Mueller matrix
        self.analysis (class): analysis of Mueller matrix
        self.check (class): checks of Mueller matrix
    """

    def _actualize_(f):
        @wraps(f)
        def wrapped(inst, *args, **kwargs):
            result = f(inst, *args, **kwargs)
            inst.update()
            return result

        return wrapped

    def __init__(self, name='M'):
        self.name = name
        self.M = zero_mueller
        self.divide_in_blocks()

        self.parameters = Parameters_Mueller(self.M)
        self.analysis = Analysis_Mueller(self.M)
        self.checks = Check_Mueller(self.M)

    def __mul__(self, other):
        """Multiplies two Mueller Matrices.

        Parameters:
            other (Mueller): 2nd Mueller matrix to multiply

        Returns:
            Stokes: `s3 = s1 * s2`
        """

        if isinstance(other, (int, float, complex)):
            M3 = Mueller()
            M3 = self.M * other
        elif isinstance(other, (self.__class__)):
            M3 = Mueller()
            M3.M = self.M * other.M
            M3.name = self.name + " * " + other.name
        elif isinstance(other, Stokes):
            M3 = Stokes()
            M3.M = self.M * other.M
            M3.name = self.name + " * " + other.name
        else:
            raise ValueError('other is Not number, Stokes or Mueller')
        M3.update()
        return M3

    def __rmul__(self, other):
        """Multiplies two Mueller Matrices.

        Parameters:
            other (Mueller): 2nd Mueller matrix to multiply

        Returns:
            Stokes: `s3 = s1 * s2`
        """
        M3 = Mueller()

        if isinstance(other, (int, float, complex)):
            M3 = other * self.M
        elif isinstance(other, self.__class__):
            M3.M = other.M * self.M
            M3.name = other.name + " * " + self.name
        else:
            raise ValueError('other is Not number or Mueller')
        M3.update()
        return M3

    def __repr__(self):
        """prints information about class"""

        M = np.array(self.M).squeeze()
        M = np.round(M, num_decimals)
        l_name = "{} = \n".format(self.name)
        difference = abs(M.round() - M).sum()

        if difference > eps:
            l0 = "  [{:+3.3f}, {:+3.3f}, {:+3.3f}, {:+3.3f}]\n".format(
                M[0, 0], M[0, 1], M[0, 2], M[0, 3])
            l1 = "  [{:+3.3f}, {:+3.3f}, {:+3.3f}, {:+3.3f}]\n".format(
                M[1, 0], M[1, 1], M[1, 2], M[1, 3])
            l2 = "  [{:+3.3f}, {:+3.3f}, {:+3.3f}, {:+3.3f}]\n".format(
                M[2, 0], M[2, 1], M[2, 2], M[2, 3])
            l3 = "  [{:+3.3f}, {:+3.3f}, {:+3.3f}, {:+3.3f}]\n".format(
                M[3, 0], M[3, 1], M[3, 2], M[3, 3])
        else:
            l0 = "  [{:+3.0f}, {:+3.0f}, {:+3.0f}, {:+3.0f}]\n".format(
                M[0, 0], M[0, 1], M[0, 2], M[0, 3])
            l1 = "  [{:+3.0f}, {:+3.0f}, {:+3.0f}, {:+3.0f}]\n".format(
                M[1, 0], M[1, 1], M[1, 2], M[1, 3])
            l2 = "  [{:+3.0f}, {:+3.0f}, {:+3.0f}, {:+3.0f}]\n".format(
                M[2, 0], M[2, 1], M[2, 2], M[2, 3])
            l3 = "  [{:+3.0f}, {:+3.0f}, {:+3.0f}, {:+3.0f}]\n".format(
                M[3, 0], M[3, 1], M[3, 2], M[3, 3])

        return l_name + l0 + l1 + l2 + l3

    def update(self):
        """Actualize parameters"""

        # print("inside set")
        self.divide_in_blocks()
        # Set parameters
        self.parameters.M = self.M
        self.parameters.m00 = self.m00
        self.parameters.P = self.P
        self.parameters.D = self.D
        self.parameters.m = self.m
        self.parameters.Mnorm = self.Mnorm
        # Set analysis
        self.analysis.M = self.M
        self.analysis.m00 = self.m00
        self.analysis.P = self.P
        self.analysis.D = self.D
        self.analysis.m = self.m
        self.analysis.Mnorm = self.Mnorm
        # Set checks
        self.checks.M = self.M
        self.checks.m00 = self.m00
        self.checks.P = self.P
        self.checks.D = self.D
        self.checks.m = self.m
        self.checks.Mnorm = self.Mnorm
        # Update names
        self.parameters.name = self.name
        self.checks.name = self.name
        self.analysis.name = self.name
        # Store parent object
        self.checks.parent = self
        self.analysis.parent = self
        # print(self.parameters.M)

    def get(self):
        """Returns matrix.

        Returns:
            M (numpy.matrix): Mueller matrix
        """

        return self.M

    def check(self):
        """
        verifies that is a 4x4 matrix
        verifies that 4x4 Mueller matrix is properly defined
        """

        # TODO: do check function
        print("TODO")
        pass

    def divide_in_blocks(self):
        """Method that divides a mueller matrix in their block components.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016)

        Parameters:
            M (4x4 matrix): Mueller matrix of the diattenuator.

        Returns:
            D (1x3 or 3x1 float): Diattenuation vector.
            P (1x3 or 3x1 float): Diattenuation vector.
            m (3x3 matrix): Small m matrix.
            m00 (float, default 1): [0, 1] Parameter of average intensity.
        """
        # Avoid divide by 0
        m00 = self.M[0, 0]
        if m00 == 0:
            M = self.M
        else:
            M = self.M / m00
        # Rest of the blocks
        D = matrix(M[0, 1:4])
        P = matrix(M[1:4, 0])
        m = matrix(M[1:4, 1:4])
        # Store in object also the normalized matrix
        self.Mnorm = M
        self.D = D
        self.P = P
        self.m = m
        self.m00 = m00
        return D, P, m, m00

    @_actualize_
    def rotate(self,
               angle=0 * degrees,
               keep=True,
               returns_matrix=False,
               is_repair_name=True):
        """Rotates a Mueller matrix a certain angle

        M_rotated = rotation_matrix_Mueller(-angle) * self.M * rotation_matrix_Mueller(angle)

        Parameters:
            angle (float): angle of rotation_matrix_Jones in radians.
            keep (bool): if True self.M is updated. If False, it returns matrix and it is not updated in self.M.
            returns_matrix (bool): if True returns a matrix, else returns an instance to object
            is_repair_name (bool): if True tries to repair name with @ rot @ rot -> @ 2*rot
        """

        if angle != 0:
            M_rotated = rotation_matrix_Mueller(
                -angle) * self.M * rotation_matrix_Mueller(angle)
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
            j3 = Mueller()
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
        """Rotation of a Mueller matrix

        M_rotated= rotation_matrix(-angle) * M * rotation_matrix(angle)

        References:
            After Gil, Ossikovski (3.3) - p. 116

        Parameters:
            angle (float): angle of rotation_matrix in radians.
            keep (bool): if True self.M is updated and returns self.M. If False, it returns matrix and it is not updated in self.M.

        """
        if angle != 0:
            M_rotated = rotation_matrix_Mueller(
                -angle) * self.M * rotation_matrix_Mueller(angle)
            self.name = self.name + " @{:1.2f}º".format(angle / degrees)
            self.name = repair_name(self.name)
        else:
            M_rotated = self.M

        if keep is True:
            self.M = M_rotated

        return M_rotated

    @_actualize_
    def clear(self):
        """removes data from stokes vector.
        """
        self.from_elements(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.name = ''

    @_actualize_
    def from_elements(self, m00, m01, m02, m03, m10, m11, m12, m13, m20, m21,
                      m22, m23, m30, m31, m32, m33):
        """4x4 Custom Mueller matrix.

        Parameters:
            m00-m33 (float): real elements of matrix

        Returns:
            (numpy.matrix): 4x4 Muller matrix
        """

        M = np.matrix(np.zeros((4, 4), dtype=float))
        M[0, 0] = m00
        M[0, 1] = m01
        M[0, 2] = m02
        M[0, 3] = m03
        M[1, 0] = m10
        M[1, 1] = m11
        M[1, 2] = m12
        M[1, 3] = m13
        M[2, 0] = m20
        M[2, 1] = m21
        M[2, 2] = m22
        M[2, 3] = m23
        M[3, 0] = m30
        M[3, 1] = m31
        M[3, 2] = m32
        M[3, 3] = m33

        self.M = M
        return self.M

    @_actualize_
    def from_matrix(self, Matrix):
        """Creates a Mueller object directly from the matrix.

        Parameters:
            Matrix (4x4 numpy.matrix): Mueller matrix

        Returns:
            obj (Mueller): Mueller object."""

        self.M = Matrix
        return self.M

    @_actualize_
    def from_Jones(self, J):
        """Takes a Jones Matrix and converts into Mueller Matrix

        .. math:: M = U^* (J \otimes J^*) * U^{-1}

        .. math:: T(M * M_t)=4*m_{00}

        References:
            Handbook of Optics vol 2. 22.36 (50)

        Parameters:
            J (2x2 mumpy.matrix): Mueller matrix

        Returns:
            M (mumpy.matrix): Mueller matrix
        """

        U = matrix([[1, 0, 0, 1], [1, 0, 0, -1], [0, 1, 1, 0], [0, 1j, -1j,
                                                                0]])
        if not isinstance(J, np.matrix):
            J = J.M
        M = U * np.kron(J, J.conjugate()) * inv(U)
        M = np.real(M)
        self.M = M
        return self.M

    @_actualize_
    def from_blocks(self, D, P, m, m00=1):
        """Function that creates a mueller matrix from their block components.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016)

        Parameters:
            D (1x3 or 3x1 float): Diattenuation vector.
            P (1x3 or 3x1 float): Diattenuation vector.
            m (3x3 matrix): Small m matrix.
            m00 (float, default 1): [0, 1] Parameter of average intensity

        Returns:
            M (numpy.matrix): 4x4 Mueller matrix of the diattenuator.
        """
        M = np.matrix(
            np.array([[1, D[0, 0], D[0, 1], D[0, 2]],
                      [P[0, 0], m[0, 0], m[0, 1], m[0, 2]],
                      [P[1, 0], m[1, 0], m[1, 1], m[1, 2]],
                      [P[2, 0], m[2, 0], m[2, 1], m[2, 2]]]))
        self.M = m00 * M
        return self.M

    @_actualize_
    def vacuum(self):
        """Muller 4x4 matrix of vacuum.

        Returns:
            M (numpy.matrix): 4x4 Mueller matrix vaccum matrix
        """

        self.M = matrix(
            array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]))
        return self.M

    @_actualize_
    def depolarizer(self, d, m00=1):
        """converts pure light into light with a certain degree of polarization.
        It is used to convert change angle of incident polarization

        Parameters:
            d (float or 1x3 array): degree of polarization
            m00 (float, default 1): [0, 1] Parameter of average intensity

        Returns:
            M (numpy.matrix): 4x4 Mueller matrix of depolarizer
        """
        if np.size(d) == 1:
            depolarizer = np.diag([1, d, d, d])
        else:
            depolarizer = np.diag([1, d[0], d[1], d[2]])

        self.M = m00 * depolarizer
        return self.M

    @_actualize_
    def diattenuator_linear(self, p1=1, p2=0, angle=0):
        """Mueller 4x4 matrix for pure linear homogeneous diattenuator.

        References:
            Gil, Ossikovski (4.79) - p. 143
            Handbook of Optics vol 2. 22.16 (Table 1) is with q=p1**2, r=p2**2

        Parameters:
            p1 (float): [0,1] maximum field transmission value.
            p2 (float): [0,1] minimum field transmission value.
            angle (float): angle of rotation_matrix with respect to 0º.

        Returns:
            M (numpy.matrix): 4x4 Mueller matrix of diattenuator_linear

        Note:
            In order to be compatible with Jones modules, field transmission and not intensity transmission is used in our program.

        """
        # Calculate intensity transmission coefficients
        a = p1**2 + p2**2
        b = p1**2 - p2**2
        c = 2 * p1 * p2
        # Calculate the matrix
        self.M = 0.5 * matrix(
            array([[a, b, 0, 0], [b, a, 0, 0], [0, 0, c, 0], [0, 0, 0, c]]))
        self.rotate(angle)
        return self.M

    @_actualize_
    def diattenuator_carac_angles_from_Jones(self,
                                             p1=1,
                                             p2=0,
                                             alpha=0,
                                             delay=0,
                                             give_all=False):
        """Function that calculates the most general homogeneous diattenuator from field transmission and caracteristic angles of the main eigenstate. It calculates it by calculating the corresponding diattenuator in Jones formalism and transforming it to Mueller.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016) pp 137.

        Parameters:
            p1 (float): [0, 1] Square root of the higher transmission for one
                eigenstate.
            p2 (float): [0, 1] Square root of the lower transmission for the other eigenstate.
            alpha (float): [0, pi/2]: tan(alpha) is the ratio between amplitudes of the eigenstates  in Jones formalism.
            delay (float): [0, 2*pi]: phase difference between both components of the eigenstates in Jones formalism.
            give_all (bool): If true, it gives also the Jones object as output. Default: False.

        Returns:
            M (4x4 matrix): Mueller matrix of the diattenuator.
            J (Jones object): Jones object of the same diattenuator.
        """
        # Do this in order to increase performance
        if p1 == 0 and p2 == 0:
            self.M = np.diag([0, 0, 0, 0])
            J = Jones_matrix(self.name)
            J.from_matrix(matrix(np.zeros((2, 2))))
        elif p1 == 1 and p2 == 1:
            self.M = np.identity(4)
            J = Jones_matrix(self.name)
            J.from_matrix(matrix(np.eye(2)))
        else:
            # Restrict parameter values to the correct interval
            alpha = put_in_limits(alpha, "alpha")
            delay = put_in_limits(delay, "delay")
            # First, calculate the Jones_vector Matrix
            J = Jones_matrix(self.name)
            J.diattenuator_carac_angles(p1, p2, alpha, delay)
            # Now, transform it to Mueller
            self.from_Jones(J)
        # Selective output
        if give_all:
            return self.M, J
        else:
            return self.M

    @_actualize_
    def diattenuator_azimuth_ellipticity_from_Jones(self,
                                                    p1=1,
                                                    p2=0,
                                                    az=0,
                                                    el=0,
                                                    give_all=False):
        """Function that calculates the most general homogenous diattenuator from field transmission and caracteristic angles of the main eigenstate. It calculates it by calculating the corresponding diattenuator in Jones formalism and transforming it to Mueller.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016) pp 137.

        Parameters:
            p1 (float): [0, 1] Square root of the higher transmission for one
                eigenstate.
            p2 (float): [0, 1] Square root of the lower transmission for the other eigenstate.
            az (float): [0, pi]: Azimuth.
            el (float): [-pi/4, pi/4]: Ellipticity.
            give_all (bool): If true, it gives also the Jones object as output. Default: False.

        Returns:
            M (4x4 matrix): Mueller matrix of the diattenuator.
            J (Jones object): Jones object of the same diattenuator.
        """
        # Do this in order to increase performance
        if p1 == 0 and p2 == 0:
            self.M = np.diag([1, 0, 0, 0])
            J = Jones_matrix(self.name)
            J.from_matrix(matrix(np.zeros((2, 2))))
        elif p1 == 1 and p2 == 1:
            self.M = np.identity(4)
            J = Jones_matrix(self.name)
            J.from_matrix(matrix(np.eye(2)))
        else:
            # Restrict parameter values to the correct interval
            az = put_in_limits(az, "azimuth")
            el = put_in_limits(el, "ellipticity")
            # First, calculate the Jones_vector Matrix
            J = Jones_matrix(self.name)
            J.diattenuator_azimuth_ellipticity(p1, p2, az, el)
            # Now, transform it to Mueller
            self.from_Jones(J)
        # Selective output
        if give_all:
            return self.M, J
        else:
            return self.M

    @_actualize_
    def diattenuator_carac_angles_from_vector(self,
                                              p1=1,
                                              p2=0,
                                              alpha=0,
                                              delay=0,
                                              give_all=False):
        """Function that calculates the most general homogenous diattenuator from diattenuator parameters with the intermediate step of calculating the diattenuation vector.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016), pp 142.

        Parameters:
            p1 (float): [0, 1] Square root of the higher transmission for one eigenstate.
            p2 (float): [0, 1] Square root of the lower transmission for the other eigenstate.
            alpha (float): [0, pi/2]: tan(alpha) is the ratio between amplitudes of the eigenstates  in Jones formalism.
            delay (float): [0, 2*pi]: phase difference between both components of the eigenstates in Jones formalism.
            give_all (bool): If true, it gives also the Jones object as output. Default: False.

        Returns:
            M (4x4 matrix): Mueller matrix of the diattenuator.
            D (1x3 array): Diattenuation vector.
            m00 (float): Mean transmission coefficient.
        """
        # Do this in order to increase performance
        if p1 == 0 and p2 == 0:
            self.M = np.diag([1, 0, 0, 0])
            D = np.matrix(np.zeros(1, 3))
            m00 = 1
        elif p1 == 1 and p2 == 1:
            self.M = np.identity(4)
            D = np.matrix(np.zeros(1, 3))
            m00 = 1
        else:
            # Restrict parameter values to the correct interval
            alpha = put_in_limits(alpha, "alpha")
            delay = put_in_limits(delay, "delay")
            # Calculate the diattenuation vector
            f = (p1**2 - p2**2) / (p1**2 + p2**2)
            D = array([
                f * cos(2 * alpha), f * sin(2 * alpha) * cos(delay),
                f * sin(2 * alpha) * sin(delay)
            ])
            m00 = 0.5 * (p1**2 + p2**2)
            # Now, transfor it to Mueller
            self.diattenuator_from_vector(D, m00)
        # Selective output
        if give_all:
            return self.M, D, m00
        else:
            return self.M

    @_actualize_
    def diattenuator_azimuth_ellipticity_from_vector(self,
                                                     p1=1,
                                                     p2=0,
                                                     az=0,
                                                     el=0,
                                                     give_all=False):
        """Function that calculates the most general diattenuator from
        diattenuator parameters with the intermediate step of calculating the
        diattenuation vector.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016), pp 142.

        Parameters:
            p1 (float): [0, 1] Square root of the higher transmission for one eigenstate.
            p2 (float): [0, 1] Square root of the lower transmission for the other eigenstate.
            az (float): [0, pi]: Azimuth.
            el (float): [-pi/4, pi/4]: Ellipticity.
            give_all (bool): If true, it gives also the Jones object as output. Default: False.

        Returns:
            M (4x4 matrix): Mueller matrix of the diattenuator.
            D (1x3 array): Diattenuation vector.
            m00 (float): Mean transmission coefficient.
        """
        # Do this in order to increase performance
        if p1 == 0 and p2 == 0:
            self.M = np.diag([1, 0, 0, 0])
            self.M = np.identity(4)
            D = np.matrix(np.zeros(1, 3))
        elif p1 == 1 and p2 == 1:
            self.M = np.identity(4)
            self.M = np.identity(4)
            D = np.matrix(np.zeros(1, 3))
        else:
            # Transform to caracteristic angles and use their Method
            alpha, delay = azimuth_elipt_2_carac_angles(az, el)
            # _, D = self.diattenuator_carac_angles_from_vector(
            #     p1, p2, alpha, delay, give_all=True) TODO: Fix output from Methods
            self.diattenuator_carac_angles_from_vector(
                p1, p2, alpha, delay, give_all=True)
        # Selective output
        if give_all:
            return self.M, self.D, self.m00
        else:
            return self.M

    @_actualize_
    def diattenuator_from_vector(self, D, m00=1):
        """Function that calculates the most general diattenuator from the
        Diattenuation or Polarizance vector.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016), pp 142.

        Parameters:
            D (1x3 or 3x1 float): Diattenuation or Polarizance vector.
            m00 (float, default 1): [0, 1] Parameter of average intensity.

        Returns:
            M (4x4 matrix): Mueller matrix of the diattenuator.
        """
        # D must be a 1x3 row vector
        D = matrix(D)
        if iscolumn(D):
            D = D.T
        if not D.size == 3:
            raise ValueError(
                'Diattenuation vector must have exactly 3 elements.')
        # Calculate diattenuation
        # TODO: (Jesus) This must be made simpler
        auxiliar = Mueller()
        auxiliar.parameters.D = D
        d = auxiliar.parameters.diattenuation()
        # Depolarization vector may be wrong, check that
        if np.isreal(d):
            if d > 1:
                print('Warning: Diattenuation vector is not real (D > 1).')
                d = 1
            elif d < 0:
                print('Warning: Diattenuation vector is not real (D < 0).')
        else:
            raise ValueError('Diattenuation vector is not real (D complex).')
        # Now we can calculate the small m matrix. If d == 0, use the identity
        if d == 0:
            m = np.eye(3)
        else:
            skd = sqrt(1 - d**2)
            m1 = skd * np.diag([1, 1, 1])
            m2 = (1 - skd) * np.kron(D, D) / d**2
            m = m1 + np.reshape(m2, (3, 3))
        # Now we have all the necessary blocks
        self.from_blocks(D, D.T, m, m00)
        return self.M

    @_actualize_
    def retarder_linear(self, D, angle=0):
        """Muller 4x4 matrix for horizontal linear retarder

        References:
            Gil, Ossikovski (4.31) - p. 132
            Handbook of Optics vol 2. 22.16 (Table 1) coincides

        Parameters:
            D (float): [0, pi] Delay introduced to the slow eigenstate respect to the fast eigenstate.
            angle (float): angle of rotation_matrix with respect to 0º.

        Returns:
            (numpy.matrix): 4x4 Muller retarder matrix
        """

        R = matrix(
            array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, cos(D),
                                                sin(D)],
                   [0, 0, -sin(D), cos(D)]]))
        self.M = R
        self.rotate(angle)
        return self.M

    @_actualize_
    def diattenuator_retarder_linear(self, p1=1, p2=1, D=0, theta=0):
        """Creates a linear diattenuator retarder with the same axes for diattenuation and retardance.

        References:
            Handbook of Optics, Chapter 22.

        Args:
            p1 (float): maximun
            p2 (float): minimum
            D (float): delay between eigenstates introduced by the linear retarder.
            theta (float): angle of diattenuating retarder

        Returns:
            ndarray: 4x4 rotation matrix
        """
        suma = p1**2 + p2**2
        dif = p1**2 - p2**2
        mult = 2 * p1 * p2
        cd = cos(D)
        sd = sin(D)
        M = 0.5 * matrix(
            array([[suma, dif, 0, 0], [dif, suma, 0, 0],
                   [0, 0, mult * cd, mult * sd], [0, 0, -mult * sd, mult * cd]
                   ]))
        self.M = M
        self.rotate(theta)
        return self.M

    @_actualize_
    def quarter_wave(self, angle=0 * degrees):
        """Muller 4x4 matrix for quarter wave retarder.
        It is used to convert linear light into circular light

        References:
            Gil, Ossikovski (4.32) - p. 132

        Parameters:
            angle (float): angle of quarter plate wave

        Returns:
            (numpy.matrix): 4x4 Muller matrix of the quarter wave
        """
        # Definicion de la matrix
        quarter_wave_0 = matrix(
            array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, -1, 0]]))
        self.M = quarter_wave_0
        self.rotate(angle)
        return self.M

    @_actualize_
    def half_wave(self, angle=0 * degrees):
        """Muller 4x4 matrix for half wave retarder.
        It is used to convert change angle of incident polarization

        Parameters:
            angle (float): angle of half plate wave

        Returns:
            (numpy.matrix): 4x4 Muller matrix of the half wave
        """
        half_wave_0 = matrix(
            array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, -1, 0], [0, 0, 0, -1]]))
        self.M = half_wave_0
        self.rotate(angle)
        return self.M

    @_actualize_
    def retarder_carac_angles_from_Jones(self,
                                         D,
                                         alpha,
                                         delta,
                                         m00=1,
                                         give_all=False):
        """Function that calculates the most general homogeneous retarder from retarder characteristic angles of the fast eigenstate. The method calculates first the matrix in Jones formalism, and then transforms it to Mueller.

        From: "Polarized light and the Mueller Matrix approach", J. J. Gil, pp 125.

        Parameters:
            D (float): [0, pi] Delay introduced to the slow eigenstate respect to the fast eigenstate.
            alpha (float): [0, pi]: tan(alpha) is the ratio between amplitudes of the electric field of the fast eigenstate.
            delta (float): [0, 2*pi]: phase difference between both components of the electric field of the fast eigenstate.
            m00 (float, default 1): [0, 1] Parameter of average intensity
            give_all (bool): If true, it gives also the Jones object as output. Default: False.

        Returns:
            M (4x4 matrix): Mueller matrix of the diattenuator.
            J (Jones object): Jones object of the same retarder.
        """
        # Check if delay is 0 or pi for optimization
        if np.abs(D % (2 * pi)) < eps:
            self.M = np.identity(4)
            J = Jones_matrix(self.name)
            J.from_matrix(matrix(np.eye(2)))
        else:
            # First, calculate the Jones Matrix
            J = Jones_matrix(self.name)
            J.retarder_carac_angles(D, alpha, delta)
            # Now, transfor it to Mueller
            self.from_Jones(J)
        # If m00 is not 1, update it
        if m00 < 1 and m00 >= 0:
            self.M = self.M * m00
            self.update()
        # Default Output
        if give_all:
            return self.M, J
        else:
            return self.M

    @_actualize_
    def retarder_azimuth_ellipticity_from_Jones(self,
                                                D,
                                                az,
                                                el,
                                                m00=1,
                                                give_all=False):
        """Function that calculates the most general homogeneous retarder from rthe azimuth and ellipticity if the fast eigenstate.

        From: "Polarized light and the Mueller Matrix approach", J. J. Gil, pp 125.

        Parameters:
            D (float): [0, pi] Delay introduced to the slow eigenstate respect to the fast eigenstate.
            az (float): [0, pi]: Azimuth.
            el (float): [-pi/4, pi/4]: Ellipticity.
            m00 (float, default 1): [0, 1] Parameter of average intensity
            give_all (bool): If true, it gives also the Jones object as output. Default: False.

        Returns:
            M (4x4 matrix): Mueller matrix of the diattenuator.
            J (Jones object): Jones object of the same retarder.
        """
        # Check if delay is 0 or pi for optimization
        if np.abs(D % (2 * pi)) < eps:
            self.M = np.identity(4)
            J = Jones_matrix(self.name)
            J.from_matrix(matrix(np.eye(2)))
        else:
            # First, calculate the Jones Matrix
            J = Jones_matrix(self.name)
            J.retarder_azimuth_ellipticity(D, az, el)
            # Now, transfor it to Mueller
            self.from_Jones(J)
        # If m00 is not 1, update it
        if m00 < 1 and m00 >= 0:
            self.M = self.M * m00
            self.update()
        # Default Output
        if give_all:
            return self.M, J
        else:
            return self.M

    @_actualize_
    def retarder_carac_angles_from_vector(self,
                                          D,
                                          alpha,
                                          delta,
                                          m00=1,
                                          give_all=False):
        """Function that calculates the most general homogeneous retarder from the characteristic angles of the fast eigenstate. The method calculates first the retardance vector, and uses it to calculate the Mueler matrix.

        From: "Polarized light and the Mueller Matrix approach", J. J. Gil, pp 125.

        Parameters:
            D (float): [0, pi] Delay introduced to the slow eigenstate respect to the fast eigenstate.
            alpha (float): [0, pi]: tan(alpha) is the ratio between amplitudes of the electric field of the fast eigenstate.
            delta (float): [0, 2*pi]: phase difference between both components of the electric field of the fast eigenstate.
            m00 (float, default 1): [0, 1] Parameter of average intensity
            give_all (bool): If true, it gives also the Jones object as output. Default: False.

        Returns:
            M (4x4 matrix): Mueller matrix of the diattenuator.
            ur (3x1 array): Unitary retardance vector.
        """
        # Check if delay is 0 or pi for optimization
        if np.abs(D % (2 * pi)) < eps:
            self.M = np.identity(4)
            ur = np.zeros(3)
        else:
            # Calculate the retardance vector
            ur = array([
                cos(2 * alpha),
                sin(2 * alpha) * cos(delta),
                sin(2 * alpha) * sin(delta)
            ])
            # Calculate using the retardance vector method
            self.retarder_from_vector(D=D, ur=ur, m00=1)
        # If m00 is not 1, update it
        if m00 < 1 and m00 >= 0:
            self.M = self.M * m00
            self.update()
        # Default Output
        if give_all:
            return self.M, ur
        else:
            return self.M

    @_actualize_
    def retarder_azimuth_ellipticity_from_vector(self,
                                                 D,
                                                 az,
                                                 el,
                                                 m00=1,
                                                 give_all=False):
        """Function that calculates the most general homogeneous retarder from razimuth and ellipticity of the fast eigenstate. The method calculates first the retardance vector, and uses it to calculate the Mueler matrix.

        From: "Polarized light and the Mueller Matrix approach", J. J. Gil, pp 125.

        Parameters:
            D (float): [0, pi] Delay introduced to the slow eigenstate respect to the fast eigenstate.
            az (float): [0, pi]: Azimuth.
            el (float): [-pi/4, pi/4]: Ellipticity.
            m00 (float, default 1): [0, 1] Parameter of average intensity
            give_all (bool): If true, it gives also the Jones object as output. Default: False.

        Returns:
            M (4x4 matrix): Mueller matrix of the diattenuator.
            ur (3x1 array): Unitary retardance vector.
        """
        # Check if delay is 0 or pi for optimization
        if np.abs(D % (2 * pi)) < eps:
            self.M = np.identity(4)
            ur = np.zeros(3)
        else:
            # Transform to characteristic angles and use their method
            alpha, delta = azimuth_elipt_2_carac_angles(az, el)
            # _, ur = self.retarder_carac_angles_from_vector(D=D, alpha=alpha, delta=delta, m00=1, give_all=True)
            # TODO: To fix when function output works
            self.retarder_carac_angles_from_vector(
                D=D, alpha=alpha, delta=delta, m00=1, give_all=True)
            ur = None  # TODO: To be fixed when returns from functions work
        # If m00 is not 1, update it
        if m00 < 1 and m00 >= 0:
            self.M = self.M * m00
            self.update()
        # Default Output
        if give_all:
            return self.M, ur
        else:
            return self.M

    @_actualize_
    def retarder_from_vector(self, D, ur, m00=1, unitary=True):
        """Function that calculates the most general homogeneous retarder from razimuth and ellipticity of the fast eigenstate. The method calculates first the retardance vector, and uses it to calculate the Mueler matrix.

        From: "Polarized light and the Mueller Matrix approach", J. J. Gil, pp 125.

        Parameters:
            D (float): [0, pi] Delay introduced to the slow eigenstate respect to the fast eigenstate.
            ur (1x3 numpy array): Unitary retardance vector, or retardance vector.
            m00 (float, default 1): [0, 1] Parameter of average intensity
            unitary (bool): If true, ur is the unitary retardance vector. If false, ur is the retardance vector.

        Returns:
            M (4x4 matrix): Mueller matrix of the diattenuator.
        """
        # Check if delay is 0 or pi for optimization
        if np.abs(D % (2 * pi)) < eps:
            self.M = np.identity(4)
        # Check the delay value is correct for using this formalism
        elif np.abs(sin(D)) < eps:
            raise ValueError(
                "This method doesn't support delay values multiple of pi")
        else:
            # Check if ur is normalized or not
            if not unitary:
                ur = ur / D
            # # If it is a row array, fix it.
            # if isrow(ur):
            #     ur = ur.T
            sD, cD = (sin(D), cos(D))
            # Calculate m matrix
            m = np.zeros((3, 3), dtype=float, order='C')
            for i in range(3):
                for j in range(3):
                    aux = 0
                    for k in range(3):
                        aux += Eijk(i, j, k) * ur[k]
                    m[i, j] = delta_kron(
                        i, j) * cD + (1 - cD) * ur[i] * ur[j] + sD * aux
            # Create P and D vectors
            Dvect = matrix(np.zeros((1, 3)))
            # Join blocks
            self.from_blocks(Dvect, Dvect.T, m, m00=1)

        # If m00 is not 1, update it
        if m00 < 1 and m00 >= 0:
            self.M = self.M * m00
            self.update()
        return self.M

    @_actualize_
    def diattenuator_retarder_linear(self, p1, p2, D, angle=0):
        """Creates the matrix for a linear diattenuator retarder with the same
        axes for diattenuation and retardance.

        References:
            Handbook of Optics, Chapter 22.

        Parameters:
            p1 (float): maximun
            p2 (float): minimum
            D (float): [0, pi] Delay introduced to the slow eigenstate respect to the fast eigenstate.
            angle (float): angle of diattenuating retarder

        Returns:
            (numpy.matrix): 4x4 Muller matrix rotation_matrix matrix
        """
        suma = p1**2 + p2**2
        dif = p1**2 - p2**2
        mult = 2 * p1 * p2
        cd = cos(D)
        sd = sin(D)
        M = 0.5 * matrix(
            array([[suma, dif, 0, 0], [dif, suma, 0, 0],
                   [0, 0, mult * cd, mult * sd], [0, 0, -mult * sd, mult * cd]
                   ]))
        self.M = M
        self.rotate(angle)
        return self.M

    @_actualize_
    def depolarizer(self, d, m00=1):
        """converts pure light into light with a certain degree of polarization.
        It is used to convert change angle of incident polarization

        Parameters:
            d (float or 1x3 array): degree of polarization
            m00 (float, default 1): [0, 1] Parameter of average intensity

        Returns:
            (numpy.matrix): 4x4 Muller matrix rotation_matrix matrix
        """
        if np.size(d) == 1:
            depolarizer = np.diag([1, d, d, d])
        else:
            depolarizer = np.diag([1, d[0], d[1], d[2]])

        self.M = m00 * depolarizer
        return self.M

    @_actualize_
    def vacuum(self):
        """Muller 4x4 matrix when no sample is included

        Returns:
            (numpy.matrix): 4x4 Muller matrix vaccum matrix
        """

        self.M = matrix(
            array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]))
        return self.M

    # def to_Jones(self):
    #     """Takes a non-depolarizing Mueller Matrix and converts into Jones matrix
    #
    #     .. math:: M = U * (J oX J*) * U^(-1)
    #     .. math:: T(M*Mt)=4*m00
    #
    #     References:
    #         Handbook of Optics vol 2. 22.36 (52-54)
    #
    #     Parameters:
    #         M (mumpy.matrix): Mueller matrix
    #
    #     """
    #     M = self.M
    #     pxx = sqrt((M[0, 0] + M[0, 1] + M[1, 0] + M[1, 1]) / 2)
    #     pxy = sqrt((M[0, 0] - M[0, 1] + M[1, 0] - M[1, 1]) / 2)
    #     pyx = sqrt((M[0, 0] + M[0, 1] - M[1, 0] - M[1, 1]) / 2)
    #     pyy = sqrt((M[0, 0] - M[0, 1] - M[1, 0] + M[1, 1]) / 2)
    #
    #     fxy = arctan((-M[0, 3] - M[1, 3]) / (M[0, 2] + M[1, 2] + 1e-15))
    #     fyx = arctan((M[3, 0] + M[3, 1]) / (M[2, 0] + M[2, 1] + 1e-15))
    #     fyy = arctan((M[3, 2] - M[2, 3]) / (M[2, 2] + M[3, 3] + 1e-15))
    #
    #     J = matrix(np.zeros((2, 2), dtype=complex))
    #     J[0, 0] = pxx
    #     J[0, 1] = pxy * exp(1j * fxy)
    #     J[1, 0] = pyx * exp(1j * fyx)
    #     J[1, 1] = pyy * exp(1j * fyy)
    #
    #     return (J)

    # Auxiliar matrices
    def covariance_matrix(self):
        """Calculates the covariance matrix of a Mueller matrix.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016)

        Parameters:
            M (numpy.matrix 4x4): Mueller matrix or diattenuation vector.

        Returns:
            (numpy.matrix 4x4): H Covariance matrix.

        Warning:
            The base of matrices S is used in an uncommon order.
        Warning:
            In order to obtain the same result as in the book, the formula must be:
            .. math:: H=0.25\sum(m[i,j]\,kron\left[S(i),S(j)^{*}\right].

        """
        M = self.M
        H = np.zeros((4, 4), dtype=complex)
        for i in range(4):
            for j in range(4):
                H += M[i, j] * np.kron(S[i], np.conj(S[j]))
                # print([i, j, np.kron(S[i], S[j])])
        return 0.25 * H


class Parameters_Mueller(object):
    """Class for Mueller Matrix Parameters

    Parameters:
        mueller_matrix (Mueller_matrix): Mueller Matrix

    Attributes:
        self.M (Mueller_matrix)
        self.dict_params (dict): dictionary with parameters
    """

    def __init__(self, mueller_matrix=zero_mueller):
        self.M = mueller_matrix
        self.dict_params = {}

    def __repr__(self):
        """print all parameters
        TODO: print all as jones_matrix"""
        self.get_all()
        header = "parameters:\n"
        text = self.dict_params.__repr__()
        text = text.replace(",", "\n    ", 7)
        text = text.replace("{", "")
        text = text.replace("}", "")
        text = text.replace("'polarized'", "\n     'polarized'")
        text = text.replace("'unpolarized'", "+ 'unpolarized'")
        text = "    " + text
        return header + text

    def help(self):
        """prints help about dictionary
        TODO"""

        text = "Here we explain the meaning of parameters.\n"
        text = text + "    intensity: intensity of the light beam.\n"
        text = text + "    TODO"
        print(text)

    def get_all(self):
        """returns a dictionary with all the parameters of Mueller Matrix"""
        # self.dict_params['intensity'] = self.intensity()
        # self.dict_params['degree_pol'] = self.degree_polarization()
        # self.dict_params['degree_linear_pol'] = self.degree_linear_polarization()
        # self.dict_params['degree_circular_pol'] = self.degree_circular_polarization()
        # self.dict_params['ellipticity'] = self.ellipticity()
        # self.dict_params['azimuth'] = self.azimuth()
        # self.dict_params['eccentricity'] = self.eccentricity()
        # self.dict_params['ellipse_parameters'] = self.ellipse_parameters()
        # polarized, unpolarized = self.polarized_unpolarized()
        # self.dict_params['polarized'] = np.squeeze(np.asarray(polarized)).tolist()
        # self.dict_params['unpolarized'] = np.squeeze(np.asarray(unpolarized)).tolist()
        pass

    def mean_transmission(self):
        """Calculates the mean transmission coefficient.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016)

        Parameters:
            M (4x4 numpy.matrix): Mueller matrix

        Returns:
            (float): Diattenuation
        """
        return self.m00

    def inhomogeneity(self):
        """Calculates the inhomogeneity parameter.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016), pp 119.

        Returns:
            eta (float): Inhomogeneity parameter.
        """
        # TODO: (Jesus) En el libro viene como hacerlo para Jones, implementarlo.
        M = self.M
        tr = np.trace(M)
        det = np.linalg.det(M)
        m00 = self.m00
        T = 1 / sqrt(2) * (tr + M[0, 1] + M[1, 0] + 1j * (M[3, 2] + M[2, 3])
                           ) / sqrt(m00 + M[1, 1] + M[1, 0] + M[0, 1])
        # T can be NaN for certain matrices
        if np.isnan(T):
            eta = 1
        else:
            eta = (4 * m00 - abs(T)**2 - abs(T**2 - 4 * det**0.25)) / (
                4 * m00 - abs(T)**2 + abs(T**2 - 4 * det**0.25))
        return sqrt(eta)

    # Purity components

    def diattenuation(self, D=None):
        """Calculates the diattenuation of a Mueller matrix or a diattenuation vector.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016)


        Returns:
            D (float): Diattenuation
        """
        D = np.linalg.norm(self.D)
        return D

    def diattenuation_linear(self):
        """Calculates the linear diattenuation of a Mueller matrix.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016)

        Returns:
            Dl (float): Linear diattenuation
        """
        Dl = np.linalg.norm(self.D[0:2])
        return Dl

    def diattenuation_circular(self):
        """Calculates the circular diattenuation of a Mueller matrix.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016)

        Returns:
            Dc (float): Circular diattenuation
        """
        Dc = self.D[0, 2]
        return Dc

    def polarizance(self):
        """Calculates the polarizance of a Mueller matrix.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016)

        Returns:
            P (float): Polarizance
        """
        P = np.linalg.norm(self.P)
        return P

    def polarizance_linear(self):
        """Calculates the linear polarizance of a Mueller matrix.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016)

        Returns:
            Pl (float): Linear polarizance
        """
        Pl = np.linalg.norm(self.P[0:2])
        return Pl

    def polarizance_circular(self):
        """Calculates the linear polarizance of a Mueller matrix.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016)

        Returns:
            Pc (float): Cilcular polarizance
        """
        Pc = self.P[2]
        return Pc

    def polarizance_degree(self):
        """Calculates the degree of polarizance.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016)

        Parameters:
            M (numpy.matrix): Mueller matrix or diattenuation vector.

        Returns:
            Pd (1x3 array): Degree of polarizance
        """
        P = self.polarizance()
        D = self.diattenuation()
        Pp = sqrt((P**2 + D**2) / 2)
        return Pp

    def spheric_purity(self):
        """Calculates the spheric purity grade.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016) pp 204.

        Parameters:
            M (numpy.matrix): Mueller matrix or diattenuation vector.

        Returns:
            Ps (1x3 array): spheric purity grade.
        """
        SP = np.linalg.norm(self.m)
        return SP / sqrt(3)

    # Similar to purity grades
    def delay(self):
        """Calculates the delay of the Mueller matrix of a pure retarder.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016) pp 128.

        Returns:
            (float): Calculated delay.
        """
        # TODO: (Jesus) We have to find a way to know if we are in the 180 -> 360 degrees region. Clue: In that case, opper triangular part is negative (except for chi negative and phi lower than 90 deg).
        # In case we have absorption/reflection, substract it
        M = self.Mnorm
        # Calculate delay
        cosD = np.trace(M) / 2 - 1
        delay = np.arccos(cosD)
        return delay

    def retardance(self, unitary=True):
        """Calculates the retardance vector of the Mueller matrix of a retarder.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016) pp 129.

        Parameters:
            M (numpy.matrix): Mueller matrix.
            unitary (bool): If true, ur is the unitary retardance vector. If false, ur is the retardance vector.

        Returns:
            ur (1x3 array): Unitary retardance vector, or retardance vector.
        """
        # Calculate the delay
        D = self.delay()
        # Consider special cases where retardance is not defined
        if np.abs(D % pi) < eps:
            ur = np.zeros(3)
        else:
            ur = np.zeros(3)
            ur[0] = self.M[2, 3] - self.M[3, 2]
            ur[1] = self.M[3, 1] - self.M[1, 3]
            ur[2] = self.M[1, 2] - self.M[2, 1]
            # Consider which vector we want to give as output
            if unitary:
                cte = 1 / (2 * sin(D))
            else:
                cte = D / (2 * sin(D))
            # Calculate final vector
            ur = cte * ur
        return ur

    # Polarization or despolarization
    def polarimetric_purity(self):
        """Calculates the degree of polarimetric purity of a Mueller matrix.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016)

        Parameters:
            M (numpy.matrix): Mueller matrix or diattenuation vector.

        Returns:
            PD (float): Degree of polarimetric purity.
        """
        Pp = self.polarizance_degree()
        Ps = self.spheric_purity()
        PD = sqrt(2. / 3. * Pp**2 + Ps**2)
        return PD

    def depolarization_degree(self):
        """Calculates the depolarization degree of a Mueller matrix.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016)

        Parameters:
            M (numpy.matrix): Mueller matrix or diattenuation vector.

        Returns:
            DD (float): Depolarization degree.
        """
        PD = self.polarimetric_purity()
        if np.isreal(PD):
            if np.abs(PD - 1) < eps:
                DD = 0
            elif np.abs(PD) < 1:
                DD = sqrt(1. - PD**2)
            else:
                raise ValueError('Mueller matrix is not real')
        else:
            raise ValueError('Mueller matrix is not real')
        return DD

    def depolarization_factors(self):
        """Calculates the Euclidean distance and depolarization factor

        References:
            Handbook of Optics vol 2. 22.49 (46 and 47)

        Parameters:
            M (4x4 numpy.matrix): Mueller matrix

        Returns:
            (float): Euclidean distance of the normalized Mueller matrix from an ideal depolarizer
            (float): Dep(M) depolarization of the matrix
        """
        # TODO: (Jesus) Check if Mnorm must be used instead of M

        M = self.M
        quadratic_sum = (array(M)**2).sum()
        euclidean_distance = sqrt(quadratic_sum - M[0, 0]**2) / M[0, 0]
        depolarization = 1 - euclidean_distance / sqrt(3)

        return euclidean_distance, depolarization

    # Polarimetric purity

    def polarimetric_purity_indices(self):
        """Calculates the polarimetric purity indices of a Mueller matrix.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016), pp 208.

        Parameters:
            M (numpy.matrix): Mueller matrix or diattenuation vector.

        Returns:
            l (1x3 array): Polarimetric purity indices.
        """
        # Calculate eigenvalues of covariance matrix
        H = self.covariance_matrix()
        th = np.absolute(np.trace(H))
        l_n, _ = np.linalg.eig(H)
        l_n = np.sort(np.absolute(l_n))
        # Calculate indices
        P1 = (l_n[3] - l_n[2]) / th
        P2 = (l_n[3] + l_n[2] - 2 * l_n[1]) / th
        P3 = (l_n[3] + l_n[2] + l_n[1] - 3 * l_n[0]) / th
        return [P1, P2, P3]

    def transmissions(self):
        """Calculate the maximum and minimum transmittance of an optical element.

        References:
            Handbook of Optics vol 2. 22.32 (eq.38)

        Args:
            M (numpy.matrix): Mueller matrix

        Returns:
            (float, float): T_max, T_min
        """
        d = self.diattenuation()
        T_max = self.m00 * (1 + d)
        T_min = self.m00 * (1 - d)
        return T_max, T_min

    def diattenuator(self, param="all", use_diat=True):
        """Calculates all the parameters from the Mueller Matrix of a
        diattenuator.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016)

        Parameters:
            param (string): Determines the output. There are three options, all,
                carac and azimuth.
            use_diat (bool): In case a matrix is inserted, use the diattenuation (True)
                or polarizance vector (False).

        Returns:
            p1, p2 (float): Axis attenuations.
            alpha (float): Rotation angle.
            delay (float): Delay between eigenstates.
            fi (float): Azimuth.
            chi (float): Ellipticity.
        """
        # Extract the diattenuation or polarizance vector
        if use_diat:
            D = self.diattenuation()
            Dv = self.diattenuation_vector()
        else:
            D = self.polarizance()
            Dv = self.polarizance_vector()
        # Calculate p1 and p2
        p1 = sqrt(self.m00 * (1 + D))
        p2 = sqrt(self.m00 * (1 - D))
        # If the vector is all 0, nothing can be calculated
        if (Dv == 0).all():
            alpha, delay = (0, 0)
            chi, fi = (0, 0)
        else:
            # Calculate alpha, is easy
            c2a = Dv[0] / D
            alpha = np.arccos(c2a) / 2
            # delay is a little bit more complex
            delay = np.arctan(Dv[2] / Dv[1])
            if delay < 0:
                delay += pi
            if Dv[2] < 0:
                delay += pi
            # Restrict measured values to the correct interval (shouldn't be
            # necessary, but just in case)
            alpha = put_in_limits(alpha, "alpha")
            delay = put_in_limits(delay, "delay")
            # Measure the equivalent coordinates
            chi, fi = carac_angles_2_azimuth_elipt(alpha, delay)
        # Output
        if param == "all":
            return p1, p2, alpha, delay, chi, fi
        elif param == "carac":
            return p1, p2, alpha, delay
        else:
            return p1, p2, chi, fi

    def retarder(self, param="all"):
        """Calculates all the parameters from the Mueller Matrix of a
        diattenuator.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016)

        Parameters:
            param (string): Determines the output. There are three options, all,
                carac and azimuth.

        Returns:
            R (float): Delay.
            alpha (float): Rotation angle.
            delay (float): Delay components of the between eigenstate.
            fi (float): Azimuth.
            chi (float): Ellipticity.
        """
        M = self.M
        # Calculate the delay
        D = self.parameters.delay()
        # This formula doesn't work for D = 0 and D = pi.
        if D == 0:
            ur = array([0, 0, 0])
        elif D == pi:
            ur = array(
                [sqrt(M[1, 1] + 1),
                 sqrt(M[2, 2] + 1),
                 sqrt(M[3, 3] + 1)])
        else:
            ur = array([
                M[2, 3] - M[3, 2], M[3, 1] - M[1, 3], M[1, 2] - M[2, 1]
            ]) / (2 * sin(D))
        # Just in case, ||ur|| should be <= 1
        urmod = np.linalg.norm(ur)
        if urmod > 1:
            ur /= urmod
        # Calculate the parameters using az and el to avoid some ambiguity
        chi = np.arcsin(ur[2]) / 2
        fi = np.arcsin(ur[1] / cos(2 * chi)) / 2
        # print([fi / degrees, chi / degrees])
        if fi < 0:
            if np.sign(ur[0]) == 1:
                fi += pi
            else:
                fi = pi / 2 - fi
        else:
            if np.sign(ur[0]) == -1:
                fi = pi / 2 - fi
        alpha, delay = azimuth_elipt_2_carac_angles(fi, chi)
        # Output
        if param == "all":
            return D, alpha, delay, fi, chi
        elif param == "carac":
            return D, alpha, delay
        else:
            return D, fi, chi


class Analysis_Mueller(object):
    """Class for Analysis of Mueller Analysis

    Parameters:
        mueller_matrix (Mueller_matrix): Mueller Matrix

    Attributes:
        self.M (Mueller_matrix)
        self.dict_params (dict): dictionary with parameters
    """

    def __init__(self, Mueller_matrix=zero_mueller):
        self.M = Mueller_matrix
        self.dict_params = {}

    def __repr__(self):
        """print all parameters"""
        self.get_all()
        header = "parameters:\n"
        # text = json.dumps(self.dict_params, indent=4)
        text = self.dict_params.__repr__()
        text = text.replace(",", "\n    ", 7)
        text = text.replace("{", "")
        text = text.replace("}", "")

        text = "    " + text
        return header + text

    def help(self):
        """prints help about dictionary"""

        text = "Here we explain the meaning of parameters.\n"
        text = text + "    intensity: intensity of the light beam.\n"
        text = text + "    TODO"
        print(text)

    def parameters_diattenuator_deprecated(self, param="all", use_diat=True):
        """Calculates all the parameters from the Mueller Matrix of a
        diattenuator.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016)

        Parameters:
            M (numpy.matrix or 1x3 array): Mueller matrix or diattenuation or
                polarizance vector.
            param (string): Determines the output. There are three options, all,
                carac and azimuth.
            use_diat (bool): In case a matrix is inserted, use the diattenuation (True)
                or polarizance vector.

        Returns:
            p1, p2 (float): Axis attenuations.
            alpha (float): Rotation angle.
            delay (float): Delay between eigenstates.
            fi (float): Azimuth.
            chi (float): Ellipticity.
        """
        # In case it is a matrix, extract the diattenuation or polarizance vector
        M = self.M
        if np.size(M) == 16:
            m00 = M[0, 0]
            if use_diat:
                D = self.parameters.diattenuation()
                Dv = diattenuation_vector(M)
            else:
                D = polarizance(M)
                Dv = polarizance_vector(M)
        else:
            Dv = M
            m00 = 1
            D = self.parameters.diattenuation()
        # Calculate p1 and p2
        p1 = sqrt(m00 * (1 + D))
        p2 = sqrt(m00 * (1 - D))
        # If the vector is all 0, nothing can be calculated
        if (Dv == 0).all():
            alpha, delay = (0, 0)
            chi, fi = (0, 0)
        else:
            # Acoid dividing by 0
            if Dv[0] == 0:
                alpha = pi / 4
            else:
                t2a = sqrt(Dv[1]**2 + Dv[2]**2) / abs(Dv[0])
                alpha = np.arctan(t2a) / 2
            if Dv[1] == 0:
                delay = np.sign(Dv[2]) * pi / 2
            else:
                td = Dv[2] / Dv[1]
                delay = np.arctan(td)
            # Restrict measured values to the correct interval
            if alpha < limAlpha[0] or alpha > limAlpha[1]:
                aux = sin(alpha)
                alpha = np.arcsin(abs(aux))
            if delay < limDelta[0] or delay > limDelta[1]:
                delay = delay % (2 * pi)
            # Measure the equivalent coordinates
            fi, chi = carac_angles_2_azimuth_elipt(alpha, delay)
        # Output
        if param == "all":
            return p1, p2, alpha, delay, fi, chi
        elif param == "carac":
            return p1, p2, alpha, delay
        else:
            return p1, p2, fi, chi

    # # Matrix filtering
    def filter_reality_conditions(self,
                                  tol=tol_default,
                                  verbose=False,
                                  counter=0):
        """Function that filters experimental errors by forcing the Mueller matrix
        M to fulfill the conditions necessary for a matrix to be real.

        Parameters:
            M (4x4 matrix): Experimental Mueller matrix.
            tol (float): Tolerance in equalities.
            verbose (float): If true, the function prints out some information
                about the algorithm and matrices.
            counter (int): Auxiliar variable that shoudln't be changed

        Returns:
            Mf (4x4 matrix): Filtered Mueller matrix.
        """
        M = self.M
        if verbose:
            print("The original matrix is:")
            print(M)
        # Check if the matrix is already real
        cond, inf = is_real(M, tol, True)
        # If it is not real, filter. The order of conditions is slightly altered to
        # place easy errors first and complex ones which may have higher impact,
        # later.
        if not cond and counter <= counter_max:
            # Zeroth A condition can be fixed changing the sign of m00
            data = inf['cond0a']
            if not data[1]:
                M[0, 0] = -M[0, 0]
                # Print for debug.
                if verbose:
                    print('Zero A condition was violated. Fixed matrix is:')
                    print(M)
                # Use recursivity to recheck the rest of conditions with the new
                # matrix
                counter = counter + 1
                M = self.filter_reality_conditions(self, tol, verbose, counter)
                return M

            # Zeroth B condition can be fixed dividing M by m00
            data = inf['cond0b']
            if not data[1]:
                M = M / M[0, 0]
                # Print for debug.
                if verbose:
                    print('Zero B condition was violated. Fixed matrix is:')
                    print(M)
                # Use recursivity to recheck the rest of conditions with the new
                # matrix
                counter = counter + 1
                M = self.filter_reality_conditions(self, tol, verbose, counter)
                return M

            # Second condition can be fixed reducing ellements to m00.
            data = inf['cond2']
            if not data[1]:
                m00 = M[0, 0]
                for indx in range(4):
                    for indy in range(4):
                        if abs(M[indx, indy]) > m00:
                            M[indx, indy] = np.sign(M[indx, indy]) * m00
                # Print for debug.
                if verbose:
                    print('Second condition was violated. Fixed matrix is:')
                    print(M)
                # Use recursivity to recheck the rest of conditions with the new
                # matrix
                counter = counter + 1
                M = self.filter_reality_conditions(self, tol, verbose, counter)
                return M

            # Third condition can be solved easily reducing polarizance /
            # diattenuation vectors proportionally
            data = inf['cond3a']
            if not data[1]:
                D = self.parameters.diattenuation()
                M[0, 1] = M[0, 1] / D
                M[0, 2] = M[0, 2] / D
                M[0, 3] = M[0, 3] / D
                # Print for debug.
                if verbose:
                    print('Third A condition was violated. Fixed matrix is:')
                    print(M)
                # Use recursivity to recheck the rest of conditions with the new
                # matrix
                counter = counter + 1
                M = self.filter_reality_conditions(self, tol, verbose, counter)
                return M
            # Condition 3B
            data = inf['cond3b']
            if not data[1]:
                P = polarizance(M)
                M[1, 0] = M[1, 0] / P
                M[2, 0] = M[2, 0] / P
                M[3, 0] = M[3, 0] / P
                # Print for debug.
                if verbose:
                    print('Third B condition was violated. Fixed matrix is:')
                    print(M)
                # Use recursivity to recheck the rest of conditions with the new
                # matrix
                counter = counter + 1
                M = self.filter_reality_conditions(self, tol, verbose, counter)
                return M

            # First condition can be fixed reducing all elements except m00
            # proportionally.
            data = inf['cond1']
            if not data[1]:
                m00 = M[0, 0]
                tr = np.trace(M * M.T)
                f = 3 * m00 / sqrt(tr - m00**2)
                M = M * f
                M[0, 0] = m00
                # Print for debug.
                if verbose:
                    print('First condition was violated. Fixed matrix is:')
                    print(M)
                # Use recursivity to recheck the rest of conditions with the new
                # matrix
                # print('Fix cond1')
                counter = counter + 1
                M = self.filter_reality_conditions(self, tol, verbose, counter)
                return M

            # Fifth condition can be solved decreasing all matrix elements so Tmax =
            # m00*(1 + D) = 1. And as Mt must be real also, do the same with P.
            data = inf['cond5a']
            if not data[1]:
                D = diattenuation(M, normalize=False)
                m00 = M[0, 0]
                # If m00 = 1, we have a rotator here, make P vector 0
                if m00 == 1:
                    M[0, 1] = 0
                    M[0, 2] = 0
                    M[0, 3] = 0
                # If not, divide the D vector so it has the maximum possible D
                else:
                    Dnew = 1 - m00
                    M[0, 1] = M[0, 1] * Dnew / D
                    M[0, 2] = M[0, 2] * Dnew / D
                    M[0, 3] = M[0, 3] * Dnew / D
                    # Print for debug.
                if verbose:
                    print('Fifth A condition was violated. Fixed matrix is:')
                    print(M)
                # Use recursivity to recheck the rest of conditions with the new
                # matrix
                # print('Fix cond5')
                counter = counter + 1
                M = self.filter_reality_conditions(self, tol, verbose, counter)
                return M
            # Condition 5B
            data = inf['cond5b']
            if not data[1]:
                P = polarizance(M, normalize=False)
                m00 = M[0, 0]
                # If m00 = 1, we have a rotator here, make D vector 0
                if m00 == 1:
                    M[1, 0] = 0
                    M[2, 0] = 0
                    M[3, 0] = 0
                # If not, divide the D vector so it has the maximum possible D
                else:
                    Pnew = 1 - m00
                    M[1, 0] = M[1, 0] * Pnew / P
                    M[2, 0] = M[2, 0] * Pnew / P
                    M[3, 0] = M[3, 0] * Pnew / P
                # Print for debug.
                if verbose:
                    print('Fifth B condition was violated. Fixed matrix is:')
                    print(M)
                # Use recursivity to recheck the rest of conditions with the new
                # matrix
                # print('Fix cond5')
                counter = counter + 1
                M = self.filter_reality_conditions(self, tol, verbose, counter)
                return M

            # Sixth condition can be fixed by making zero low enough eigenvalues
            data = inf['cond6']
            if not data[1]:
                # Calculate covariance matrix eigenvalues
                H = self.covariance_matrix()
                qi, U = np.linalg.eig(H)
                qi, U = order_eig(qi, U)
                U = np.matrix(U)
                # Make the smaller ones zero
                for ind, q in enumerate(qi):
                    if q < tol:
                        qi[ind] = 0
                    elif q > 1:
                        qi[ind] = 1
                # Recompose the matrix
                Hf = U * np.diag(qi) * U.H
                # Go back to Mueller
                M = inverse_covariance(Hf)
                # Print for debug.
                if verbose:
                    print('Sixth condition was violated. Fixed matrix is:')
                    print(M)
                # Use recursivity to recheck the rest of conditions with the new
                # matrix
                # print('Fix cond6')
                counter = counter + 1
                M = self.filter_reality_conditions(self, tol, verbose, counter)
                return M
        else:
            # Print for debug.
            if verbose:
                if counter > counter_max:
                    print('Maximum number of iterations reached.')
                else:
                    print('None condition was violated.')
            # Nothing has to be done
            counter = 0
            return M

    # # Matrix decomposition

    def decompose_pure(self,
                       right=True,
                       tol=tol_default,
                       verbose=False,
                       give_all=False):
        """Polar decomposition of a pure Mueller matrix in a retarder and a
        diattenuator.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016), pp 151.

        Parameters:
            right (bool): the diattenuator is calculated to be at the right of the
                retarder.
            tol (float): Tolerance in equalities.
            verbose (float): If true, the function prints out some information
                about the matrices.
            give_all (bool): If true, the complete output will be thrown.

        Returns:
            Mr (numpy.matrix): Mueller matrix of the retarder.
            Md (numpy.matrix): Mueller matrix of the diattenuator.
            param (dictionary): Dictionary with the 9 parameters (7 independent) of
                both the retarder and the diattenuator (optional).
        """
        M = self.M
        # Just in case
        M = np.matrix(M)
        # Calculate the diattenuator Parameters
        if right:
            p1, p2, alphaD, deltaD, fiD, chiD = diattenuator(M)
        else:
            p1, p2, alphaD, deltaD, fiD, chiD = polarizer(M)
        # Calculate the diattenuator Matrix
        Md = stokes.general_diattenuator_parvect(
            p1, p2, alphaD, deltaD, carac=True)
        # In order to proceed, we have to know if M is singular or not.
        cond2 = is_singular2(M, tol=tol)
        if cond2:
            # Singular matrix. We have to check that P or D vectors are not nule.
            Pv = polarizance_vector(M)
            Dv = diattenuation_vector(M)
            c1 = (abs(Pv) <= tol).all()
            c2 = (abs(Dv) <= tol).all()
            if c1 and c2:
                # If P and D are 0, then we started with a retarder all the time
                Mr = M
                if give_all or verbose:
                    R, alphaR, deltaR, fiR, chiR = retarder(M)
            else:
                # Calculate the retarder with minimum delay
                cR = np.dot(Pv, Dv)
                R = np.arccos(cR)
                pv = np.cross(Pv, Dv)
                Rv = R * pv / np.linalg.norm(Pv)
                Mr = stokes.general_retarder_vect(R, Rv)
                # Extract the other parameters
                if give_all or verbose:
                    _, alphaR, deltaR, fiR, chiR = retarder(Mr)
        else:
            # Non-singular matrix. Multiply by Md^(-1) at the correct side
            if right:
                Mr = M * Md.I
            else:
                Mr = Md.I * M
            # If required, calculate the parameters from the Matrix
            if give_all or verbose:
                R, alphaR, deltaR, fiR, chiR = retarder(Mr)
        # Calculate error
        if give_all or verbose:
            if right:
                Mt = Mr * Md
            else:
                Mt = Md * Mr
            MeanErr = np.mean(sqrt(np.power(M - Mt, 2)))
            MaxErr = abs(M - Mt).max()

        # If required, print the Parameters
        if verbose:
            print("------------------------------------------------------")
            if right:
                print("Matrx M decomposed as M = Mr * Md.")
                print("")
                print("The retarder Mueller matrix is:")
                print(Mr)
                print("Parameters:")
                print(("  - Delay = {}º.".format((R / degrees))))
                print(
                    ("  - Angle = {}º; Delay between components = {}º.".format(
                        (alphaR / degrees), (deltaR / degrees))))
                print(("  - Azimuth = {}º; Ellipticity = {}º.".format(
                    (fiR / degrees), (chiR / degrees))))
                print("")
                print("The diatenuator Mueller matrix is:")
                print(Md)
                print("Parameters:")
                print(("  - p1 = {}; p2 = {}.".format(p1, p2)))
                print(
                    ("  - Angle = {}º; Delay between components = {}º.".format(
                        (alphaD / degrees), (deltaD / degrees))))
                print(("  - Azimuth = {}º; Ellipticity = {}º.".format(
                    (fiD / degrees), (chiD / degrees))))
            else:
                print("Matrx M decomposed as M = Md * Mr.")
                print("")
                print("The diatenuator Mueller matrix is:")
                print(Md)
                print("Parameters:")
                print(("  - p1 = {}; p2 = {}.".format(p1, p2)))
                print(
                    ("  - Angle = {}º; Delay between components = {}º.".format(
                        (alphaD / degrees), (deltaD / degrees))))
                print(("  - Azimuth = {}º; Ellipticity = {}º.".format(
                    (fiD / degrees), (chiD / degrees))))
                print("")
                print("The retarder Mueller matrix is:")
                print(Mr)
                print("Parameters:")
                print(("  - Delay = {}º.".format((R / degrees))))
                print(
                    ("  - Angle = {}º; Delay between components = {}º.".format(
                        (alphaR / degrees), (deltaR / degrees))))
                print(("  - Azimuth = {}º; Ellipticity = {}º.".format(
                    (fiR / degrees), (chiR / degrees))))
            print("")
            print(("The mean square error in the decomposition is: {}".format(
                MeanErr)))
            print(
                ("The maximum error in the decomposition is: {}".format(MaxErr)
                 ))
            print("------------------------------------------------------")
        #  If required, make a dictionary with the Parameters
        if give_all:
            param = dict(
                Delay=R,
                AngleR=alphaR,
                AxisDelayR=deltaR,
                AzimuthR=chiR,
                EllipticityR=fiR,
                p1=p1,
                p2=p2,
                AngleD=alphaD,
                AxisDelayD=deltaD,
                AzimuthD=fiD,
                EllipticityD=chiD,
                MeanError=MeanErr,
                MaxError=MaxErr)
            return Mr, Md, param
        else:
            return Mr, Md

    def decompose_polar(self,
                        decomposition='DRP',
                        tol=tol_default,
                        verbose=False,
                        give_all=False,
                        filter=True):
        """Polar decomposition of a general Mueller matrix in a partial depolarizer,
        retarder and a diattenuator.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016), pp 257.

        Parameters:
            M (numpy.matrix): Mueller matrix or diattenuation vector.
            decomposition (string): string with the order of the elements:
                depolarizer (D), retarder (R) or diattenuator/polarizer (P).
            tol (float): Tolerance in equalities.
            verbose (float): If true, the function prints out some information
                about the matrices.
            give_all (bool): If true, the complete output will be thrown.
            filter (bool): If true, the algorithm attempts to filter the Mueller
                matrix before decomposition.

        Returns:
            Mr (numpy.matrix): Mueller matrix of the retarder.
            Md (numpy.matrix): Mueller matrix of the diattenuator.
            param (dictionary): Dictionary with the 9 parameters (7 independent) of
                both the retarder and the diattenuator (optional).
        """
        # Print results
        if verbose:
            print("------------------------------------------------------")
        # Filter the matrix if required
        if filter:
            M = filter_reality_conditions(M, tol)
        # If M is pure, there is no point in continuing in this path, go to the
        # pure decomposition instead
        if is_non_depolarizing(M, tol):  # False:  #
            print("The matrix M is pure.")
            Md = np.identity(4)
            Mr, Mp = decompose_pure(M, right=False, tol=tol)
            p1, p2, alphaP, deltaP, fiP, chiP = diattenuator(Mp)
        else:
            if decomposition == 'DRP':
                # Calculate the diattenuator/polarizer
                p1, p2, alphaP, deltaP, fiP, chiP = diattenuator(M)
                Mp = stokes.general_diattenuator_parvect(
                    p1, p2, alphaP, deltaP, carac=True)
                D = self.parameters.diattenuation()
                # Check if the matrix M is singular or not.
                singM = is_singular2(M, tol=tol)
                singMp = is_singular2(Mp, tol=tol)
                if singMp:
                    # We have to determine if only Md is singular or not
                    P = polarizance(M)
                    cond3 = abs(1 - P) <= tol
                    if cond3:
                        # Print type of decomposition
                        if verbose:
                            print(
                                "Both the depolarizer and the polarizer are singular."
                            )
                        # Homogeneous case
                        Md = np.identity(4)
                        Mr, Mp = decompose_pure(M, right=False, tol=tol)
                    else:
                        # Print type of decomposition
                        if verbose:
                            print("The polarizer is singular.")
                        # Calculate the depolarizer polarizance vector
                        Dv, Pv, m, m00 = divide_in_blocks(M)
                        Pdv = (Pv - m * Dv.T) / (1 - D**2)
                        Mr = np.identity(4)
                        cero = np.zeros(3)
                        ceroM = np.zeros((3, 3))
                        Md = self.from_blocks(cero, Pdv, ceroM)
                else:
                    # Calculate the depolarizer polarizance vector
                    Dv, Pv, m, m00 = divide_in_blocks(M)
                    Pdv = (Pv - m * Dv.T) / (1 - D**2)
                    # For calculating the small matrix m of the depolarizer we need an
                    # auxiliary matrix mf
                    Gaux = matrix(np.diag([1, -1, -1, -1]))
                    if singM:
                        Mpinv = Gaux * Mp * Gaux / D**2
                    else:
                        Mpinv = Gaux * Mp * Gaux / (1 - D**2)
                    Mf = M * Mpinv
                    _, _, mf, _ = divide_in_blocks(Mf)
                    md2 = mf * mf.T
                    qi2, mr2 = np.linalg.eig(md2)
                    qi2, mr2 = order_eig(qi2, mr2)
                    # check_eig(qi2, mr2, md2)
                    qi = np.sqrt(qi2)
                    cero = np.zeros(3)
                    # Calculation method depends on Md being singular or not
                    if singM:  # If M is singular and Mp is not => Md is singular
                        # Calculate the number of eigenvalues that are zero
                        nz = sum(qi < tol)
                        # Calculate other auxiliary matrices and vectors
                        md1 = mf.T * mf
                        qi12, mr1 = np.linalg.eig(md1)
                        qi12, mr1 = order_eig(qi12, mr1)
                        v1, v2, w1, w2 = (mr2[:, 0], mr2[:, 1], mr1[0, :].T,
                                          mr1[1, :].T)
                        if nz == 3:
                            # Print type of decomposition
                            if verbose:
                                print(
                                    "Depolarized matrix singular case with three null eigenvalues."
                                )
                            # Trivial case
                            md = np.zeros([3, 3])
                            Md = self.from_blocks(cero, Pdv, md)
                            Mr = np.eye(4)
                        elif nz == 2:
                            # Print type of decomposition
                            if verbose:
                                print(
                                    "Depolarized matrix singular case with two null eigenvalues."
                                )
                            # Depolarizer
                            md = mf * mf.T / sqrt(np.trace(mf * mf.T))
                            Md = self.from_blocks(cero, Pdv, md)
                            # Retarder
                            cR = np.trace(mf) / sqrt(np.trace(mf * mf.T))
                            R = np.arccos(cR)
                            x1 = np.cross(v1.T, w1.T)
                            Mr = stokes.general_retarder_vect(
                                R, R * x1 / np.linalg.norm(x1))
                        else:
                            # Print type of decomposition
                            if verbose:
                                print(
                                    "Depolarized matrix singular case with one null eigenvalue."
                                )
                            # Depolarizer
                            md = (qi[0] + qi[1]) * (mf * mf.T + qi[0] * qi[1] *
                                                    np.eye(3)).I * mf * mf.T
                            Md = self.from_blocks(cero, Pdv, md)
                            # Retarder
                            (y1, y2) = (np.cross(v1.T, v2.T),
                                        np.cross(w1.T, w2.T))
                            mr = v1 * w1.T + v2 * w2.T + y1 * y2.T / (
                                np.linalg.norm(y1) * np.linalg.norm(y2))
                            Mr = self.from_blocks(cero, cero, mr)
                    else:
                        # Print type of decomposition
                        if verbose:
                            print("General case.")
                        # General case
                        s = np.sign(np.linalg.det(M))
                        md = np.diag([qi[0], qi[1], s * qi[2]])
                        md = mr2 * md * mr2.T
                        Md = self.from_blocks(cero, Pdv, md)
                        # Calculate the retarder
                        mdinv = mr2 * np.diag(
                            [1 / qi[0], 1 / qi[1], s / qi[2]]) * mr2.T
                        mr = mdinv * mf
                        Mr = self.from_blocks(cero, cero, mr)
            else:
                raise ValueError("Decomposition not yet implemented.")
        # Order the output matrices
        Mout = [0, 0, 0]
        for ind in range(3):
            if decomposition[ind] == 'D':
                Mout[ind] = Md
            elif decomposition[ind] == 'P':
                Mout[ind] = Mp
            else:
                Mout[ind] = Mr
        # Calculate parameters
        if verbose or give_all:
            R, alphaR, deltaR, fiR, chiR = retarder(Mr)
            Pd = polarizance(Md)
            Desp = depolarization_degree(Md)
        # Calculate error
        if give_all or verbose:
            if decomposition == 'DRP':
                Mt = Md * Mr * Mp
                D = np.abs(Mt - M)
            MeanErr = np.std(np.square(D))
            MaxErr = D.max()
        # Print results
        if verbose:
            if decomposition == 'DRP':
                print("Polar decomposition of the matrix M = Mdesp * Mr * Mp:")
            for ind in range(3):
                print("")
                if decomposition[ind] == 'D':
                    print("The depolarizer Mueller matrix is:")
                    print(Md)
                    print("Parameters:")
                    print(("  - Polarizance = {}.".format(Pd)))
                    print(("  - Depolarization degree = {}.".format(Desp)))
                elif decomposition[ind] == 'P':
                    print("The diatenuator/polarizer Mueller matrix is:")
                    print(Mp)
                    print("Parameters:")
                    print(("  - p1 = {}; p2 = {}.".format(p1, p2)))
                    print(("  - Angle = {}º; Delay between components = {}º.".
                           format((alphaP / degrees), (deltaP / degrees))))
                    print(("  - Azimuth = {}º; Ellipticity = {}º.".format(
                        (fiP / degrees), (chiP / degrees))))
                else:
                    print("The retarder Mueller matrix is:")
                    print(Mr)
                    print("Parameters:")
                    print(("  - Delay = {}º.".format((R / degrees))))
                    print(("  - Angle = {}º; Delay between components = {}º.".
                           format((alphaR / degrees), (deltaR / degrees))))
                    print(("  - Azimuth = {}º; Ellipticity = {}º.".format(
                        (fiR / degrees), (chiR / degrees))))
            print("")
            print(("The mean square error in the decomposition is: {}".format(
                MeanErr)))
            print(
                ("The maximum error in the decomposition is: {}".format(MaxErr)
                 ))
            print("------------------------------------------------------")
        # Dictionary of parameters
        if give_all:
            param = dict(
                Delay=R,
                AngleR=alphaR,
                AxisDelayR=deltaR,
                AzimuthR=chiR,
                EllipticityR=fiR,
                p1=p1,
                p2=p2,
                AngleP=alphaP,
                AxisDelayP=deltaP,
                AzimuthP=fiP,
                EllipticityP=chiP,
                DespPolarizance=Pd,
                DespDegree=Desp,
                MeanError=MeanErr,
                MaxError=MaxErr)
        # Output
        if give_all:
            return Mout[0], Mout[1], Mout[2], param
        else:
            return Mout[0], Mout[1], Mout[2]


class Check_Mueller(object):
    """Class for Check of Mueller Matrices

    Parameters:
        mueller_matrix (Mueller_matrix): Mueller Matrix

    Attributes:
        self.M (Mueller_matrix)
        self.dict_params (dict): dictionary with parameters
    """

    def __init__(self, Mueller_matrix=zero_mueller):
        self.M = Mueller_matrix
        self.dict_params = {}

    def __repr__(self):
        """print all parameters"""
        self.get_all()
        header = "parameters:\n"
        # text = json.dumps(self.dict_params, indent=4)
        text = self.dict_params.__repr__()
        text = text.replace(",", "\n    ", 7)
        text = text.replace("{", "")
        text = text.replace("}", "")

        text = "    " + text
        return header + text

    def help(self):
        """prints help about dictionary"""

        text = "Here we explain the meaning of parameters.\n"
        text = text + "    intensity: intensity of the light beam.\n"
        text = text + "    TODO"
        print(text)

    def method_test(self):
        """Test about storing parent object."""
        parent = self.parent
        D = parent.parameters.diattenuation()
        print(D)
        return parent

    def is_real(self, tol=tol_default, give_all=False):
        """Conditions of physical realizability,

        .. math:: cond0a: m_{00} \leq 1
        .. math:: cond0b: m_{00} \geq  0
        .. math:: cond1: Tr(M*M_t)\leq 4(m_{00})^2
        .. math:: cond2: m_{00}\geq abs(m_{ij})
        .. math:: cond3a: (m_{00})^2\geq b^2
        .. math:: cond3a: (m_{00})^2\geq b'^2
        .. math:: cond4: (m_{00}-b)^2\geq \sum(m_{0j}-\sum(m_{jk} a_k))
        .. math:: cond5a: Tmax=m_{00}+b\leq 1
        .. math:: cond5a: Tmax_inv=m_{00}+b'\leq 1
        .. math:: cond6a: Eig(H)  \geq  0
        .. math:: cond6b:  Eig(H) \leq  0

        where

        .. math:: b=sqrt(m_{01}^2+m_{02}^2+m_{03}^2)

        .. math:: a_j=m_{0j}/b


        .. math:: b'=\sqrt(m_{10}^2+m_{20}^2+m_{30}^2)


        .. math:: a'_j=m_{j0}/b'.

        it also returns distance, if positive, it is fullfilled

        References:
            Handbook of Optics vol 2. 22.34

        Parameters:
            tol (float): Tolerance in equality conditions
            give_all (bool): If true, the function will return the individual
                conditions and distances.

        Returns:
            cond (bool): Is real or not.
            ind (dictionary): dictionary with condition, True/False, distance

        Todo:
            condition 4 does not work. In addition I do not understand when
            M=matrix(sp.eye(4)) since b=0 and a= indeterminate

        """

        M = self.M
        b = sqrt(M[0, 1]**2 + M[0, 2]**2 + M[0, 3]**2)
        bp = sqrt(M[1, 0]**2 + M[2, 0]**2 + M[3, 0]**2)

        c0a = M[0, 0]
        c0b = M[0, 0]
        c1 = 4 * M[0, 0]**2 - np.trace(M * M.T)
        c2 = M[0, 0] - (abs(M).max())
        c3a = M[0, 0]**2 - b**2
        c3b = M[0, 0]**2 - bp**2
        # a = M[0, :] / b
        # t1 = float(sum(M[:, 1:-1].transpose(>) * a.transpose()))
        # c4 = (M[0, 0] - b)**2 - sum(array(M[0, 1::]) - t1)
        c5a = -M[0, 0] - b + 1
        c5b = -M[0, 0] - bp + 1

        H = self.covariance_matrix()
        l_n, _ = np.linalg.eig(H)
        l_n = np.sort(np.real(l_n))
        c6 = l_n.min()

        cond0a = c0a >= -tol
        cond0b = c0b <= 1 + tol
        cond1 = c1 >= -tol
        cond2 = c2 >= -tol
        cond3a = c3a >= -tol
        cond3b = c3b >= -tol
        cond5a = c5a >= -tol
        cond5b = c5b >= -tol
        cond6 = c6 >= -tol
        cond = cond0a and cond0b and cond1 and cond2 and cond3a and cond3b and cond5a and cond5b and cond6

        conditions = dict(
            cond0a=[c0a, cond0a],
            cond0b=[c0b, cond0b],
            cond1=[c1, cond1],
            cond2=[c2, cond2],
            cond3a=[c3a, cond3a],
            cond3b=[c3b, cond3b],
            # cond4=[c4, c4 >= 0],
            cond5a=[c5a, cond5a],
            cond5b=[c5b, cond5b],
            cond6=[c6, cond6])
        if individual:
            return cond, conditions
        else:
            return cond

    def is_non_depolarizing(self, tol=tol_default, give_all=False):
        """Checks if matrix is non-depolarizing (the degree of polarimetric purity
        must be 1).

        Parameters:
            tol (float): Tolerance in equality conditions
            give_all (bool): If true, the complete output will be thrown.

        Returns:
            cond (bool): True if non-depolarizing
        """
        PD = self.parameters.polarimetric_purity()
        cond = 1 - PD <= tol
        if give_all:
            return cond, PD
        else:
            return cond

    def is_homogeneous(self, tol=tol_default, give_all=False):
        """Checks if the matrix is homogeneous. The inhomogeneity parameter must be 0 if M is homogeneous

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016), pp 119.

        Parameters:
            tol (float): Tolerance in equality conditions.
            give_all (bool): If true, the complete output will be thrown.

        Returns:
            (bool): True if non-depolarizing.
            (float): Inhomogeneity factor.
        """
        eta = self.inhomogeneity()
        cond = eta <= tol
        if give_all:
            return cond, eta
        else:
            return cond

    def is_homogeneous2(self, tol=tol_default, give_all=False):
        """Checks if the matrix is homogeneous. A matrix is homogeneous if P == D (vectors).It can be measured from the inhomogeneity parameter.


        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016), pp 119.


        Parameters:
            tol (float): Tolerance in equality conditions.
            give_all (bool): If true, the complete output will be thrown.

        Returns:
            (bool): True if non-depolarizing.
            (float): Inhomogeneity factor.
        """
        M = self.M
        u = (M[1:4, 0]
             ).T  # TODO: (Jesus) Cambiar por vectores D y P por elegancia
        v = M[0, 1:4]
        d = np.power(u - v, 2)
        f = sqrt(np.sum(d)) / 3
        if abs(f) <= tol:
            cond = True
        else:
            cond = False
        if give_all:
            return cond, f
        else:
            return cond

    def is_retarder(self, tol=tol_default, give_all=False):
        """Checks if the matrix M corresponds to a pure retarder.There are three
        conditions:
            1) ||P|| = P = 0
            2) ||D|| = D = 0
            3) M^T = M^(-1)

            We can define a non-retarder factor as:
            .. math:: f = \sqrt(\sum((M^T-M^{-1})^2)

        Parameters:
            tol (float): Tolerance in equality conditions.
            give_all (bool): If true, the complete output will be thrown.

        Returns:
            give_all = False
                (bool): True if is a retarder.
            give_all = True
                (1x4 bool): Global and each of the three conditions.
                (1x3 float): P, D and f.
        """
        # divide in blocks to take the m matrix
        M = self.M
        D, P, m, m00 = divide_in_blocks(M)
        # Check that D and P are 0.
        c1 = np.linalg.norm(P) / 3
        c2 = np.linalg.norm(D) / 3
        cond1 = c1 <= tol
        cond2 = c2 <= tol
        # Check that the matrix is not singular (if it is, its not a retarder)
        if np.linalg.det(
                m) < 1e-8:  # No use of tol here, as it is mathematical
            if give_all:
                return [False, False, False, False], [0, 0, 0]
            else:
                return False
        # Check that the matrix corresponds to a retarder
        aux = m.I - m.T
        f = sqrt(np.sum(np.power(aux, 2)))
        cond3 = f <= tol
        cond = cond1 and cond2 and cond3
        if give_all:
            return [cond, cond1, cond2, cond3], [c1, c2, f]
        else:
            return cond

    def is_diattenuator(self, tol=tol_default, give_all=False):
        """Checks if the matrix M corresponds to a pure homogeneous diattenuator.
        The condition is M = M^T.

        Parameters:
            tol (float): Tolerance in equality conditions.
            give_all (bool): If true, the complete output will be thrown.

        Returns:
            cond (bool): True if is a polarizer.
            d (float): distance to violate the condition.
        """
        M = self.M
        d = abs(M - M.T)
        d = np.sum(d) / 16
        cond = d <= tol
        if give_all:
            return cond, d
        else:
            return cond

    def is_singular(self, tol=tol_default, give_all=False):
        """Checks if the matrix is singular. A matrix is homogeneous if det(M) = 0.


        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016)


        Parameters:
            tol (float): Tolerance in equality conditions.
            give_all (bool): If true, the complete output will be thrown.

        Returns:
            (bool): True if non-depolarizing.
        """
        M = self.M
        det = np.linalg.det(M)
        cond = abs(det) <= tol**2
        if give_all:
            return cond, det
        else:
            return cond

    def is_singular2(self, tol=tol_default, give_all=False):
        """Checks if the matrix is singular. A matrix is singular if any of its eigenvalues is 0.

        References:
            J.J. Gil, R. Ossikovsky "Polarized light and the Mueller Matrix approach", CRC Press (2016)

        Parameters:
            tol (float): Tolerance in equality conditions.
            give_all (bool): If true, the complete output will be thrown.

        Returns:
            (bool): True if non-depolarizing.
        """
        M = self.M
        l, _ = np.linalg.eig(M)
        ml = min(abs(l))
        cond = ml <= tol
        if give_all:
            return cond, ml
        else:
            return cond
