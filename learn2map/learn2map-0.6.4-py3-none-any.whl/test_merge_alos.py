import os
import glob
import sys
import subprocess
from osgeo import gdal
import raster_tools as rt


data_path = '/Volumes/MyBookThunderboltDuo/ALOS2_out/agb'
os.chdir(data_path)


in_file = glob.glob('agb_*')
print(in_file)
out_file = 'globe_agb_100m.vrt'

in_file_string = ' '.join('"{}"'.format(i) for i in in_file)
gdal_expression = 'gdalbuildvrt "{}" {}'.format(out_file, in_file_string)
print(gdal_expression)
subprocess.check_output(gdal_expression, shell=True)

ref_file = '/Volumes/LACIE01/yy/globe_biomass/inputdata/globe_lc_map.tif'
new_file = '//Volumes/MyBookThunderboltDuo/ALOS2_out/agb/global_agb_10km_2007.tif'
rt.raster_clip(ref_file, out_file, new_file, resampling_method='average', srcnodata='nan', dstnodata='nan')

in_file = glob.glob('p_*')
print(in_file)
out_file = 'globe_agb_p_100m.vrt'

in_file_string = ' '.join('"{}"'.format(i) for i in in_file)
gdal_expression = 'gdalbuildvrt "{}" {}'.format(out_file, in_file_string)
print(gdal_expression)
subprocess.check_output(gdal_expression, shell=True)

ref_file = '/Volumes/LACIE01/yy/globe_biomass/inputdata/globe_lc_map.tif'
new_file = '//Volumes/MyBookThunderboltDuo/ALOS2_out/agb/global_agb_p_10km_2007.tif'
rt.raster_clip(ref_file, out_file, new_file, resampling_method='average', srcnodata='nan', dstnodata='nan')

# in_file = glob.glob('yeargain_gain_loss*')
# print(in_file)
# out_file = 'globe_forest_gain_30m.vrt'
#
# in_file_string = ' '.join('"{}"'.format(i) for i in in_file)
# gdal_expression = (
#     'gdalbuildvrt "{}" {}').format(
#     out_file, in_file_string)
# print(gdal_expression)
# subprocess.check_output(gdal_expression, shell=True)
#
# ref_file = '/Volumes/LACIE01/yy/globe_biomass/inputdata/globe_lc_map.tif'
# new_file = '/Users/xuliang/Documents/yy/global_data/globe_gfc_10km_gain.tif'
# rt.raster_clip(ref_file, out_file, new_file, resampling_method='average', srcnodata='nan', dstnodata='nan')


# for i in range(16):
#     out_file2 = 'global_hensen_loss_gain_yr{}.tif'.format(i+2000)
#     gdal_expression = (
#         'gdal_calc.py --creation-option="COMPRESS=LZW" -A {} --outfile={} --calc="A=={}"').format(
#         out_file, out_file2, i+1)
#     print(gdal_expression)
#     subprocess.check_output(gdal_expression, shell=True)
#     ref_file = '/Volumes/LACIE01/yy/globe_biomass/inputdata/globe_lc_map.tif'
#     new_file = '/Users/xuliang/Documents/yy/global_data/globe_gfc_10km_yr{}.tif'.format(i+2000)
#     rt.raster_clip(ref_file, out_file2, new_file, resampling_method='average', srcnodata='nan', dstnodata='nan')
#     # subprocess.check_output('rm -f {}'.format(out_file2), shell=True)



