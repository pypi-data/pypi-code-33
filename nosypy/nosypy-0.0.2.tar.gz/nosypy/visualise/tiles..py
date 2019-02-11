import numpy as np 


def regions(img,tiles,colour=[255,0,0],linewidth=3):
    '''
        Visualise the tile regions as produced by data.split_frame()


        Parameters
        ----------
        img : numpy array
            image

        tiles : array
            numpy array of size (tiles,4), [[tile index],jstart,jend,istart,iend]]

        Returns
        -------
    '''

    try:
        height,width,_ = np.shape(img)
    except:
        height,width = np.shape(img)
        print ("viz: ", height,width)
        img2 = np.array(np.zeros((height,width,3)))
        img2[:,:,0] = img
        img2[:,:,1] = img
        img2[:,:,2] = img
        img         = img2
    if np.shape(colour) == (len(tiles),3):
        for t in range(np.shape(tiles)[0]):
            # Draw tile t
            # vertical left line
            img[int(tiles[t][0]):int(tiles[t][1]),int(max(tiles[t][2]-(linewidth/2),0)):int(min(tiles[t][2]+(linewidth/2),width))]           = colour[t]
            # vertical right line
            img[int(tiles[t][0]):int(tiles[t][1]),int(max(tiles[t][3]-(linewidth/2),0)):int(min(tiles[t][3]+(linewidth/2),width))]           = colour[t]
            # horizontal top line
            img[int(max(tiles[t][0]-(linewidth/2),0)):int(min(tiles[t][0]+(linewidth/2),height)),int(tiles[t][2]):int(tiles[t][3])]          = colour[t]
            # horizontal bottom line
            img[int(max(tiles[t][1]-(linewidth/2),0)):int(min(tiles[t][1]+(linewidth/2),height)),int(tiles[t][2]):int(tiles[t][3])]          = colour[t]

    else:
        colour=[255,0,0]
        for t in range(np.shape(tiles)[0]):
            # Draw tile t
            # vertical left line
            img[int(tiles[t][0]):int(tiles[t][1]),int(max(tiles[t][2]-(linewidth/2),0)):int(min(tiles[t][2]+(linewidth/2),width))]           = colour
            # vertical right line
            img[int(tiles[t][0]):int(tiles[t][1]),int(max(tiles[t][3]-(linewidth/2),0)):int(min(tiles[t][3]+(linewidth/2),width))]           = colour
            # horizontal top line
            img[int(max(tiles[t][0]-(linewidth/2),0)):int(min(tiles[t][0]+(linewidth/2),height)),int(tiles[t][2]):int(tiles[t][3])]          = colour
            # horizontal bottom line
            img[int(max(tiles[t][1]-(linewidth/2),0)):int(min(tiles[t][1]+(linewidth/2),height)),int(tiles[t][2]):int(tiles[t][3])]          = colour
    return img
