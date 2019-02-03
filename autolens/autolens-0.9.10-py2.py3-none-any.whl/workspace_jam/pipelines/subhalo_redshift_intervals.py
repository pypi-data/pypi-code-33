from autofit.optimize import non_linear as nl
from autofit.mapper import model_mapper as mm
from autolens.data.array import mask as msk
from autolens.model.galaxy import galaxy_model as gm
from autolens.pipeline import phase as ph
from autolens.pipeline import pipeline
from autolens.model.profiles import light_profiles as lp
from autolens.model.profiles import mass_profiles as mp
from autolens.model.inversion import pixelizations as pix
from autolens.model.inversion import regularization as reg

import os

# In this pipeline, we'll perform a subhalo analysis which fits a source galaxy using a light profile
# followed by an inversion, where the lens galaxy's light is not present in the image. A subhalo grid-search will
# then be performed to try and detec the subhalo. The pipeline comprises three phases:

# Phase 1) Fit the lens galaxy's mass (SIE) and source galaxy's light using a single Sersic light profile.

# Phase 2) Fit the lens galaxy's mass (SIE) and source galaxy's light using an inversion, initializing the priors
#          of the lens the results of Phase 1.

# Phase 3) Perform the grid-search of the subhalo.

def make_pipeline(pipeline_path=''):

    pipeline_name = 'pipeline_redshift_intervals'
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

            self.lens_galaxies.lens.mass.centre_0 = mm.GaussianPrior(mean=0.0, sigma=0.1)
            self.lens_galaxies.lens.mass.centre_1 = mm.GaussianPrior(mean=0.0, sigma=0.1)

    phase1 = LensSourcePhase(lens_galaxies=dict(lens=gm.GalaxyModel(mass=mp.EllipticalIsothermal)),
                               source_galaxies=dict(source=gm.GalaxyModel(light=lp.EllipticalSersic)),
                               mask_function=mask_function_annular, optimizer_class=nl.MultiNest,
                               phase_name=pipeline_path + '/phase_1_source')

    # You'll see these lines throughout all of the example pipelines. They are used to make MultiNest sample the \
    # non-linear parameter space faster (if you haven't already, checkout 'tutorial_7_multinest_black_magic' in
    # 'howtolens/chapter_2_lens_modeling'.

    # Fitting the lens galaxy and source galaxy from uninitialized priors often risks MultiNest getting stuck in a
    # local maxima, especially for the image in this example which actually has two source galaxies. Therefore, whilst
    # I will continue to use constant efficiency mode to ensure fast run time, I've upped the number of live points
    # and decreased the sampling efficiency from the usual values to ensure the non-linear search is robust.

    phase1.optimizer.const_efficiency_mode = True
    phase1.optimizer.n_live_points = 80
    phase1.optimizer.sampling_efficiency = 0.2

    ### PHASE 2 ###

    # In phase 2, we fit the lens's mass and source galaxy using an inversion, where we:

    # 1) Initialize the priors on the lens galaxy using the results of phase 1.
    # 2) Assume default priors for all source inversion parameters.

    class InversionPhase(ph.LensSourcePlanePhase):

        def pass_priors(self, previous_results):

            self.lens_galaxies.lens.mass = previous_results[0].variable.lens.mass

    phase2 = InversionPhase(lens_galaxies=dict(lens=gm.GalaxyModel(mass=mp.EllipticalIsothermal)),
                            source_galaxies=dict(source=gm.GalaxyModel(pixelization=pix.AdaptiveMagnification,
                                                                      regularization=reg.Constant)),
                            optimizer_class=nl.MultiNest, mask_function=mask_function_annular,
                            phase_name=pipeline_path + '/phase_2_inversion')

    phase2.optimizer.const_efficiency_mode = True
    phase2.optimizer.n_live_points = 50
    phase2.optimizer.sampling_efficiency = 0.5

    ### PHASE 3 ###

    # In phase 3, we fit the lens's mass and source galaxy using an inversion, where we:

    class SubhaloPhase(ph.MultiPlanePhase):

        def pass_priors(self, previous_results):

            self.galaxies.lens.mass = previous_results[1].constant.lens.mass
            self.galaxies.source.pixelization = previous_results[1].constant.source.pixelization
            self.galaxies.source.regularization = previous_results[1].constant.source.regularization

    phase3 = SubhaloPhase(galaxies=dict(lens=gm.GalaxyModel(mass=mp.EllipticalIsothermal, redshift=0.5),
                                        source=gm.GalaxyModel(pixelization=pix.AdaptiveMagnification,
                                                              regularization=reg.Constant, redshift=1.0),
                                        subhalo=gm.GalaxyModel(mass=mp.SphericalNFW,
                                                               variable_redshift=True)),
                         optimizer_class=nl.MultiNest, mask_function=mask_function_annular,
                         phase_name=pipeline_path + '/phase_3_subhalo_with_redshift')

    return pipeline.PipelineImaging(pipeline_path, phase1, phase2, phase3)