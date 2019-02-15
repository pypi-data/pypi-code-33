# Copyright (C) 2019 demetriou engineering ltd.
# Part of `dx-utilities`, licensed under the AGPLv3+
"""Functions for linear algebra operations with numpy."""
import numpy as np

from .exceptions import CodedValueError


def project(source_vector_array, target_vector):
    """Calculate the projection of a sequence
    of vectors onto a target vector.

    :param source_vector_array: The array of the
        vectors to be projected.
    :type source_vector_array: `numpy.array`
    :param target_vector: The vector that lies on the projection
        line
    :type target_vector: `tuple` or `numpy.array`
    :rtype: `numpy.array`
    :return: An array of the shame shape as the source_vector_array.
    :raises ValueError: If projections is impossible due to ill-defined
        source or target vectors.
    """
    ref_vector = np.array(target_vector)
    if len(ref_vector.shape) > 1:
        return NotImplemented
    else:
        if ref_vector.shape[0] != source_vector_array.shape[1]:
            raise CodedValueError(1013, "Source and target vectors do not conform.")
        ref_unit_vector = ref_vector / np.linalg.norm(ref_vector)

    projection_factors = np.einsum(
        '...j,j', source_vector_array, ref_unit_vector
        )

    return projection_factors.reshape(-1, 1)*ref_unit_vector.reshape(1, -1)


def reflect(vector_array, normal=(1., 0., 0.), origin=(0., 0., 0.)):
    """Reflect a vector array with respect to the plane with the
    specified normal.

    :param vector_array: The array of the vectors
        to be projected.
    :type vector_array: `numpy.array`
    :param tuple normal: The vector normal to the projection
        plane.
    :rtype: `numpy.array`
    :param tuple origin: The origin of the reflection plane.
    """
    # Evaluate the projections along the normal
    size = vector_array.shape[1]
    normal = np.array(normal[:size])
    origin = np.array(origin[:size])
    vector_array_local = vector_array - origin
    projections_normal = project(vector_array_local, normal)
    return vector_array_local - 2*projections_normal + origin
