import sys
sys.path.insert(0, './')

import pointframes as pf
import open3d as o3
import pandas as pd
import numpy as np
import math

def signed_distance(point, normals, plane_points):
    """ Compute the signed distance between plane and point"""
    for i, n in enumerate(normals):
        if np.dot(n, (point-plane_points[i])) < 0:
            return False
    return True


def translate_point(point, xT, yT, zT):
    """ Translate single point by X, Y, Z"""
    t_mat = np.identity(4)
    t_mat[:3, 3] = [xT, yT, zT]
    return np.dot(t_mat, np.insert(point, 3, 1))[:3]


def view_frustum_bbox(camera, near_distance, far_distance):
    """ Calculate the viewing frustum bounding box coordinates for
        a CameraObject class object.

        args:
            camera        : CameraObject class
            near_distance : float
            far_distance  : float
        returns:
            numpy ndarray bounding box coordinates (8x3)
                with order [near_top_left, near_top_right, near_bottom_left, near_bottom_right,
                            far_top_left, far_top_right, far_bottom_left, far_bottom_right]

            numpy ndarray (6x3) points on planes with order [near_centre, far_centre, near_left
                                                             near_right, near_bottom, near_top]

            numpy ndarray (6x3) plane normals with order [near_centre, far_centre, near_left,
                                                          near_right, near_bottom, near_top]
    """

    camera_xyz = np.array([camera.x, camera.y, camera.z])
    sensor_size = np.array(camera.sensor_size)
    if camera.rotation_matrix is None:
        camera.compute_rotation_matrix()
    rotation_matrix = camera.rotation_matrix

    cam_right = rotation_matrix[0]
    cam_up = -rotation_matrix[1]
    cam_front = rotation_matrix[2]

    near_height = 2 * math.tan(math.radians(camera.fov)/2) * near_distance
    far_height = 2 * math.tan(math.radians(camera.fov)/2) * far_distance
    near_width = near_height * sensor_size[0]/sensor_size[1]
    far_width = far_height * sensor_size[0]/sensor_size[1]

    near_centre = camera_xyz + (cam_front * near_distance)
    far_centre = camera_xyz + (cam_front * far_distance)

    near_top_left = near_centre + (cam_up * (near_height/2)) - (cam_right*(near_width/2))
    near_top_right = near_centre + (cam_up * (near_height/2)) + (cam_right*(near_width/2))
    near_bottom_left = near_centre - (cam_up * (near_height/2)) - (cam_right*(near_width/2))
    near_bottom_right = near_centre - (cam_up * (near_height/2)) + (cam_right*(near_width/2))
    far_top_left = far_centre + (cam_up * (far_height/2)) - (cam_right*(far_width/2))
    far_top_right = far_centre + (cam_up * (far_height/2)) + (cam_right*(far_width/2))
    far_bottom_left = far_centre - (cam_up * (far_height/2)) - (cam_right*(far_width/2))
    far_bottom_right = far_centre - (cam_up * (far_height/2)) + (cam_right*(far_width/2))

    ab = near_top_left - far_top_left
    ac = near_top_left - far_bottom_left
    n = np.cross(ab, ac)
    normal_left = n / np.linalg.norm(n, ord=1)
    normal_left = -normal_left

    ab = near_top_right - far_top_right
    ac = near_top_right - far_bottom_right
    n = np.cross(ab, ac)
    normal_right = n / np.linalg.norm(n, ord=1)

    ab = near_bottom_left - far_bottom_left
    ac = near_bottom_left - far_bottom_right
    n = np.cross(ab, ac)
    normal_bottom = n / np.linalg.norm(n, ord=1)
    normal_bottom = -normal_bottom

    ab = near_top_left - far_top_left
    ac = near_top_left - far_top_right
    n = np.cross(ab, ac)
    normal_top = n / np.linalg.norm(n, ord=1)

    normal_near = cam_front
    normal_far = -cam_front

    bbox = np.array([near_top_left,
                     near_top_right,
                     near_bottom_left,
                     near_bottom_right,
                     far_top_left,
                     far_top_right,
                     far_bottom_left,
                     far_bottom_right])

    normals = np.array([normal_near,
                        normal_far,
                        normal_left,
                        normal_right,
                        normal_bottom,
                        normal_top])

    plane_points = np.array([near_centre,
                             far_centre,
                             (near_centre - cam_right * near_width/2),
                             (near_centre + cam_right * near_width/2),
                             (near_centre - cam_up * near_height/2),
                             (near_centre + cam_up * near_height/2)])

    return bbox, normals, plane_points


