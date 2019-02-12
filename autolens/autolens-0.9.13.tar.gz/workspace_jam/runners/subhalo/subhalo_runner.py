from autofit import conf
import os
path = '{}/../../'.format(os.path.dirname(os.path.realpath(__file__)))
conf.instance = conf.Config(config_path=path+'config', output_path=path+'output')

from autolens.data import ccd
from autolens.data.array import mask as msk
from autolens.data.plotters import ccd_plotters

import os

path = '{}/../'.format(os.path.dirname(os.path.realpath(__file__)))
conf.instance = conf.Config(config_path=path+'config', output_path=path+'output')

lens_name = 'lens_with_00_subhalo_smooth_source'

ccd_data = ccd.load_ccd_data_from_fits(image_path=path + '/data/subhalo/' + lens_name + '/image.fits',
                                       psf_path=path+'/data/subhalo/'+lens_name+'/psf.fits',
                                       noise_map_path=path+'/data/subhalo/'+lens_name+'/noise_map.fits',
                                       pixel_scale=0.05)

mask = msk.Mask.circular(shape=ccd_data.shape, pixel_scale=ccd_data.pixel_scale, radius_arcsec=3.0)
ccd_plotters.plot_ccd_subplot(ccd_data=ccd_data, mask=mask)

from workspace_jam.pipelines import pipeline_subhalo_no_lens_light
pipeline = pipeline_subhalo_no_lens_light.make_pipeline(pipeline_path='/subhalo/' + lens_name + '/')
pipeline.run(data=ccd_data)

# from workspace_jam.pipelines import subhalo_redshift_intervals
# pipeline = subhalo_redshift_intervals.make_pipeline(pipeline_path='/subhalo/' + lens_name + '/')
# pipeline.run(data=ccd_data)

# from workspace_jam.pipelines import pipeline_subhalo_redshift_intervals
# pipeline = pipeline_subhalo_redshift_intervals.make_pipeline(pipeline_path='/subhalo/' + lens_name + '/')
# pipeline.run(data=ccd_data)