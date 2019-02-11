import numpy as np

def error(img,pheight,pwidth,tile,model,nframepatches,Nmap=None, Nweights=None, MODE=1):
    '''
        Adds to a novety map and normalisation map (Nweights).

        Compare x with x' and
        MODE 1:
            add difference to the centre 2x2 block of the patch.
            Each addition in Nmap accumlates in the Nweights array, so that values
            can be normalised after.

        MODE 2:
            pixel difference

        The centre of even patches is considered the bottom right pixel of the centre
        2x2 block. Overlap for even patches is the largest overlap from this pixel
        (to the left and to the top).

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

    X = np.array(np.zeros((nframepatches,pheight,pwidth,1)))
    pidx = 0
    for j in range(jrange[0],jrange[1]):
        for i in range(irange[0],irange[1]):
            X[pidx,...] = padded[j-jolap:j+jolap,i-iolap:i+iolap] # for even pheight and pwidth
            pidx+=1

    # Run on all patches
    decoded = model.decode(X) # performing this on all samples is faster
    idx=0

    if MODE == 1: # Store error for entire patch in centre 2x2 block
        for j in range(jrange[0],jrange[1]):
            for i in range(irange[0],irange[1]):
                error = np.sum(np.power(np.subtract(X[idx,...],decoded[idx,...]),2))
                # add to centre 2x2
                Nmap[           max(j-jolap-1,0):min(j-jolap+1,height),
                                max(i-iolap-1,0):min(i-iolap+1,width)] =  np.add(Nmap[max(j-jolap-1,0):min(j-jolap+1,height),
                                                                                max(i-iolap-1,0):min(i-iolap+1,width)],error) # not padded

                Nweights[       max(j-jolap-1,0):min(j-jolap+1,height),
                                max(i-iolap-1,0):min(i-iolap+1,width)] =  np.add(Nweights[max(j-jolap-1,0):min(j-jolap+1,height),
                                                                                max(i-iolap-1,0):min(i-iolap+1,width)],1.0) # not padded
                idx+=1

    elif MODE == 2: # store pixel-wise error in corresponding pixel
        for j in range(jrange[0],jrange[1]):
            for i in range(irange[0],irange[1]):
                # print(j,i)
                error = np.power(np.subtract(   X[idx,  max(0,pheight-j-1):   min(pheight,height-j+pheight-1),
                                                        max(0,pwidth-i-1):    min(pwidth,width-i+pwidth-1)],
                                                decoded[idx,max(0,pheight-j-1):   min(pheight,height-j+pheight-1),
                                                            max(0,pwidth-i-1):    min(pwidth,width-i+pwidth-1)]),2)[:,:,0]
                # print(np.shape(error))
                # print(np.shape(Nmap[  max(j-(2*jolap)+1,0):min(j+1,height),
                                                                    # max(i-(2*iolap)+1,0):min(i+1,width)]),i+1,width)
                Nmap[           max(j-(2*jolap)+1,0):min(j+1,height),
                                max(i-(2*iolap)+1,0):min(i+1,width)] =  np.add(Nmap[    max(j-(2*jolap)+1,0):min(j+1,height),
                                                                                        max(i-(2*iolap)+1,0):min(i+1,width)],error) # not padded

                Nweights[       max(j-(2*jolap)+1,0):min(j+1,height),
                                max(i-(2*iolap)+1,0):min(i+1,width)] =  np.add(Nweights[  max(j-(2*jolap)+1,0):min(j+1,height),
                                                                                            max(i-(2*iolap)+1,0):min(i+1,width)],1.0) # not padded
                idx+=1
    else:
        raise ValueError("Invalid mode in data.novelty_map()")

    return Nmap,Nweights