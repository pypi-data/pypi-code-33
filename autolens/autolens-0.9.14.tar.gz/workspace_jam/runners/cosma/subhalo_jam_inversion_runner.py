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

### In-house simulation data strings ###

data_name = 'subhalo_jam'
level = ''
pixel_scale = 0.05

lens_name = []
lens_name.append('') # Task number beings at 1, so keep index 0 blank
lens_name.append('lens_with_00_subhalo_cuspy_source') # Index 1
lens_name.append('lens_with_05_subhalo_cuspy_source') # Index 2
lens_name.append('lens_with_00_subhalo_smooth_source') # Index 3
lens_name.append('lens_with_05_subhalo_smooth_source') # Index 4

data_path = cosma_data_path + 'data/' + cosma_username + '/' + data_name + '/' + level + '/' + lens_name[cosma_array_id]

ccd_data = ccd.load_ccd_data_from_fits(image_path=data_path + '/image.fits',
                                       psf_path=data_path + '/psf.fits',
                                       noise_map_path=data_path + '/noise_map.fits', pixel_scale=pixel_scale)

from workspace_jam.pipelines import pipeline_subhalo_inversion_no_lens_light

pipeline = \
    pipeline_subhalo_inversion_no_lens_light.make_pipeline(
        pipeline_path=data_name + '/' + level + '/'+ lens_name[cosma_array_id]+'/')

pipeline.run(data=ccd_data)