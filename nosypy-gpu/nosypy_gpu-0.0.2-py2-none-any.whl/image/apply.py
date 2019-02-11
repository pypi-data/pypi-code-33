import os
import nosypy as nosy

def mask(img,t):

    # apply threshold
    highidx         = img>=t
    lowidx          = img<t
    img[highidx]   = 255
    img[lowidx]    = 0

    return img

def maskall(inpath,outpath,t):
    '''
        Generate a mask by applying a threshold
    '''

    if not os.path.exists(outpath): os.mkdir(outpath)
    '''
        Get list of files in directory 
    '''
    filelist = os.listdir(inpath)

    for f in filelist:
        # load image 
        orig        = nosy.image.io.imread(os.path.join(inpath,f))  
        # Apply threshold 
        maskimg     = mask(orig,t)
        # save image
        nosy.image.io.save_image(maskimg,os.path.join(outpath,f))