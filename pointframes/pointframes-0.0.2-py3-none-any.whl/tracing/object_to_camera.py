import sys
sys.path.insert(0, './')

import numpy as np
import pandas as pd
import math
import time
import pointframes as pf
import cv2

def point_to_pixel(point, camera, pix=True):
    """ Function to compute the pixel coordinates of a given
        point in world space for a given camera.

        args:
            point  : vector 1x3 (list or numpy) [X, Y, Z]
            camera : CameraObject class
            pix    : Bool
                        Return measurement in pixel coordinates
        returns:
            list : [x, y]
                Returns None if point is not visible in camera
        """

    p = point
    c = [camera.x, camera.y, camera.z]
    r = camera.rotation_matrix

    if pix == True:
        assert camera.resolution is not None, "[error] resolution must be available to return in pixel coordinates"

    # Compute collinearity equation. Equation taken from Luhmann et al., 2014
    x_ = ( (r[0,0] * (p[0]-c[0])) + (r[1,0] * (p[1]-c[1])) + (r[2,0] * (p[2]-c[2])) ) / \
         ( (r[0,2] * (p[0]-c[0])) + (r[1,2] * (p[1]-c[1])) + (r[2,2] * (p[2]-c[2])) )

    y_ = ( (r[0,1] * (p[0]-c[0])) + (r[1,1] * (p[1]-c[1])) + (r[2,1] * (p[2]-c[2])) ) / \
         ( (r[0,2] * (p[0]-c[0])) + (r[1,2] * (p[1]-c[1])) + (r[2,2] * (p[2]-c[2])) )

    x_ = ( camera.principle_point[0] + (-camera.focal_length * x_) )
    y_ = ( camera.principle_point[1] + (-camera.focal_length * y_) )

    # Check if point is within sensor range
    if abs(x_) > camera.sensor_size[0]/2 or abs(y_) > camera.sensor_size[1]/2:
        return [None, None]

    if pix == True:
        x_ = (x_ + (camera.sensor_size[0]/2)) / (camera.sensor_size[0]/camera.resolution[0])
        y_ = (y_ + (camera.sensor_size[1]/2)) / (camera.sensor_size[1]/camera.resolution[1])

    return [x_, y_]

def points_to_camera_coords(pointcloud, camera_objects, open_cv=False):
    """ Store for each point it's location in every camera
        for a given list of Camera() objects. Currently assumes
        no distortion is present. WILL UPDATE SOON.

        args:
            pointcloud     : pandas dataframe
            camera_objects : list (containing Camera() objects)
            open_cv        : bool
                                 Use OpenCV projectPoints function
        returns:
            pandas dataframe
    """

    pf.check_attributes(pointcloud, ['X', 'Y', 'Z'])

    # Find indicies for X,Y,Z columns
    xyz_idx = [pointcloud.columns.get_loc('X'),
               pointcloud.columns.get_loc('Y'),
               pointcloud.columns.get_loc('Z')]

    # Store columns and convert to numpy array for efficiency
    columns = pointcloud.columns
    pointcloud = pointcloud.values

    # Check if camera coordinates are already present
    if 'cam_coord' in columns:
        cam_coord_idx = np.where(columns=='cam_coord')[0][0]
    else:
        # Make a new column in array
        tmp_arr = np.zeros((pointcloud.shape[0], pointcloud.shape[1]+1), dtype='object')
        tmp_arr[:, :-1] = pointcloud
        pointcloud = tmp_arr
        tmp_arr = None
        cam_coord_idx = -1

    # Loop through all points in pointcloud
    for idx, point in enumerate(pointcloud[:, xyz_idx]):
        cam_list = []
        # Loop through each camera in scene
        # TODO: No need to go through every camera
        for camera in camera_objects:
            # Check if we need to compute rotation matrix
            assert camera.euler_angles, 'Error: Camera object must have euler angles'
            if camera.rotation_matrix is None:
                camera.euler_to_rotation_matrix()
            # Comptute pixel coordinates

            if open_cv == False:
                x_, y_ = point_to_pixel(point[xyz_idx], camera)
                if x_ is not None or y_ is not None:
                    cam_list.append([camera.name, [x_, y_]])
            else:
                rvec = np.zeros((1,3))
                rvec = cv2.Rodrigues(camera.rotation_matrix, rvec)[0]
                tvec = np.array([camera.x, camera.y, camera.z])
                img_coord = cv2.projectPoints(np.array([point.astype(np.float64)]), rvec, tvec, camera.camera_matrix, camera.dist_coef)[0]
                if abs(img_coord[0][0][0]) <= camera.sensor_size[0]/2 or abs(img_coord[0][0][1]) <= camera.sensor_size[1]/2:
                    cam_list.append([camera.name, [img_coord[0][0][0], img_coord[0][0][1]]])

        pointcloud[idx][cam_coord_idx] = cam_list
        if idx%10000 == 0:
            print ('processed point: {:}'.format(idx))

    # Check if we need to create new column for dataframe
    if 'cam_coord' in columns:
        pointcloud = pd.DataFrame(data=pointcloud, columns=columns)
    else:
        pointcloud = pd.DataFrame(data=pointcloud, columns=columns.insert(len(columns), 'cam_coord'))

    return pointcloud


if __name__ == '__main__':

    pc = pf.PointCloud()
    pc.read_pointcloud('./examples/data/street_pc_full.asc')
    pc.data.columns=['X', 'Y', 'Z', 'class']

    pc = pd.DataFrame(data = np.array([[-37.074348, -3.559017, 0.184227, 1]]), columns=['X', 'Y', 'Z', 'class'])

    cam_list = pf.read_blender_cameras('./examples/data/blender_cameras.txt')
    cam_xyz = []

    for cam in cam_list:
        cam.camera_matrix = np.eye(3)
        cam.dist_coef = np.zeros((1, 5))

    for cam in cam_list:
        if int(cam.name.split('.')[0].split('_')[-1]) == 400:
            cam_xyz.append(cam)


    pc.data = points_to_camera_coords(pc, cam_xyz, open_cv=False)

    for p in pc.data.values:
        print(p)
