import sys
sys.path.insert(0, './')

import open3d as o3
import numpy as np
import pointframes as pf

def read_blender_cameras(filepath):
    """ Read blender camera export into list of camera objects.
        Assumes file is written with header and order:
        frame, X, Y, Z, rX, rY, rZ, c, fov, sensor_x, sensor_y, res_x, res_y

        args:
            filepath : string

        returns:
            list (containing CameraObject objects)
    """

    camera_data = np.loadtxt(filepath, delimiter=',', skiprows=1)

    cam_list = []

    for i, cam in enumerate(camera_data):
        c = pf.CameraObject()
        c.name = 'frame_'+str(i)+'.png'
        c.x = cam[1]
        c.y = cam[2]
        c.z = cam[3]
        c.euler_angles = [cam[4], cam[6], cam[5]]
        c.focal_length = cam[7]
        c.fov = cam[8]
        c.sensor_size = [cam[9], cam[10]]
        c.resolution = [cam[11], cam[12]]
        c.principle_point = [0, 0]
        c.euler_to_rotation_matrix()
        cam_list.append(c)

    return cam_list

if __name__ == '__main__':

    cam_list = read_blender_cameras('./examples/data/blender_cameras.txt')
    cam_xyz = []

    for cam in cam_list:
        if int(cam.name.split('.')[0].split('_')[-1])%100 == 0:
            cam_xyz.append(cam)

    bbox_list = []
    for cam in cam_xyz:
        bbox, _, _ = pf.view_frustum_bbox(cam, 5, 20)
        bbox = np.hstack((bbox, np.zeros((8, 3))))
        bbox[:, 5] = 1
        bbox = np.vstack((bbox, np.array([cam.x, cam.y, cam.z, 0, 0, 0])))
        [bbox_list.append(i) for i in bbox]

    pfpc = pf.PointCloud()
    pfpc.read_pointcloud('./examples/data/street_pc_full.asc')
    pfpc.data.columns=['X', 'Y', 'Z', 'class']
    #pfpc.data = pf.downsample(pfpc.data, min_cube_size=.5, class_ind=3)
    mls = pfpc.data[['X', 'Y', 'Z']].values
    mls = np.hstack((mls, np.zeros((mls.shape[0], 3))))
    mls[:, 3:] = [1, 0, 0]

    bbox_list = np.array(bbox_list)
    bbox_list = np.vstack((bbox_list, mls))
    pc = o3.PointCloud()
    pc.points = o3.Vector3dVector(bbox_list[:,:3])
    pc.colors = o3.Vector3dVector(bbox_list[:,3:])
    o3.draw_geometries([pc])
