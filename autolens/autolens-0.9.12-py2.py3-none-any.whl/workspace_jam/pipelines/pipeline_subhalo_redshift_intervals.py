from autofit.optimize import non_linear as nl
from autofit.mapper import prior
from autofit.tools import phase as autofit_ph
from autolens.data.array import mask as msk
from autolens.model.galaxy import galaxy_model as gm
from autolens.pipeline import phase as ph
from autolens.pipeline import pipeline
from autolens.model.profiles import light_profiles as lp
from autolens.model.profiles import mass_profiles as mp
from autolens.model.inversion import pixelizations as pix
from autolens.model.inversion import regularization as reg

import os

# In this pipeline, we'll perform an analysis which fits an image with a mass model and parametric source model, and 
# then performs a subhalo grid search using a 1D grid of redshifts. This pipeline comprises two phases:

# Phase 1) Fit the lens galaxy's mass (SIE) and source galaxy's light using a single Sersic light profile.

# Phase 2) Fit a 1D grid of subhalos over redshift, keeping the lens mass model and source light profile fixed to the
#          results of phase 1.

def make_pipeline(pipeline_path=''):

    pipeline_name = 'pipeline_subhalo_redshift_intervals'
    pipeline_path = pipeline_path + pipeline_name

    # As there is no lens light component, we can use an annular mask throughout this pipeline which removes the
    # central regions of the image.

    def mask_function_annular(image):
        return msk.Mask.circular_annular(shape=image.shape, pixel_scale=image.pixel_scale,
                                         inner_radius_arcsec=0.2, outer_radius_arcsec=3.3)

    ### PHASE 1 ###

    # In phase 1, we will fit the lens galaxy's mass and one source galaxy, where we:

    # 1) Set our priors on the lens galaxy (y,x) centre such that we assume the image is centred around the lens galaxy.

    class LensSourcePhase(ph.LensSourcePlanePhase):

        def pass_priors(self, previous_results):

            self.lens_galaxies.lens.mass.centre_0 = prior.GaussianPrior(mean=0.0, sigma=0.1)
            self.lens_galaxies.lens.mass.centre_1 = prior.GaussianPrior(mean=0.0, sigma=0.1)
            
            # If you want to skip the fitting in this phase, you can fix the lens model / source model parameters by
            # manually inputting them below.

            # self.lens_galaxies.lens.mass.centre_0 = 0.0
            # self.lens_galaxies.lens.mass.centre_1 = 0.0
            # self.lens_galaxies.lens.mass.axis_ratio = 0.0
            # self.lens_galaxies.lens.mass.phi = 0.0
            # self.lens_galaxies.lens.mass.einstein_radius = 0.0

            # self.source_galaxies.source.light.centre_0 = 0.0
            # self.source_galaxies.source.light.centre_1 = 0.0
            # self.source_galaxies.source.light.axis_ratio = 0.0
            # self.source_galaxies.source.light.phi = 0.0
            # self.source_galaxies.source.light.intensity = 0.0
            # self.source_galaxies.source.light.effective_radius = 0.0
            # self.source_galaxies.source.light.sersic_index = 0.0

    phase1 = LensSourcePhase(lens_galaxies=dict(lens=gm.GalaxyModel(mass=mp.EllipticalIsothermal)),
                             source_galaxies=dict(source=gm.GalaxyModel(light=lp.EllipticalSersic)),
                             mask_function=mask_function_annular, optimizer_class=nl.MultiNest,
                             phase_name=pipeline_path + '/phase_1_source')

    phase1.optimizer.const_efficiency_mode = True
    phase1.optimizer.n_live_points = 80
    phase1.optimizer.sampling_efficiency = 0.2

    ### PHASE 2 ###

    # In phase 2, we'll perform the 1D grid-search over subhalo redshift, where:

    # 1) The lens galaxy's mass and source galaxy's light are fixed to the best-fit model of phase 1.
    # 2) The (y,x) centre, mass and scale radius of the subhalo are varied as free parameters.
    # 3) The redshift is fixed to a location on a 1D grid.

    class RedshiftGridPhase(autofit_ph.as_grid_search(ph.MultiPlanePhase)):

        @property
        def grid_priors(self):
            return [self.variable.subhalo.redshift.redshift]

        def pass_priors(self, previous_results):

            # This UniformPrior specifies the range of redshifts of the 1D grid search. The number of steps below
            # sets how many steps are used.

            # The grid-search uses 8 equally distributed points between the upper and lower limits. For the setup below
            # with redshift limit 0.0 -> 2.0 and 8 steps, the 8 redshift intervals will be 0.25, 0.5, 0.75, 1.0, 1.25,
            # 1.5, 1.75

            self.galaxies.subhalo.redshift.redshift = prior.UniformPrior(lower_limit=0.0, upper_limit=2.0)

            # We fix the lens and source galaxies to their redshifts.

            self.galaxies.lens.redshift = 1.0
            self.galaxies.source.redshift = 2.0

            # For each redshift MultiNest search, the priors below specify the allowed values of the subhalo.

            self.galaxies.subhalo.mass.centre_0 = prior.UniformPrior(lower_limit=-2.0, upper_limit=2.0)
            self.galaxies.subhalo.mass.centre_1 = prior.UniformPrior(lower_limit=-2.0, upper_limit=2.0)
            self.galaxies.subhalo.mass.kappa_s = prior.UniformPrior(lower_limit=0.0, upper_limit=0.2)

            # These fix the lens mass model / source light model to the results of phase 1.

            self.galaxies.lens.mass = previous_results[0].constant.lens.mass
            self.galaxies.source.light = previous_results[0].constant.source.light


    phase2 = RedshiftGridPhase(galaxies=dict(lens=gm.GalaxyModel(mass=mp.EllipticalIsothermal),
                                             subhalo=gm.GalaxyModel(mass=mp.SphericalNFW, variable_redshift=True),
                                             source=gm.GalaxyModel(light=lp.EllipticalSersic)),
                              number_of_steps=8, optimizer_class=nl.MultiNest,
                              phase_name=pipeline_path + '/phase_2_subhalo_redshift_search')

    phase2.optimizer.const_efficiency_mode = True
    phase2.optimizer.n_live_points = 20
    phase2.optimizer.sampling_efficiency = 0.2

    return pipeline.PipelineImaging(pipeline_path, phase1, phase2)