
import numpy as np
from gputools.denoise import nlm3



if __name__ == '__main__':
    from time import time
    
    d = 10*np.linspace(0,1,128*129*130).reshape((128,129,130))

    d += np.random.normal(0,1,d.shape)

    t = time()
    res = nlm3(d,100,2,7)
    t = time() -t 

    print("took %.2f ms"%(1000.*t))

