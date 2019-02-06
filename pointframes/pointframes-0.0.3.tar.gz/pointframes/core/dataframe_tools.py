import pandas as pd
import numpy as np
import open3d as o3
import pointframes as pf
import colorsys

def open3d_visualize(pointcloud, color_by_class=False):

    if color_by_class == False:
        pf.check_attributes(pointcloud, ['X', 'Y', 'Z'])
        o3pc = o3.PointCloud()
        o3pc.points = o3.Vector3dVector(pointcloud[['X','Y','Z']].values)
        o3.draw_geometries([o3pc])
    else:
        pf.check_attributes(pointcloud, ['X', 'Y', 'Z', 'class'])
        o3pc = o3.PointCloud()
        o3pc.points = o3.Vector3dVector(pointcloud[['X','Y','Z']].values)
        colors = pointcloud['class'].values
        colors /= np.max(np.abs(colors),axis=0)

        classes = np.linspace(0, 1, len(np.unique(colors)))

        unique_classes = np.unique(colors)

        rgb_classes = [colorsys.hsv_to_rgb(c, 0.8, 1) for c in classes]
        rgb_classes = np.array(rgb_classes)

        color_arr = np.zeros((colors.shape[0], 3))

        for idx, c in enumerate(colors):
            color_arr[idx] = rgb_classes[np.where(c==unique_classes)]

        o3pc.colors = o3.Vector3dVector(color_arr)
        o3.draw_geometries([o3pc])


def open3d_normals(pointcloud, radius=0.0, max_nn=0):

    pf.check_attributes(pointcloud, ['X', 'Y', 'Z'])
    o3pc = o3.PointCloud()
    o3pc.points = o3.Vector3dVector(pointcloud[['X','Y','Z']].values)
    o3.estimate_normals(o3pc, search_param = o3.KDTreeSearchParamHybrid(radius = radius, max_nn = max_nn))
    normals = np.asarray(o3pc.normals)

    pointcloud['nX'] = normals[:,0]
    pointcloud['nY'] = normals[:,1]
    pointcloud['nZ'] = normals[:,2]

    return pointcloud

def array_average(array):
    averages = []
    [averages.append(np.average(array[:,i], axis=0)) for i in range(0, array.shape[-1])]
    averages = np.array(averages)
    return averages

def get_class_mode(array):

    return np.argmax(np.bincount(array.flatten().astype(int)))


def downsample(pointcloud, min_cube_size=0.5, average_ind=None, class_ind=None):
    ''' Function to perform a voxel downsample for a dataframe.
        average_ind must be a list containing lists of column indicies
        to average during downsampling. If class_ind is valid, the mode
        is calculated to determine the downsampled points class.
        args:
            pointcloud    : pandas dataframe
            min_cube_size : float minimum size of voxel cubes
            average_ind   : list list containing lists of column indicies to average
            class_ind     : int index for class attribute
        returns:
            pointcloud    : pandas dataframe
    '''

    pc_arr = pointcloud.values
    columns = pointcloud.columns

    # Construct a list of columns to be processed
    column_ind = np.array([np.where(columns=='X')[0][0],
                           np.where(columns=='Y')[0][0],
                           np.where(columns=='Z')[0][0]])

    if average_ind is not None:
        for idx, set in enumerate(average_ind):
            for idx2, col in enumerate(set):
                average_ind[idx][idx2] = np.where(col==columns)[0][0]
        column_ind = np.append(column_ind, np.unique(average_ind))
    if class_ind is not None:
        column_ind = np.append(column_ind, class_ind)

    columns = columns[column_ind]

    # Create an Open3D pointcloud
    o3pc = o3.PointCloud()
    o3pc.points = o3.Vector3dVector(pointcloud[['X','Y','Z']].values)

    # Find minimum and maximum bounding for scene
    min_bound = o3pc.get_min_bound() - min_cube_size * 0.5
    max_bound = o3pc.get_min_bound() + min_cube_size * 0.5

    # Perform voxel downsampling
    pcd_curr_down, cubic_id = o3.voxel_down_sample_and_trace(o3pc,
                                                          min_cube_size,
                                                          min_bound,
                                                          max_bound,
                                                          False)
    pcd_curr_down_arr = np.asarray(pcd_curr_down.points)

    complete_array = []

    # TODO: This should be re-done to make it much faster
    # Most the overhead is on the averaging of points so
    # vectorizing this function would be a good start.

    if average_ind is not None or class_ind is not None:
        for i in range(0, pcd_curr_down_arr.shape[0]):
            for p in np.where(cubic_id[i]!=-1):
                tmp_arr = []
                if average_ind is not None:
                    for indices in average_ind:
                        averages = array_average(pc_arr[cubic_id[i][p]][:,indices])
                        tmp_arr = np.append(tmp_arr, averages)
                if class_ind is not None:
                    class_mode = get_class_mode(pc_arr[cubic_id[i][p]][:,class_ind])
                    if len(tmp_arr) > 0:
                        try:
                            tmp_arr = np.insert(tmp_arr, int(class_ind), class_mode)
                        except:
                            tmp_arr = np.insert(tmp_arr, -1, class_mode)
                    else:
                        tmp_arr = np.array((class_mode))
                complete_array.append(np.append(pcd_curr_down_arr[i], tmp_arr))
        complete_array = np.array(complete_array)
        pointcloud = pd.DataFrame(data=complete_array, columns=columns)
    else:
        pointcloud = pd.DataFrame(data=pcd_curr_down_arr, columns=columns)

    return pointcloud
