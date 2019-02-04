import sys
sys.path.insert(0, './')

import cv2
import numpy as np
import glob
import pylab as plt
import pointframes as pf

def extended_checkerboard_calibration(cam, filepath, img_ext='jpg', cb_size=(7, 7)):
    """ Extended OpenCV checkerboard camera calibration. Returns extended intrinsic
        calibration parameters along with camera matrix and distortion coefficients.

        args:
            cam      : CameraObject()
            filepath : String
            img_ext  : String
            cb_size  : tuble
                           Size of checkerboard

        returns:
            camera matrix           : numpy array 3x3
            distortion coefficients : numpy arrat 1x[4-8]
    """

    mtx, dist = simple_checkerboard_calibration(filepath, img_ext, cb_size)
    file_paths = glob.glob(filepath+'/*.'+img_ext)
    img_size = cv2.imread(file_paths[0], 0).shape
    fov_x, fov_y, c, principle_point, aspect_ratio = cv2.calibrationMatrixValues(mtx,
                                                                                 img_size,
                                                                                 cam.sensor_size[0],
                                                                                 cam.sensor_size[1])

    return mtx, dist, fov_x, fov_y, c, principle_point


def simple_checkerboard_calibration(filepath, img_ext='jpg', cb_size=(7,7)):
    """ Basic OpenCV checkerboard camera calibration. Returns only camera matrix
        and distortion coefficients.

        args:
            filepath : String
            img_ext  : String
            cb_size  : tuble
                           Size of checkerboard

        returns:
            camera matrix           : numpy array 3x3
            distortion coefficients : numpy arrat 1x[4-8]
    """

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    objp = np.zeros((cb_size[0]*cb_size[1],3), np.float32)
    objp[:,:2] = np.mgrid[0:cb_size[0],0:cb_size[1]].T.reshape(-1,2)

    objpoints = []
    imgpoints = []

    file_paths = glob.glob(filepath+'/*.'+img_ext)

    assert len(file_paths) >= 10, 'At least 10 images are required for calibration.'

    print('Performing camera calibration on %d images...'%len(file_paths))

    for file in file_paths:

        img = cv2.imread(file, 0)
        ret, corners = cv2.findChessboardCorners(img, (cb_size[0],cb_size[1]),None)

        if ret == True:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(img,corners,(11,11),(-1,-1),criteria)
            imgpoints.append(corners2)

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, img.shape[::-1],None,None)

    return mtx, dist

if __name__ == '__main__':

    cam = pf.CameraObject()
    cam.sensor_size=[3.6, 4.8]

    extended_checkerboard_calibration(cam, './examples/data/calibration_images', 'JPG')
