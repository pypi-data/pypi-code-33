import requests
import tarfile
import os
import sys
import warnings
from nosypy.image.io import imread
import numpy as np

def downloader(url,localdir):
    r = requests.get(url, allow_redirects=True, stream=True)
    total_length = r.headers.get('content-length')
    output = open(localdir, 'wb')
    if total_length is None: # no content length header
        output.write(r.content)
    else:
        dl = 0
        total_length = int(total_length)
        for data in r.iter_content(total_length/100):
            dl += len(data)
            output.write(data)
            done = int(50 * dl / total_length)
            sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )    
            sys.stdout.flush()


def unpack(fname):
    path    = os.path.dirname(os.path.realpath(fname))
    if (fname.endswith("tar.gz")):
        tar = tarfile.open(fname, "r:gz")
        tar.extractall(path=path)
        tar.close()
    elif (fname.endswith("tar")):
        tar = tarfile.open(fname, "r:")
        tar.extractall(path=path)
        tar.close()


def getpaths(path,prefix='',imgrange=None,ext='JPG'):
    '''
        Returns a list of file paths. If the filenames are 
        asigned sequentially, the imgrange=[start,end] list 
        can be used to select the range of images to be 
        added to the output list of paths. Otherwise, all 
        files in path will be added 

        Parameters 
        ---------- 

        Return
        -------
    '''
    if imgrange==None:
        # list of files in directory
        files = os.listdir(path)
        # remove any within an excepted extention 
        files = [x for x in files if any(y in x for y in ['.png','.jpg','.JPG','.tif'])]
        # add path as prefix 
        filepaths = [os.path.join(path,s) for s in files]
    else:
        files = []
        filepaths = []
        for i in range(imgrange[0],imgrange[1]):
            files.append(os.path.join(prefix+str(i)+'.'+ext))
            filepaths.append(os.path.join(path,prefix+str(i)+'.'+ext))
    return files,filepaths

class Set:

    def __init__(self, traindir,validatedir=None):
        '''

        Parameters
        ----------
        traindir : 

        validatedir : 

        Returns
        -------

        '''
        # locate images in path 
        self.train_files,self.train_paths = getpaths(traindir)
        if not validatedir == None: self.val_paths = validatedir

        # determine height and width from first image
        try:self.height, self.width = np.shape(imread(self.train_paths[0]))
        except:self.height, self.width, _ = np.shape(imread(self.train_paths[0]))


class UCSD:

    def __init__(self,localdir='UCDS_dataset'):
        if not os.path.exists(localdir): os.mkdir(localdir)
        if not os.path.exists(os.path.join(localdir,'UCSD_Anomaly_Dataset.v1p2')):
            if not os.path.exists(os.path.join(localdir,'UCSD_Anomaly_Dataset.tar.gz')):
                print('\nDownloading UCDS dataset')
                url = 'http://www.svcl.ucsd.edu/projects/anomaly/UCSD_Anomaly_Dataset.tar.gz'
                try: # add multiple attempts
                    downloader(url,os.path.join(localdir,'UCSD_Anomaly_Dataset.tar.gz'))
                    print ("complete\n")
                except:
                    raise ValueError('Failed to download dataset - the link may be dead :(')
            # MD5 checksum: 5006421b89885f45a6f93b041145f2eb
            print("unpacking dataset...")
            unpack(os.path.join(localdir,'UCSD_Anomaly_Dataset.tar.gz'))
            print("...done")
        
        if not os.path.exists(os.path.join(localdir,'UCSD_Ped1')):
            if not os.path.exists(os.path.join(localdir,'UCSD_Ped1.tar.gz')):
                print('Downloading UCDS groundtruth data')
                gt_url = 'https://hci.iwr.uni-heidelberg.de/sites/default/files/node/files/1109511602/UCSD_Ped1.tar.gz'
                try:
                    downloader(gt_url,os.path.join(localdir,'UCSD_Ped1.tar.gz'))
                    print ("complete\n")
                except:
                    raise ValueError('Failed to download groundtruth data - the link may be dead :(')  
            
            print("unpacking ground truth...")
            unpack(os.path.join(localdir,'UCSD_Ped1.tar.gz'))
            print("...done")

        # set parameters 
        self.height,self.width = 158,238
        # file list 
        ped1dir     = os.path.join(localdir,'UCSD_Anomaly_Dataset.v1p2','UCSDped1','Train')
        # training sets
        self.train001 = getpaths(os.path.join(ped1dir,'Train001'))
        self.train002 = getpaths(os.path.join(ped1dir,'Train002'))
        self.train003 = getpaths(os.path.join(ped1dir,'Train003'))
        self.train004 = getpaths(os.path.join(ped1dir,'Train004'))
        self.train005 = getpaths(os.path.join(ped1dir,'Train005'))
        self.train006 = getpaths(os.path.join(ped1dir,'Train006'))
        self.train007 = getpaths(os.path.join(ped1dir,'Train007'))
        self.train008 = getpaths(os.path.join(ped1dir,'Train008'))
        self.train009 = getpaths(os.path.join(ped1dir,'Train009'))
        self.train009 = getpaths(os.path.join(ped1dir,'Train010'))
        self.train010 = getpaths(os.path.join(ped1dir,'Train011'))
        self.train011 = getpaths(os.path.join(ped1dir,'Train012'))
        self.train012 = getpaths(os.path.join(ped1dir,'Train013'))
        self.train013 = getpaths(os.path.join(ped1dir,'Train014'))
        self.train014 = getpaths(os.path.join(ped1dir,'Train015'))
        self.train016 = getpaths(os.path.join(ped1dir,'Train016'))
        self.train017 = getpaths(os.path.join(ped1dir,'Train017'))
        self.train018 = getpaths(os.path.join(ped1dir,'Train018'))
        self.train019 = getpaths(os.path.join(ped1dir,'Train019'))
        self.train020 = getpaths(os.path.join(ped1dir,'Train020'))
        self.train021 = getpaths(os.path.join(ped1dir,'Train021'))
        self.train022 = getpaths(os.path.join(ped1dir,'Train022'))
        self.train023 = getpaths(os.path.join(ped1dir,'Train023'))
        self.train024 = getpaths(os.path.join(ped1dir,'Train024'))
        self.train025 = getpaths(os.path.join(ped1dir,'Train025'))
        self.train026 = getpaths(os.path.join(ped1dir,'Train026'))
        self.train027 = getpaths(os.path.join(ped1dir,'Train027'))
        self.train028 = getpaths(os.path.join(ped1dir,'Train028'))
        self.train029 = getpaths(os.path.join(ped1dir,'Train029'))
        self.train030 = getpaths(os.path.join(ped1dir,'Train030'))
        self.train031 = getpaths(os.path.join(ped1dir,'Train031'))
        self.train032 = getpaths(os.path.join(ped1dir,'Train032'))
        self.train033 = getpaths(os.path.join(ped1dir,'Train033'))
        self.train034 = getpaths(os.path.join(ped1dir,'Train034'))