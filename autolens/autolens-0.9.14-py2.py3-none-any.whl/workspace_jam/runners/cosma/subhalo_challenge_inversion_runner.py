from autofit import conf
import os
import sys

from autolens.data import ccd
from autolens.data.array import mask as msk
from autolens.data.plotters import ccd_plotters

import os

# Given your username is where your data is stored, you'll need to put your cosma username here.
cosma_username = 'pdtw24'
cosma_data_path = '/cosma5/data/autolens/'

path = '{}/../'.format(os.path.dirname(os.path.realpath(__file__)))

# Use this path to explicitly set the config path, and override the output path with the Cosma path.
conf.instance = conf.Config(config_path=path+'config', output_path=cosma_data_path+'output_'+cosma_username)

# The fifth line of this batch script - '#SBATCH --array=1-17' is what species this. Its telling Cosma we're going to
# run 17 jobs, and the id's of those jobs will be numbered from 1 to 17. Infact, these ids are passed to this runner,
# and we'll use them to ensure that each jobs loads a different image. Lets get the cosma array id for our job.
cosma_array_id = int(sys.argv[1])

### Subhalo challenge data strings ###

data_name = 'subhalo_challenge'
level = 'level_0'
pixel_scale = 0.00976562

lens_name = []
lens_name.append('') # Task number beings at 1, so keep index 0 blank
lens_name.append('large_r_ein') # Index 1
lens_name.append('small_r_ein') # Index 2

data_path = cosma_data_path + 'data/' + cosma_username + '/' + data_name + '/' + level + '/' + lens_name[cosma_array_id]

ccd_data = ccd.load_ccd_data_from_fits(image_path=data_path + '/image.fits',
                                       psf_path=data_path + '/psf.fits',
                                       noise_map_path=data_path + '/noise_map.fits', pixel_scale=pixel_scale)

mask = msk.load_mask_from_fits(mask_path=data_path + '/mask.fits', pixel_scale=pixel_scale)

# mask = msk.Mask.circular(shape=ccd_data.shape, pixel_scale=ccd_data.pixel_scale, radius_arcsec=3.2)
# ccd_plotters.plot_ccd_subplot(ccd_data=ccd_data, mask=mask)

from workspace_jam.pipelines import pipeline_subhalo_inversion_no_lens_light

pipeline = \
    pipeline_subhalo_inversion_no_lens_light.make_pipeline(
        pipeline_path=data_name + '/' + level + '/'+ lens_name[cosma_array_id]+'/')

pipeline.run(data=ccd_data, mask=mask)