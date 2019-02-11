import numpy as np

def rgb2luma(arr):
	'''
        convert RGB image to greyscale

        Parameters 
        ----------
        arr : numpy array 
            numpy array containing two spatial dimensions and 3 colour channels

        Returns 
        --------
        arr : numpy array
            2D numpy array containing the luminance conversion of the input 3D 
            colour array
    ''' 
	return np.dot(arr[...,:3], [0.299, 0.587, 0.144])