import sys
sys.path.insert(0, './')

import pointframes as pf
import numpy as np

def calculate_awi(pointcloud, min_prob, calc_prob=True):
    """ Calculate the augmented weighting index.

        args:
            pointcloud : pandas dataframe
            min_prob   : float [0, 1]
                           minimum allowed probability

        returns:
            awi : float [0, 1]
    """

    if calc_prob == True:
        prob = pf.class_probabilities_index(pointcloud, min_prob=min_prob)
    else:
        pf.check_attributes(pointcloud, ['inv_prob'])
        prob = pointcloud['inv_prob'].values
    return float(len(np.where(prob>min_prob)[0]))/float(prob.shape[0])

def augment_rotation(pointcloud, rotation_axis, small_rotations=False, rotation_matrix=None):
    """ Function to augment a point cloud by rotating randomly along a given axis.
        If small_rotations is also True, then a small rotation will also be applied
        along all three axis. If rotation_matrix is not None then the augmentation will
        use the given rotation matrix.

        Code adapted from Pedro Hermosilla (pedro-1.hermosilla-casajus@uni-ulm.de)
        https://github.com/viscom-ulm/MCCNN/blob/master/utils/DataSet.py

        args:
            pointcloud      : pandas dataframe
            rotation_axis   : Int
                                Must be one of [0, 1, 2] i.e. X, Y, Z
            small_rotations : Bool
            rotation_matrix : numpy array [3 x 3]

        returns:
            pandas dataframe
    """

    pf.check_attributes(pointcloud, ['X', 'Y', 'Z'])

    rotation_axis = pointcloud.columns.get_loc(rotation_axis)

    rs = np.random.RandomState()

    xyz = pointcloud[['X', 'Y', 'Z']].values

    if rotation_matrix is None:
        # Compute the main rotation
        rotation_angle = rs.uniform() * 2.0 * np.pi
        cosval = np.cos(rotation_angle)
        sinval = np.sin(rotation_angle)
        if rotation_axis == 0:
            rotation_matrix = np.array([[1.0, 0.0, 0.0], [0.0, cosval, -sinval], [0.0, sinval, cosval]])
        elif rotation_axis == 1:
            rotation_matrix = np.array([[cosval, 0.0, sinval], [0.0, 1.0, 0.0], [-sinval, 0.0, cosval]])
        else:
            rotation_matrix = np.array([[cosval, -sinval, 0.0], [sinval, cosval, 0.0], [0.0, 0.0, 1.0]])

        # Compute small rotations.
        if small_rotations:
            angles = np.clip(0.06*rs.randn(3), -0.18, 0.18)
            Rx = np.array([[1.0, 0.0, 0.0],
                        [0.0, np.cos(angles[0]), -np.sin(angles[0])],
                        [0.0, np.sin(angles[0]), np.cos(angles[0])]])
            Ry = np.array([[np.cos(angles[1]), 0.0, np.sin(angles[1])],
                        [0.0, 1.0, 0.0],
                        [-np.sin(angles[1]), 0.0, np.cos(angles[1])]])
            Rz = np.array([[np.cos(angles[2]), -np.sin(angles[2]), 0.0],
                        [np.sin(angles[2]), np.cos(angles[2]), 0.0],
                        [0.0, 0.0, 1.0]])
            R = np.dot(Rz, np.dot(Ry,Rx))
            rotation_matrix = np.dot(R, rotation_matrix)

    xyz = np.dot(xyz, rotation_matrix)

    pointcloud[['X', 'Y', 'Z']] = xyz

    return pointcloud
