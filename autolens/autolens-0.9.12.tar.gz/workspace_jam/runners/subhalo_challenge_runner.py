from autofit import conf
import os
path = '{}/../'.format(os.path.dirname(os.path.realpath(__file__)))
conf.instance = conf.Config(config_path=path+'config', output_path=path+'output')

from autolens.data import ccd
from autolens.data.array import mask as msk
from autolens.data.plotters import ccd_plotters

import os

path = '{}/../'.format(os.path.dirname(os.path.realpath(__file__)))
conf.instance = conf.Config(config_path=path+'config', output_path=path+'output')

level = 'level_0'
lens_name = 'small_halo'

pixel_scale = 0.00976562

data_path = path + '/data/subhalo_challenge/' + level + '/' + lens_name

ccd_data = ccd.load_ccd_data_from_fits(image_path=data_path + '/image.fits',
                                       psf_path=data_path + '/psf.fits',
                                       noise_map_path=data_path + '/noise_map.fits', pixel_scale=pixel_scale)

mask = msk.Mask.circular(shape=ccd_data.shape, pixel_scale=ccd_data.pixel_scale, radius_arcsec=3.2)
ccd_plotters.plot_ccd_subplot(ccd_data=ccd_data, mask=mask)

from workspace_jam.pipelines import pipeline_subhalo_no_lens_light
pipeline = pipeline_subhalo_no_lens_light.make_pipeline(pipeline_path='/subhalo_challenge/'+level+'/'+lens_name+'/')
pipeline.run(data=ccd_data)