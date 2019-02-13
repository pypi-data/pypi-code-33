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

# In this pipeline, we'll perform a subhalo analysis which fits a source galaxy using a light profile
# followed by an inversion, where the lens galaxy's light is not present in the image. Two grid-searches will then be
# performed, to assess our sensitivity to subhalos and to attempt to detect subhalos in the observed image. The
# pipeline comprises four phases:

# Phase 1) Fit the lens galaxy's mass (SIE) and source galaxy's light using a single Sersic light profile.

# Phase 2) Fit the lens galaxy's mass (SIE) and source galaxy's light using an inversion, initializing the priors
#          of the lens the results of Phase 1.

# Phase 3) Perform the sensitivity analysis, using an ordinary grid search over subhalo (y,x) coordinates and mass.

# Phase 4) Perform the subhalo detection analysis, using a Multinest grid search oer subhalo (y,x) coordinate cells,
#          where each phase optimizes the subhalo position in these cells as well as its mass and concentration.

def make_pipeline(pipeline_path=''):

    pipeline_name = 'pipeline_subhalo_light_profile_no_lens_light'
    pipeline_path = pipeline_path + pipeline_name

    ### PHASE 1 ###

    # In phase 1, we will fit the lens galaxy's mass and one source galaxy, where we:

    # 1) Set our priors on the lens galaxy (y,x) centre such that we assume the image is centred around the lens galaxy.

    class LensSourcePhase(ph.LensSourcePlanePhase):

        def pass_priors(self, previous_results):

            self.lens_galaxies.lens.mass.centre_0 = prior.GaussianPrior(mean=0.0, sigma=0.1)
            self.lens_galaxies.lens.mass.centre_1 = prior.GaussianPrior(mean=0.0, sigma=0.1)

    phase1 = LensSourcePhase(lens_galaxies=dict(lens=gm.GalaxyModel(mass=mp.EllipticalIsothermal)),
                             source_galaxies=dict(source=gm.GalaxyModel(light=lp.EllipticalSersic)),
                             optimizer_class=nl.MultiNest,
                             phase_name=pipeline_path + '/phase_1_source')

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
                            source_galaxies=dict(source=gm.GalaxyModel(light=lp.EllipticalSersic)),
                            optimizer_class=nl.MultiNest,
                            phase_name=pipeline_path + '/phase_2_inversion')

    phase2.optimizer.const_efficiency_mode = True
    phase2.optimizer.n_live_points = 50
    phase2.optimizer.sampling_efficiency = 0.5

    ### Phase 3 ###

    # In phase 3, we perform the sensitivity analysis of our lens, using a grid search of subhalo (y,x) coordinates and
    # mass, where:

    # 1) The lens model and source-pixelization parameters are held fixed to the best-fit values from phase 2.

    class GridPhase(ph.LensSourcePlanePhase):

        def pass_priors(self, previous_results):

            self.lens_galaxies.lens.mass = previous_results[1].constant.lens.mass
            self.source_galaxies.source = previous_results[1].constant.source

            self.lens_galaxies.subhalo.mass.centre_0 = prior.UniformPrior(lower_limit=-2.0, upper_limit=2.0)
            self.lens_galaxies.subhalo.mass.centre_1 = prior.UniformPrior(lower_limit=-2.0, upper_limit=2.0)
            self.lens_galaxies.subhalo.mass.kappa_s = prior.UniformPrior(lower_limit=0.0, upper_limit=1.0)
            self.lens_galaxies.subhalo.mass.scale_radius = 5.0

    phase3 = GridPhase(lens_galaxies=dict(lens=gm.GalaxyModel(mass=mp.EllipticalIsothermal),
                                          subhalo=gm.GalaxyModel(mass=mp.SphericalNFW)),
                       source_galaxies=dict(source=gm.GalaxyModel(light=lp.EllipticalSersic)),
                       optimizer_class=nl.GridSearch,
                       phase_name=pipeline_path + '/phase_3_sensitivity')

    ### Phase 4 ###

    # In phase 4, we attempt to detect subhalos, by performing a NxN grid search of MultiNest searches, where:

    # 1) The lens model and source-pixelization parameters are held fixed to the best-fit values from phase 2.
    # 2) Each grid search varies the subhalo (y,x) coordinates and mass as free parameters.
    # 3) The priors on these (y,x) coordinates are UniformPriors, with limits corresponding to the grid-cells.

    class GridPhase(autofit_ph.as_grid_search(ph.LensSourcePlanePhase)):

        @property
        def grid_priors(self):
            return [self.variable.subhalo.mass.centre_0, self.variable.subhalo.mass.centre_1]

        def pass_priors(self, previous_results):

            self.lens_galaxies.subhalo.mass.centre_0 = prior.UniformPrior(lower_limit=-2.0, upper_limit=2.0)
            self.lens_galaxies.subhalo.mass.centre_1 = prior.UniformPrior(lower_limit=-2.0, upper_limit=2.0)
            self.lens_galaxies.subhalo.mass.kappa_s = prior.UniformPrior(lower_limit=0.0, upper_limit=0.2)

            self.lens_galaxies.lens.mass = previous_results[1].constant.lens.mass
            self.source_galaxies.source = previous_results[1].constant.source


    phase4 = GridPhase(lens_galaxies=dict(lens=gm.GalaxyModel(mass=mp.EllipticalIsothermal),
                                          subhalo=gm.GalaxyModel(mass=mp.SphericalNFW)),
                       source_galaxies=dict(source=gm.GalaxyModel(light=lp.EllipticalSersic)),
                       number_of_steps=6, optimizer_class=nl.MultiNest,
                       phase_name=pipeline_path + '/phase_4_subhalo_search')

    return pipeline.PipelineImaging(pipeline_path, phase1, phase2, phase3, phase4)