def crop_frustum(camera, f_coords, crop_coords, near_distance, far_distance):
    """ Crop a frustum by 2D image coordinates. Image coordinates
        should be in the order [xmin, ymin, xmax, ymax]. Returns
        the new coordinates for frustum.

        args:
            camera : CameraObject
            f_coords : numpy ndarray (8x3)
            crop_coords : list or ndarray (1x4)
        returns:
            numpy ndarray (8x3)
    """

    cam_right = camera.rotation_matrix[0]
    cam_up = -camera.rotation_matrix[1]
    cam_front = camera.rotation_matrix[2]

    xmin, ymin, xmax, ymax = crop_coords

    # Normalise crop coordinates
    xmin_sf = float(xmin) / camera.resolution[0]
    xmax_sf = float(xmax) / camera.resolution[0]
    ymin_sf = float(ymin) / camera.resolution[1]
    ymax_sf = float(ymax) / camera.resolution[1]

    # Calculate XY width and height for near and far planes (sclaing factor)
    near_height = 2 * math.tan(math.radians(camera.fov)/2) * near_distance
    far_height = 2 * math.tan(math.radians(camera.fov)/2) * far_distance
    near_width = near_height * camera.sensor_size[0]/camera.sensor_size[1]
    far_width = far_height * camera.sensor_size[0]/camera.sensor_size[1]

    # Calculate translations for each point
    near_xminT = near_width*xmin_sf
    near_xmaxT = near_width*(1-xmax_sf)
    near_zminT = near_height*ymin_sf
    near_zmaxT = near_height*(1-ymax_sf)
    far_xminT = far_width*xmin_sf
    far_xmaxT = far_width*(1-xmax_sf)
    far_zminT = far_height*ymin_sf
    far_zmaxT = far_height*(1-ymax_sf)

    near_top_left = f_coords[0] - (cam_up*near_zmaxT) + (cam_right*near_xminT)
    near_top_right = f_coords[1] - (cam_up*near_zmaxT) - (cam_right*near_xmaxT)
    near_bottom_left = f_coords[2] + (cam_up*near_zminT) + (cam_right*near_xminT)
    near_bottom_right = f_coords[3] + (cam_up*near_zminT) - (cam_right*near_xmaxT)
    far_top_left = f_coords[4] - (cam_up*far_zmaxT) + (cam_right*far_xminT)
    far_top_right = f_coords[5] - (cam_up*far_zmaxT) - (cam_right*far_xmaxT)
    far_bottom_left = f_coords[6] + (cam_up*far_zminT) + (cam_right*far_xminT)
    far_bottom_right = f_coords[7] + (cam_up*far_zminT) - (cam_right*far_xmaxT)

    # Re-compute new normals
    n = np.cross((near_top_left-far_top_left), (near_top_left - far_bottom_left))
    normal_left = -(n / np.linalg.norm(n, ord=1))

    n = np.cross((near_top_right-far_top_right), (near_top_right-far_bottom_right))
    normal_right = n / np.linalg.norm(n, ord=1)

    n = np.cross((near_bottom_left-far_bottom_left), (near_bottom_left-far_bottom_right))
    normal_bottom = -(n / np.linalg.norm(n, ord=1))

    n = np.cross((near_top_left-far_top_left), (near_top_left-far_top_right))
    normal_top = n / np.linalg.norm(n, ord=1)

    normal_near = cam_front
    normal_far = -cam_front

    bbox = np.array([near_top_left,
                     near_top_right,
                     near_bottom_left,
                     near_bottom_right,
                     far_top_left,
                     far_top_right,
                     far_bottom_left,
                     far_bottom_right])

    normals = np.array([normal_near,
                        normal_far,
                        normal_left,
                        normal_right,
                        normal_bottom,
                        normal_top])

    near_centre = np.array([camera.x, camera.y, camera.z]) + (cam_front * near_distance)
    far_centre = np.array([camera.x, camera.y, camera.z]) + (cam_front * far_distance)

    plane_points = np.array([near_centre,
                             far_centre,
                             near_top_left,
                             near_top_right,
                             near_bottom_left,
                             near_top_left])

    return bbox, normals, plane_points

if __name__ == '__main__':

    camera = pf.CameraObject()
    camera.x = 0
    camera.y = 0
    camera.z = 0
    camera.euler_angles = [90, 0, 0]
    camera.sensor_size = [36, 24]
    camera.resolution = [2000, 1500]
    camera.fov = 50
    camera.principle_point = [0, 0]

    near_distance = 5
    far_distance = 20

    bbox, normals, plane_points = view_frustum_bbox(camera, near_distance=near_distance, far_distance=far_distance)

    bbox, normals, plane_points = crop_frustum(camera, bbox, [0, 0, 2000, 500])

    points = np.random.randint(low=-far_distance, high=far_distance, size=(100000, 3))

    inside = []
    outside = []

    for point in points:
        if signed_distance(point, normals, plane_points) == True:
            inside.append(point)
        else:
            outside.append(point)

    print (len(inside), len(outside))

    inside = np.array(inside)
    inside_arr = np.zeros((inside.shape[0]+8, 6))
    inside_arr[:-8,0:3] = inside
    inside_arr[:-8,3:6] = [1, 0, 0]
    inside_arr[-8:,0:3] = bbox
    inside_arr[-8:,3:6] = [0, 0, 0]

    outside = np.array(outside)
    outside_arr = np.zeros((outside.shape[0], 6))
    outside_arr[:,0:3] = outside
    outside_arr[:,3:6] = [0, 0, 1]

    data = np.vstack((inside_arr, outside_arr))

    pc = o3.PointCloud()
    pc.points = o3.Vector3dVector(data[:,0:3])
    pc.colors = o3.Vector3dVector(data[:,3:6])
    o3.draw_geometries([pc])

    data = np.vstack((bbox, plane_points[4:6]))
    #data = bbox
    pc = o3.PointCloud()
    pc.points = o3.Vector3dVector(data)
    o3.draw_geometries([pc])
