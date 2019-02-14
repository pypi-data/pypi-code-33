import os
import glob
import time
import subprocess
import learn2map.raster_tools as rt


data_path = '/Users/xuliang/Documents/yy/global_data/LC/output'
# data_path = 'G:\\yy\\globe_biomass\\inputdata\\lst_noqa'
os.chdir(data_path)
input_mask = '/Volumes/LACIE01/yy/globe_biomass/inputdata/globe_lc_map.tif'

# Raster to Raster (creating all tif files into geotiff with the same dimension and projection as the reference)
for i in range (17):
    year=2001+i
    in_file = glob.glob('globe_lc_500m_{}.tif'.format(year))
    print(in_file)
    out_file = 'globe_lc_fnf{}.tif'.format(year)

    expression0 = '(A>0) * (A<6) + (A==8)'
    gdal_expression = (
        'gdal_calc.py --creation-option COMPRESS=DEFLATE --creation-option ZLEVEL=9 --creation-option PREDICTOR=2 '
         ' --creation-option BIGTIFF=YES --overwrite --NoDataValue=0 --type=Byte -A "{}" --outfile="{}" --calc="{}"'
         ).format(in_file[0], out_file, expression0)
    print(gdal_expression)
    subprocess.check_output(gdal_expression, shell=True)
    time.sleep(1.5)
    output_x = '{}_10km.tif'.format(os.path.splitext(out_file)[0])
    rt.raster_clip(input_mask, out_file, output_x, resampling_method='average')