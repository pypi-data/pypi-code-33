import pandas as pd
import pointframes as pf

class PointCloud(object):
    ''' Generic point cloud class which holds dataframe and
        any other attributes required.

        Default class for a camera object with
        a known exterior orientation in a given
        coordinate system.

        Attributes:
        ------------
            data : pandas dataframe

        Functions:
        ------------
            calculate_normals     : Calculate normals for local point neighbourhoods
            visualize             : Visualise point cloud in Open3D
            read_pointcloud       : read a pointcloud into data attribute
            create_pid            : Generate point ID column
            write_pointcloud      : Write point cloud to file
            translate             : Translate point cloud by X, Y, Z
            rotate_euler          : Rotate point cloud by three euler angles
            rotate_and_translate  : Rotate and translate by X, Y, Z and euler angles
            calculate_eigenvalues : Calculate three eigen values for local point neighbourhoods
    '''

    def __init__(self):

        self._data = None

    @property
    def data(self):
        return self._data
    @data.setter
    def data(self, data):
        self._data = data

    def calculate_normals(self, radius=0.0, max_nn=0):

        pc = pf.open3d_normals(self._data, radius=radius, max_nn=max_nn)
        self._data = pc

    def visualize(self, color_by_class=False):
        pf.open3d_visualize(self._data, color_by_class)

    def read_pointcloud(self, pointcloud_path):
        self._data = pf.read_pointcloud(pointcloud_path)

    def create_pid(self, start_idx=0):
        self._data.insert(0, 'pID', pd.Int64Index(self._data.index+start_idx))

    def write_pointcloud(self, save_path):
        pf.write_pointcloud(self._data, save_path)

    def translate(self, x, y, z):
        self._data = pf.translate(self._data, x, y, z)

    def rotate_euler(self, alpha, beta, gamma):
        self._data = pf.rotate_euler(self._data, alpha, beta, gamma)

    def rotate_and_translate(self, euler_angles, translation):
        self._data = pf.rotate_and_translate(self._data, euler_angles, translation)

    def calculate_eigenvalues(self, nn=30, features=[], leaf_size=40):
        self._data = pf.compute_eigenvalues(self._data, nn, features=features, leaf_size=40)
