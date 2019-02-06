import numpy as np
import pointframes as pf

class CameraObject(object):
    """ Default class for a camera object with
        a known exterior orientation in a given
        coordinate system.

        Attributes:
        ------------
            x                     : float
            y                     : float
            z                     : float
            name                  : string
            euler_angles          : array 1x3 (deg)
            sensor_size           : array 1x2 (width x height) (mm)
            resolution            : array 1x2 (width x height) (pix)
            fov                   : float (deg)
            principle_point       : array 1x2 (mm)
            distortion_parameters : array 4x4
            rotation_matrix       : arrray 3x3
            camera_matrix         : array 3x3
            dist_coef             : array 1xn

        Functions:
        ------------
            euler_to_rotation_matrix  : Calculate euler to rotation matrix
            checkerboard_calibration  : Simple/extended checkerboard camera calibration
    """

    def __init__(self):

        self._x = None
        self._y = None
        self._z = None
        self._name = None
        self._euler_angles = None
        self._focal_length = None
        self._sensor_size = None
        self._resolution = None
        self._fov = None
        self._principle_point = None
        self._distortion_parameters = None
        self._rotation_matrix = None
        self._camera_matrix = None
        self._dist_coef = None

    @property
    def x(self):
        return self._x
    @x.setter
    def x(self, x):
        self._x = x

    @property
    def y(self):
        return self._y
    @y.setter
    def y(self, y):
        self._y = y

    @property
    def z(self):
        return self._z
    @z.setter
    def z(self, z):
        self._z = z

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, name):
        self._name = name

    @property
    def euler_angles(self):
        return self._euler_angles
    @euler_angles.setter
    def euler_angles(self, euler_angles):
        self._euler_angles = euler_angles

    @property
    def focal_length(self):
        return self._focal_length
    @focal_length.setter
    def focal_length(self, focal_length):
        self._focal_length = focal_length

    @property
    def sensor_size(self):
        return self._sensor_size
    @sensor_size.setter
    def sensor_size(self, sensor_size):
        self._sensor_size = sensor_size

    @property
    def resolution(self):
        return self._resolution
    @resolution.setter
    def resolution(self, resolution):
        self._resolution = resolution

    @property
    def fov(self):
        return self._fov
    @fov.setter
    def fov(self, fov):
        self._fov = fov

    @property
    def principle_point(self):
        return self._principle_point
    @principle_point.setter
    def principle_point(self, principle_point):
        self._principle_point = principle_point

    @property
    def distortion_parameters(self):
        return self._distortion_parameters
    @distortion_parameters.setter
    def distortion_parameters(self, distortion_parameters):
        self._distortion_parameters = distortion_parameters

    @property
    def rotation_matrix(self):
        return self._rotation_matrix
    @rotation_matrix.setter
    def rotation_matrix(self, rotation_matrix):
        self._rotation_matrix = rotation_matrix

    @property
    def camera_matrix(self):
        return self._camera_matrix
    @camera_matrix.setter
    def camera_matrix(self, camera_matrix):
        self._camera_matrix = camera_matrix

    @property
    def dist_coef(self):
        return self._dist_coef
    @dist_coef.setter
    def dist_coef(self, dist_coef):
        self._dist_coef = dist_coef


    def euler_to_rotation_matrix(self):
        self._rotation_matrix = pf.euler_to_rotation_matrix(self._euler_angles[0],
                                                            self._euler_angles[1],
                                                            self._euler_angles[2])


    def checkerboard_calibration(self, filepath, img_ext='jpg', cb_size=(7,7), extended=False):
        """ Compute intrinsic calibration parameters for given camera. If extended is true
            focal length, principle point and field of view will also be updated.

            args:
                self     : self
                filepath : String
                img_ext  : String
                cb_size  : tuble
                               Size of checkerboard
                extended : bool
        """

        if extended == False:
            mtx, dist = pf.simple_checkerboard_calibration(filepath, img_ext, cb_size)
            self._camera_matrix = mtx
            self._dist_coef = dist
        else:
            mtx, dist, fov_x, fov_y, c, principle_point = pf.extended_checkerboard_calibration(self,
                                                                                            filepath,
                                                                                            img_ext,
                                                                                            cb_size)
            self._camera_matrix = mtx
            self._dist_coef = dist
            # Need to calculate AFOV from hFOV and vFOV
            cam.fov = fov_x
            self._focal_length = c
            self._principle_point = [principle_point[0], principle_point[1]]
