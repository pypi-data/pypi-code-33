import os
from pyroSAR import identify
from pyroSAR.auxdata import dem_autoload
from spatialist import Raster

filename = '/home/truc_jh/Desktop/S1_ARD/S1A_IW_GRDH_1SDV_20180829T170656_20180829T170721_023464_028DE0_F7BD.zip'

maindir = '/home/truc_jh/Desktop/DEM_test'

if not os.path.isdir(maindir):
    os.makedirs(maindir)

id = identify(filename)

shp = os.path.join(maindir, 'coverage.shp')
if not os.path.isfile(shp):
    id.bbox(shp)

for demType in ['AW3D30', 'SRTM 1Sec HGT', 'SRTM 3Sec', 'TDX90m']:

    outname = os.path.join(maindir, '{}.tif'.format(demType.replace(' ', '-')))
    
    if not os.path.isfile(outname):
    
        vrt = dem_autoload([id.bbox()], demType=demType, vrt='/vsimem/test.vrt', buffer=0.01,
                           username='john.truckenbrodt@uni-jena.de', password='Rbv823rv%&')
        
        with Raster(vrt) as ras:
            ras.write(outname, format='GTiff')
