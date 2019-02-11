import numpy as np

def create(height,width,jtiles,itiles, overlaps=False):
    '''
        Split frame into multiple tiles and return the tile coordinates

        Parameters
        ----------
        height : int
            height of frame
        width : int
            width of frame
        jtiles : int
            the number of tiles to split the frame into in the vertical dimension
        itiles : int
            the number of tiles to split the frame into in the horizontal dimension
        overlaps : boolean
            if True: create addition tiles of equal size that are centred at the
            original tile cross boundaries

        Returns
        -------
        array of size (tiles,4) which includes the tiles' starting j index, ending
        j index, i starting index, and i ending index, respectively.
    '''
    tileheight, tilewidth = np.ceil(height/jtiles),np.ceil(width/itiles)
    ntiles          = jtiles*itiles
    if overlaps:
        # number of cross boundaries, number of overlap tiles
        ontiles     = (jtiles-1)*(itiles-1)
        ntiles+=ontiles
    tiles           = np.array(np.zeros((ntiles,4)))
    tile_id         = 0
    for j in range(jtiles): # if last tile expand to edge
        for i in range(itiles):

            tiles[tile_id] = [  int(j*tileheight),
                                int(min((j*tileheight)+tileheight,height)),
                                int(i*tilewidth),
                                int(min((i*tilewidth)+tilewidth,width))] # jstart,jend,istart,iend

            if i==itiles-1: # if last tile expand to edge
                tiles[tile_id][3] = int(width)
            if j==jtiles-1: # if last tile expand to edge
                tiles[tile_id][1] = int(height)


            tile_id+=1

    if overlaps:
        # add overlapping tiles
        for j in range(jtiles-1):
            for i in range(itiles-1):
                jcentre,icentre     =  int(min((j*tileheight)+tileheight,height)),int(min((i*tilewidth)+tilewidth,width))
                tiles[tile_id]      =  [    int(jcentre-(tileheight/2)),
                                            int(jcentre+(tileheight/2)),
                                            int(icentre-(tilewidth/2)),
                                            int(icentre+(tilewidth/2))] # jstart,jend,istart,iend
                tile_id+=1

    return tiles


def extract_patches(img,pheight,pwidth, tile):
    '''
        The centre of even patches is considered the bottom right pixel of the centre
        2x2 block. Overlap for even patches is the largest overlap from this pixel
        (to the left and to the top).

        Parameters
        ----------

        tile : list of size (4)
            contains [starting j index, ending j index, i starting index, and i ending index]

    '''
    try:height,width    = np.shape(img)
    except:height,width,_    = np.shape(img)
    if pheight%2==0:# even
        jolap=int(pheight/2)
        jrange=[int(jolap+tile[0]),int(tile[1]+jolap+1)] # of padded image
    else: # odd
        # jolap=int((pheight-1)/2)
        # jrange = [jolap,height-jolap]
        raise NotImplementedError

    if pwidth%2==0:# even
        iolap = int(pwidth/2)
        irange = [int(iolap+tile[2]),int(tile[3]+iolap+1)]
    else:
        # iolap=int((pwidth-1)/2)
        # irange = [iolap,width-iolap]
        raise NotImplementedError

    # pad image to account for overlapping patches
    padded = np.pad(img, ((jolap,iolap),(jolap,iolap)), 'reflect')[:,:,np.newaxis] # (up,left),(down,right)
    patches = []
    for j in range(jrange[0],jrange[1]):
        for i in range(irange[0],irange[1]):
            patches.append(padded[j-jolap:j+jolap,i-iolap:i+iolap]) # for even pheight and pwidth

    return patches
