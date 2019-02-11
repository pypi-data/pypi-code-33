'''
    Run NATI on the UCSD Anomaly Detection Dataset
'''
try:
    import nosypy as nosy
except:
    from context import nosypy as nosy

import os
'''
    Create directories for data
'''
data    = 'ucsd_data'
output  = 'nosypy_output' 
if not os.path.exists(data):os.mkdir(data)
if not os.path.exists(output):os.mkdir(output)
    
'''
    Download dataset
'''
ds      = nosy.data.UCSD(localdir=data) 

'''
    The UCSD dataset has 34 Training sets in ped1 and the file paths are given in 
    UCDS.train001 to UCDS.train034  

    Train NATI
'''
pheight, pwidth = 28,28
jtiles, itiles  = 5,7

nosy.run.train_models(ds.train001,output,ds.height,ds.width,pheight, pwidth, jtiles, itiles,epoch=1)

