import pandas as pd
import numpy as np
import math
import pointframes as pf

def euler_to_rotation_matrix(alpha=0.0, beta=0.0, gamma=0.0):
    """ Euler angles (degrees) to rotation matrix """

    alpha = np.radians(alpha)
    beta = np.radians(beta)
    gamma = np.radians(gamma)

    R_x = np.array([[1, 0              ,  0              ],
                    [0, math.cos(alpha), -math.sin(alpha)],
                    [0, math.sin(alpha),  math.cos(alpha)]])

    R_y = np.array([[math.cos(beta),  0, math.sin(beta)],
                    [0,               1,              0],
                    [-math.sin(beta), 0, math.cos(beta)]])

    R_z = np.array([[math.cos(gamma), -math.sin(gamma), 0],
                    [math.sin(gamma),  math.cos(gamma), 0],
                    [0,                0,               1]])

    R = np.dot(R_z, np.dot(R_y, R_x))
    return R

def rotate_euler(pointcloud, alpha, beta, gamma):
    ''' Function to rotate a point cloud object by
        the three euler angles
        args:
            pointcloud : Pandas Dataframe
            alpha      : float
            beta       : float
            gamma      : float
        returns:
            PointCloud
    '''

    rotation_matrix = euler_to_rotation_matrix(alpha=alpha, beta=beta, gamma=gamma)
    p_vals = pointcloud[['X', 'Y', 'Z']].values

    for idx, point in enumerate(p_vals):
        p_vals[idx] = np.dot(rotation_matrix, point)
    pointcloud[['X','Y','Z']] = p_vals

    return pointcloud

def translate(pointcloud, x, y, z):
    ''' Function to translate a point cloud object by
        x, y and z components
        args:
            pointcloud: PointCloud() object
            x: float
            y: float
            z: float
        returns:
            PointCloud
    '''
    t_mat = np.zeros((4, 4), dtype=float)
    t_mat = np.array([[1.0, 0.0, 0.0, 0.0],
                      [0.0, 1.0, 0.0, 0.0],
                      [0.0, 0.0, 1.0, 0.0],
                      [0.0, 0.0, 0.0, 1.0]])
    t_mat[:3, 3] = [x, y, z]

    p_vals = pointcloud[['X', 'Y', 'Z']].values
    p_vals = np.hstack((p_vals, np.ones((p_vals.shape[0], 1))))

    for idx, point in enumerate(p_vals):
        p_vals[idx] = np.dot(t_mat, point)
    pointcloud[['X', 'Y', 'Z']] = p_vals[:,:3]

    return pointcloud

def rotate_and_translate(pointcloud, euler_angles=[0.0, 0.0, 0.0], translation=[0.0, 0.0, 0.0]):
    ''' Function to rotate and translate a point cloud object by
        three euler angeles and an x, y, z translation
        args:
            pointcloud: PointCloud() object
            euler_angles : Array [3 x 1]
            translation  : Array [3 x 1]
        returns:
            PointCloud
    '''

    R_mat = euler_to_rotation_matrix(alpha=euler_angles[0],
                                     beta=euler_angles[1],
                                     gamma=euler_angles[2])

    RT_mat = np.zeros((4, 4), dtype=float)
    RT_mat[0:3, 0:3] = R_mat
    RT_mat[:3, 3] = translation
    RT_mat[3, 3] = 1.0

    p_vals = pointcloud[['X', 'Y', 'Z']].values

    p_vals = pointcloud[['X', 'Y', 'Z']].values
    p_vals = np.hstack((p_vals, np.ones((p_vals.shape[0], 1))))

    for idx, point in enumerate(p_vals):
        p_vals[idx] = np.dot(RT_mat, point)

    pointcloud[['X', 'Y', 'Z']] = p_vals[:,:3]
    return pointcloud
