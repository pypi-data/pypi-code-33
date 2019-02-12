import os
import glob
import time
import subprocess
import learn2map.raster_tools as rt


data_path = '/Volumes/MyBookThunderboltDuo/ALOS2_out/alos_10km'
# data_path = 'G:\\yy\\globe_biomass\\inputdata\\lst_noqa'
os.chdir(data_path)
input_mask = '/Users/xuliang/Documents/yy/global_biomass/inputdata/globe_lc_map.tif'
#
# # Raster to Raster (creating all tif files into geotiff with the same dimension and projection as the reference)
# for i in range (17):
#     year=2017+i
#     # in_file = '/Volumes/LACIE01/yy/globe_biomass/output/basemap_rgb.tif'
#     # out_file='basemap_usa.tif'
#     in_file='globe_mcd64_500m_rvdeforet_{}.tif'.format(year)
#     print(in_file)
#     out_file = 'globe_mcd64_10km_rvdeforet_{}.tif'.format(year)
#
#     # expression0 = '(A>0) * (A<6) + (A==8)'
#     # gdal_expression = (
#     #     'gdal_calc.py --creation-option COMPRESS=DEFLATE --creation-option ZLEVEL=9 --creation-option PREDICTOR=2 '
#     #      ' --creation-option BIGTIFF=YES --overwrite --NoDataValue=0 --type=Byte -A "{}" --outfile="{}" --calc="{}"'
#     #      ).format(in_file[0], out_file, expression0)
#     # print(gdal_expression)
#     # subprocess.check_output(gdal_expression, shell=True)
#     # time.sleep(1.5)
#     # output_x = '{}_10km.tif'.format(os.path.splitext(out_file)[0])
#     rt.raster_clip(input_mask, in_file, out_file, resampling_method='average')

# input_mask = '/Volumes/MyBookThunderboltDuo/globbiomass_output/output/Kalimantan_agb_10km.tif'
# infile='/Users/xuliang/Documents/yy/global_biomass/inputdata/globe_agb_2014.tif'
# outfile='/Volumes/LACIE01/yy/globe_biomass/output/kalimantan_agb.tif'
# rt.raster_clip(input_mask, infile, outfile, resampling_method='average')
#
# input_mask = '/Volumes/MyBookThunderboltDuo/globbiomass_output/output/GABON_10km.tif'
# infile='/Users/xuliang/Documents/yy/global_biomass/inputdata/globe_agb_2014.tif'
# outfile='/Volumes/LACIE01/yy/globe_biomass/output/gabon_agb.tif'
# rt.raster_clip(input_mask, infile, outfile, resampling_method='average')
#
# input_mask = '/Volumes/MyBookThunderboltDuo/globbiomass_output/output/DRC_10km.tif'
# infile='/Users/xuliang/Documents/yy/global_biomass/inputdata/globe_agb_2014.tif'
# outfile='/Volumes/LACIE01/yy/globe_biomass/output/drc_agb.tif'
# rt.raster_clip(input_mask, infile, outfile, resampling_method='average')

for i in range (4):
    year=2007+i
    # in_file = '/Volumes/LACIE01/yy/globe_biomass/output/basemap_rgb.tif'
    # out_file='basemap_usa.tif'
    in_file='alos_agb_{}.tif'.format(year)
    print(in_file)
    out_file = 'alos2a_agb_10kmcut{}.tif'.format(year)
    rt.raster_clip(input_mask, in_file, out_file, resampling_method='average')
