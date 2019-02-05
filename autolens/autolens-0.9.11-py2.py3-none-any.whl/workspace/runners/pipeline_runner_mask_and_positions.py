from autofit import conf
from autolens.data import ccd
from autolens.data.array import mask as msk
from autolens.data.plotters import ccd_plotters

import os

# In the example pipelines, there is a pipeline 'mask_and_positions.py' which uses an input mask to tailor its masking
# to the lensed source and an input set of positions to resample mass models where the multiple images do not trace
# close to one another.

# To run that pipeline, we need load these custom masks and positions, and pass them to run function, which is what we
# do below.

# Get the relative path to the config files and output folder in our workspace.
path = '{}/../'.format(os.path.dirname(os.path.realpath(__file__)))

# Use this path to explicitly set the config path and output path.
conf.instance = conf.Config(config_path=path+'config', output_path=path+'output')

# It is convenient to specify the lens name as a string, so that if the pipeline is applied to multiple images we
# don't have to change all of the path entries in the load_ccd_data_from_fits function below.


lens_name = 'lens_light_and_x1_source' # An example simulated image with lens light emission and a source galaxy.
pixel_scale = 0.1

ccd_data = ccd.load_ccd_data_from_fits(image_path=path + '/data/example/' + lens_name + '/image.fits',
                                       psf_path=path+'/data/example/'+lens_name+'/psf.fits',
                                       noise_map_path=path+'/data/example/'+lens_name+'/noise_map.fits',
                                       pixel_scale=pixel_scale)

# Load its mask from a mask.fits file generated using the tools/mask_maker.py file.
mask = msk.load_mask_from_fits(mask_path=path + '/data/example/' + lens_name + '/mask.fits', pixel_scale=0.1)

# Load its positions from a positions.fits file generated using the tools/positions_maker.py file.
positions = ccd.load_positions(positions_path=path + '/data/example/' + lens_name + '/positions.dat')

# Lets plot an image of the ccd data, mask and positions to make sure they are chosen correctly.
ccd_plotters.plot_ccd_subplot(ccd_data=ccd_data, mask=mask, positions=positions)

# Import the mask and positions pipeline, and pass it the custom mask and positions when we run it so that they are used
# by the pipeline.

from workspace.pipelines.examples import mask_and_positions

pipeline = mask_and_positions.make_pipeline(pipeline_path='example/' + lens_name + '/')

pipeline.run(data=ccd_data, mask=mask, positions=positions)

