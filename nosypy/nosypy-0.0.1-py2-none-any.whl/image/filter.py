import numpy as np
import os 
import nosypy as nosy
from scipy import ndimage

def lincoeff(filterwidth=31):
    '''
        Generate a 1D array of linear filter coefficients
        filterwidth should be odd, otherwise filterwidth-1 will be taken

        Parameters
        ----------

    '''
    olap = int((filterwidth+1)/2)
    return np.lib.pad(np.linspace(1,3,olap), (0,olap-1),'reflect')

def linear2D(img,filterwidth=31):
    '''
        Apply a 2D linear filter to image 

        Parameters
        ----------
        img : array_like
    '''
    kernel = kernel2D(lincoeff(filterwidth=filterwidth))
    return ndimage.convolve(img,kernel)


def linear2Dall(inpath,outpath,filterwidth=31):
    '''
        Use a 2D linear filter on each image in inpath
    '''
    kernel = kernel2D(lincoeff(filterwidth=filterwidth))
    if not os.path.exists(outpath): os.mkdir(outpath)
    
    '''
        Get list of files in directory 
    '''
    filelist = os.listdir(inpath)

    for f in filelist:
        # load image 
        orig        = nosy.image.io.imread(os.path.join(inpath,f))
        # resize image 
        filtered    = ndimage.convolve(orig,kernel)
        # save image 
        nosy.image.io.save_image(filtered,os.path.join(outpath,f))


def kernel2D(coeffs):
    '''
        Create a 2D normalised kernel from a 1D array

        Parameters
        ----------
        coeffs : numpy array
            1D numpy array of filter coefficients 

    '''
    size = len(coeffs)
    Unit = np.array(np.ones((size,size)),dtype=float)
    filtx = [coeffs]
    Kx = np.multiply(filtx,Unit)
    filty = [coeffs]
    Ky = np.multiply(Unit,np.transpose(filty))
    Kernel = np.multiply(Kx,Ky)
    Normalise = np.sum(Kernel)
    return np.divide(Kernel,Normalise)