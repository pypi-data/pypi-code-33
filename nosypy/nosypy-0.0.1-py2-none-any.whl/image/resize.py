from scipy import ndimage
import nosypy as nosy 
import os 

def bicubic(arr,scale):
    '''
        User scipy library to resize image array 
        using bicubic interpolation

        Parameters 
        ----------
        arr : numpy array 
            2D array or 3D (RGB) image array
        scale : int or float 
            scale factor. <1 decreases spatial resolution, >1
            increases spatial resolution

        Returns 
        -------
        resized array
    '''
    return ndimage.zoom(arr.astype(float), scale, order=3)


def allbicubic(inpath,outpath,scale):
    '''
        Scale all images in path 
        Move this to another module
    '''
    if not os.path.exists(outpath): os.mkdir(outpath)
    
    '''
        Get list of files in directory 
    '''
    filelist = os.listdir(inpath)

    for f in filelist:
        # load image 
        orig        = nosy.image.io.imread(os.path.join(inpath,f))
        # resize image 
        scaled      = nosy.image.resize.bicubic(orig, scale)
        # save image 
        nosy.image.io.save_image(scaled,os.path.join(outpath,f))