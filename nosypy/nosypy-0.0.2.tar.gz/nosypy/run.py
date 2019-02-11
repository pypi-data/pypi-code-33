import nosypy as nosy
import numpy as np
import time
import os


def detect(filepaths,outpath,height,width,pheight, pwidth, jtiles, itiles):
    '''


    '''
    
    '''
        Define tiles
    '''
    tiles = nosy.image.tile.create(height,width,jtiles,itiles, overlaps=False)
    ntiles  = len(tiles)
    print(ntiles, " tiles")


    '''
        Build model
    '''
    aen     = nosy.autoencoder.ConvNet()
    aen.model(pheight,pwidth)
    aen.model_summary()

    '''
        Output directories
    '''
    noveltymaps             = os.path.join(outpath, 'novelty')
    novmap_npy_path         = os.path.join(outpath, 'novelty', 'numpy_error')
    novmap_setscale_path    = os.path.join(outpath, 'novelty', 'set_norm')
    if not os.path.exists(noveltymaps): os.mkdir(noveltymaps)
    if not os.path.exists(novmap_npy_path): os.mkdir(novmap_npy_path)
    if not os.path.exists(novmap_setscale_path): os.mkdir(novmap_setscale_path)

    setmax = 0.0    # maximum sse of set
    for imgidx in range(len(filepaths)):
        '''
            Extract filename from path 
        '''
        filename = os.path.basename(filepaths[imgidx])
        print ("Image: ", filename)
        # load image
        img = np.divide(nosy.image.io.imread(filepaths[imgidx]).astype('float'),255.0)

        '''
        # Initialise Novety map for image
        '''
        Nmap = np.array(np.zeros((height,width)))
        Nweights = np.array(np.zeros((height,width)))

        for tile_id in range(ntiles):
            tile            = tiles[tile_id]

            '''
                X patch array
                need to create in loop because tile dimensions can change near borders
            '''
            nframepatches   = int((tile[1]-tile[0]+1) * (tile[3]-tile[2]+1))
            # print (nframepatches, ' patches in tile ', str(tile_id))

            # Load Tile Model
            aen.load_model(path=os.path.join(outpath,'models','aen_tile' + str(tile_id) + '_model.h5'))

            # Calculate difference between X and X' and create novety map
            Nmap,Nweights = nosy.novelty.patch.error(img,pheight,pwidth,tile,aen,nframepatches,Nmap=Nmap, Nweights=Nweights)


        # Normalise Novelty map and save
        Nmap        = np.divide(Nmap,Nweights)
        imgmax = np.max(Nmap) # for tracking maximum value in set
        if imgmax > setmax:
            setmax = imgmax
        # andect.ip.save_image(Nmap,os.path.join(novmap_path, fileprefix+str(img_range[0] + img_id)+'.png'))
        np.save(os.path.join(novmap_npy_path, filename +'.npy'),Nmap)

    '''
        Normalise/scale images according to max sse of entire set
    '''
    for imgidx in range(len(filepaths)):
        '''
            Extract filename from path 
        '''
        filename = os.path.basename(filepaths[imgidx])

        img = np.load(os.path.join(novmap_npy_path, filename +'.npy'))
        nosy.image.io.save_image(np.multiply(img,255.0/setmax),os.path.join(novmap_setscale_path, filename +'.png'))

    '''
        Remove temporary numpy files 
    '''
    

def train_models(filepaths,outpath,height,width,pheight, pwidth, jtiles, itiles,epoch=20):
    '''

    Parameters
    ----------
    pheight :

    pwidth : 

    jtiles :

    itiles :


    Returns
    -------

    '''
    def train(aen,tiles,tilelist,model_dir,filepaths,pheight,pwidth,epoch=20):

        for tile_id in tilelist:
            start_time = time.time()
            outputmodel = os.path.join(model_dir,'aen_tile' + str(tile_id) + '_model.h5')
            if os.path.exists(outputmodel): continue

            '''
                Callbacks
            '''
            checkpoint_path = os.path.join(model_dir,'tile' + str(tile_id) + '_training')
            if not os.path.exists(checkpoint_path): os.mkdir(checkpoint_path)
            tensorboard_path = os.path.join(model_dir,'tile' + str(tile_id) + '_tensorboard/covnet_autoencoder')
            aen.reinitialise()
            aen.tensorboard(log=tensorboard_path)
            aen.checkpoints(path=checkpoint_path,N=10)

            aen.model(pheight,pwidth)
            aen.model_summary()

            '''
                Extract patches in tile and add to list
            '''
            tile            = tiles[tile_id]
            print("tile: ", tile_id)
            for i in range(len(filepaths)):
                # load image and convert to range [0,1]
                img = np.divide(nosy.image.io.imread(filepaths[i]).astype('float'),255.0)
                X[i*nframepatches:(i+1)*nframepatches,...] = nosy.image.tile.extract_patches(img,pheight,pwidth,tile)


            aen.train(X,epoch=epoch)
            aen.save_model(path=outputmodel)
            elapsed_time = time.time() - start_time
            print ("Time elapsed: ", elapsed_time, " seconds")
            print ("Time elapsed: ", elapsed_time/60.0, " minutes")


    # create working directory
    if not os.path.exists(outpath): os.mkdir(outpath)

    model_dir               = os.path.join(outpath,'models')
    if not os.path.exists(model_dir): os.mkdir(model_dir)

    # define tiles
    tiles = nosy.image.tile.create(height,width,jtiles,itiles, overlaps=False)
    ntiles  = len(tiles)
    print(ntiles, " tiles")
    # Create Model Class
    aen     = nosy.autoencoder.ConvNet()
    nimages         = len(filepaths)
    
    #### Train tiles not on the right or bottom border ###
    nframepatches   = int((tiles[0][1]-tiles[0][0]+1) * (tiles[0][3]-tiles[0][2]+1))
    npatches        = nframepatches*nimages
    print (npatches, ' patches')

    # array for storiing patches
    X = np.array(np.zeros((npatches, pheight, pwidth, 1)))

    tilelist = []
    for i in range(jtiles-1):
        tilelist.extend(np.arange((i*itiles),(((i+1)*itiles)-1)))
    train(aen,tiles,tilelist,model_dir,filepaths,pheight,pwidth,epoch=epoch)

    #### Train tiles on the right border ###
    nframepatches   = int((tiles[itiles][1]-tiles[itiles][0]+1) * (tiles[itiles][3]-tiles[itiles][2]+1))
    npatches        = nframepatches*nimages

    # array for storiing patches
    X = np.array(np.zeros((npatches, pheight, pwidth, 1)))

    tilelist = []
    for i in range(jtiles-1):
        tilelist.append(i*itiles)
    # train(aen,tiles,tilelist,model_dir,filepaths,pheight,pwidth,epoch=epoch)

    #### Train tiles on the bottom right tile ###
    nframepatches   = int((tiles[(itiles*jtiles)-1][1]-tiles[(itiles*jtiles)-1][0]+1) * (tiles[(itiles*jtiles)-1][3]-tiles[(itiles*jtiles)-1][2]+1))
    npatches        = nframepatches*nimages

    # array for storiing patches
    X = np.array(np.zeros((npatches, pheight, pwidth, 1)))

    tilelist = []
    for i in range(jtiles-1):
        tilelist.append(i*itiles)
    # train(aen,tiles,tilelist,model_dir,filepaths,pheight,pwidth,epoch=epoch)




# if __name__=='__main__':
#     detection(filepaths,outpath,height,width,pheight, pwidth, jtiles, itiles)