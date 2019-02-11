import os
import nosypy as nosy
import numpy as np
from skimage import measure

def percentile(inpath,percentile=0.99):
    '''
        Calculate the n percetile
    '''

    
    #Get list of files in directory 
    filelist = os.listdir(inpath)

    # Create array to store frequency of pixel intensities
    hist_arr = np.array(np.zeros(256))
    for f in filelist:
        # load image 
        img        = nosy.image.io.imread(os.path.join(inpath,f))

        img_arr = img.ravel() # is this needed?
        unique, counts  = np.unique(img_arr, return_counts=True)
        for t in range(len(unique)):
            hist_arr[unique[t]] += counts[t]

    total       = float(np.sum(hist_arr))
    cuml        = 0.0
    for i in range(255,0,-1):
        cuml = np.sum(hist_arr[:i])/total
        if cuml <=percentile:
            treshold=i
            break

    return treshold


def meanpercentile(inpath,percentile=0.99):
    '''
        Calculate mean percentile
    '''
    #Get list of files in directory 
    filelist    = os.listdir(inpath)
    nfiles      = len(filelist)
    sumthreshold = 0
    for f in filelist:
        # Create array to store frequency of pixel intensities
        hist_arr = np.array(np.zeros(256))
        # load image 
        img        = nosy.image.io.imread(os.path.join(inpath,f))

        img_arr = img.ravel() # is this needed?
        unique, counts  = np.unique(img_arr, return_counts=True)
        for t in range(len(unique)):
            hist_arr[unique[t]] += counts[t]
        total       = float(np.sum(hist_arr))
        for i in range(255,0,-1):
            cuml = np.sum(hist_arr[:i])/total
            if cuml <=percentile:
                sumthreshold+=i
                break

    return int(np.floor(sumthreshold/float(nfiles)))


def contours(mask):
    '''
        find contours in image mask 
    '''
    return measure.find_contours(mask, 0)

def contour2bbox(contour):
    '''
        Calculate a bounding box from a contour

        Parameters
        ----------
        contour : array_like 
            a single contour

        Returns
        -------
        x and y points of each corner of the bounding box in image
        ymin,ymax,xmin,xmax
    '''
    xmin,xmax       = min(contour[:, 1]), max(contour[:, 1])
    ymin,ymax       = min(contour[:, 0]), max(contour[:, 0])

    return ymin,ymax,xmin,xmax