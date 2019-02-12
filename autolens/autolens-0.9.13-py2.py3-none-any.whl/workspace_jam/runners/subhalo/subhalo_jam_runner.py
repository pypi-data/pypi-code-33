from autofit import conf
import os

from autolens.data import ccd
from autolens.data.array import mask as msk
from autolens.data.plotters import ccd_plotters

import os

path = '{}/../../'.format(os.path.dirname(os.path.realpath(__file__)))
conf.instance = conf.Config(config_path=path+'config', output_path=path+'output')

data_name = 'subhalo_jam'
level = ''
lens_name = 'lens_with_05_subhalo_cuspy_source'
pixel_scale = 0.05

data_path = path + '/data/' + data_name + '/' + level + '/' + lens_name

ccd_data = ccd.load_ccd_data_from_fits(image_path=data_path + '/image.fits',
                                       psf_path=data_path + '/psf.fits',
                                       noise_map_path=data_path + '/noise_map.fits', pixel_scale=pixel_scale)

from workspace_jam.pipelines import pipeline_subhalo_inversion_no_lens_light

pipeline = \
    pipeline_subhalo_inversion_no_lens_light.make_pipeline(pipeline_path=data_name + '/' + level+ '/'+ lens_name+'/')

pipeline.run(data=ccd_data)