import os
import glob
import time
import subprocess
import learn2map.raster_tools as rt


data_path = '/Volumes/MyBookThunderboltDuo/ALOS2_out'
# data_path = 'G:\\yy\\globe_biomass\\inputdata\\lst_noqa'
os.chdir(data_path)
input_mask = '/Users/xuliang/Documents/yy/global_data/inputdata/reference.tif'

# Raster to Raster (creating all tif files into geotiff with the same dimension and projection as the reference)
in_file = '/Volumes/MyBookThunderboltDuo/ALOS2_out/alos_2007_global_3sec_hv_cut_landsatfill.int'
out_file = '/Volumes/MyBookThunderboltDuo/ALOS2_out/globe_hv_100m.tif'

expression0 = '3709800*(A/10000)**2.8199'
gdal_expression = (
    'gdal_calc.py --creation-option COMPRESS=DEFLATE --creation-option ZLEVEL=9 --creation-option PREDICTOR=2 '
     ' --creation-option BIGTIFF=YES --overwrite --NoDataValue=0 --type=Byte -A "{}" --outfile="{}" --calc="{}"'
).format(in_file, out_file, expression0)
print(gdal_expression)
subprocess.check_output(gdal_expression, shell=True)
time.sleep(1.5)

output_x = '{}_10km.tif'.format(os.path.splitext(out_file)[0])
rt.raster_clip(input_mask, out_file, output_x, resampling_method='average')

out_file2= '/Volumes/MyBookThunderboltDuo/ALOS2_out/globe_p_agbgt100.tif'
expression1 = 'A>100'
gdal_expression = (
    'gdal_calc.py --creation-option COMPRESS=DEFLATE --creation-option ZLEVEL=9 --creation-option PREDICTOR=2 '
     ' --creation-option BIGTIFF=YES --overwrite --NoDataValue=0 --type=Byte -A "{}" --outfile="{}" --calc="{}"'
).format(out_file, out_file2, expression1)
print(gdal_expression)
subprocess.check_output(gdal_expression, shell=True)
time.sleep(1.5)

output_x = '{}_10km.tif'.format(os.path.splitext(out_file2)[0])
rt.raster_clip(input_mask, out_file2, output_x, resampling_method='average')
# gdal_calc.py -A in_file --outfile=out_file --calc= "3709800*(A/10000)^2.8199" --NoDataValue=0
# gdal_calc.py -A out_file --outfile=outfile --calc= "3709800*(A/10000)^2.8199" --NoDataValue=0