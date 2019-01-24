from autofit import conf
from autolens.data import ccd
from autolens.data.plotters import ccd_plotters

import os

# Before we go through the runner, you need to setup a workspace in cosma on your home directory
# ('/cosma/home/durham/cosma_username'). Now, your home directory is given a limited amount of hard-disk space, so it
# is key that the parts of the workspace which store large amounts of data (e.g. the data and output folders) are
# omitted from this workspace.

# To setup your cosma workspace, the following commands should work from a terminal:

# 1) ssh -X cosma_username@login.cosma.dur.ac.uk

#    This command ssh's you into cosma, and should be something you're familiar with. It'll login you into your home
#    directory ('/cosma/home/durham/cosma_username')

# 2) cp -r /cosma/home/durham/pdtw24/workspace .

#    This command will copy my template cosma workspace from my cosma home directory to yours.

# Now we need to setup your cosma environment so that it can run PyAutoLens.

# module purge
# module import python/3.6.5
# source /cosma/home/durham/pdtw24/PyAutoLens/bin/activate

# Welcome to the cosma pipeline runner. Hopefully, you're familiar with runners at this point, and have been using them
# with PyAutoLens to model lenses on your laptop. If not, I'd recommend you get used to that, before trying to run
# PyAutoLens on a super-computer. You need some familiarity with the software and lens modeling before trying to
# model a large sample of lenses on a supercomputer!

# If you are ready, then let me take you through the cosma runner. To be honest, it looks incredibly similar to the
# ordinary pipeline runners, however it has to make a few changes for running on cosma:

# 1) The data path is over-written to the path '/cosma5/cosma_username/data/' as oppossed to being in the workspace

# Given your username is where your data is stored, you'll need to put your cosma username here.
cosma_username = 'pdtw24'

# Get the relative path to the config files and output folder in our workspace.
path = '{}/../'.format(os.path.dirname(os.path.realpath(__file__)))

# Use this path to explicitly set the config path and output path.
conf.instance = conf.Config(config_path=path+'config', output_path='/cosma5/data/'+cosma_username+'/output')

# It is convenient to specify the lens name as a string, so that if the pipeline is applied to multiple images we \
# don't have to change all of the path entries in the load_ccd_data_from_fits function below.

# lens_name = 'lens_light_and_x1_source' # An example simulated image with lens light emission and a source galaxy.
# pixel_scale = 0.1

lens_name = []
lens_name.append('') # Task number beings at 1, so keep index 0 blank
lens_name.append('slacs1430+4105') # Index 1

pixel_scale = 0.03

cosma_array = 1

cosma_data_path = '/cosma5/data/durham/autolens/'+cosma_username

ccd_data = ccd.load_ccd_data_from_fits(
    image_path=cosma_data_path + '/data/example/' + lens_name[cosma_array] + '/image.fits',
    psf_path=cosma_data_path+'/data/example/'+lens_name[cosma_array]+'/psf.fits',
    noise_map_path=cosma_data_path+'/data/example/'+lens_name[cosma_array]+'/noise_map.fits',
    pixel_scale=pixel_scale)

ccd_plotters.plot_ccd_subplot(ccd_data=ccd_data)

# Running a pipeline is easy, we simply import it from the pipelines folder and pass the lens data to its run function.
# Below, we'll' use a 3 phase example pipeline to fit the data with a parametric lens light, mass and source light
# profile. Checkout _workspace/pipelines/examples/lens_light_and_x1_source_parametric.py_' for a full description of
# the pipeline.

from pipelines.examples import lens_light_and_x1_source_parametric

pipeline = lens_light_and_x1_source_parametric.make_pipeline(pipeline_path='example/' + lens_name[cosma_array] + '/')

pipeline.run(data=ccd_data)