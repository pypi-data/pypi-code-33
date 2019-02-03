import os

from autofit import conf
from autofit.core import model_mapper as mm
from autofit.core import non_linear as nl
from autolens.pipeline import phase as ph
from autolens.pipeline import pipeline
from autolens.data import ccd as im
from autolens.data.array import mask as ma
from autolens.model.inversion import pixelizations as pix
from autolens.model.inversion import regularization as reg
from autolens.model.galaxy import galaxy_model as gm
from autolens.model.profiles import light_profiles as lp
from autolens.model.profiles import mass_profiles as mp
from autolens.data.plotters import imaging_plotters

pixel_scale = 0.02

path = '{}/../'.format(os.path.dirname(os.path.realpath(__file__)))
conf.instance = conf.Config(config_path=path+'config', output_path=path+'output')


image = im.load_ccd_data_from_fits(image_path=path + '/datas/chentao2/G09.97_870.fits', pixel_scale=0.02,
                                   psf_path=path+'/datas/chentao2/psf.fits',
                                   noise_map_path=path+'/datas/chentao2/noise_maps.fits',
                                   resized_ccd_shape=(400, 400), renormalize_psf=True)

image.noise_map = image.noise_map*1.5

image.psf = im.PSF.simulate_as_gaussian_via_alma_fits_header_parameters(shape=(21, 21), pixel_scale=pixel_scale,
                                                                        x_stddev=5.272060218785E-05,
                                                                        y_stddev=3.427845943305E-05 ,
                                                                        theta=5.982536315918E+01)

mask = ma.Mask.circular(shape=image.shape, pixel_scale=pixel_scale, radius_arcsec=3.0)

imaging_plotters.plot_image_subplot(image=image, mask=mask, positions=[[[0.9, 0.55], [-0.22, -0.56]]])

def make_pipeline():

    pipeline_name = 'chentao_new2'  # Give the pipeline a name.

    def mask_function(img):
        return ma.Mask.circular(shape=image.shape, pixel_scale=pixel_scale, radius_arcsec=3.0)

    class ParametricPhase(ph.LensSourcePlanePhase):

        def pass_priors(self, previous_results):

            self.lens_galaxies.lens_0.mass.centre_0 = 0.9
            self.lens_galaxies.lens_0.mass.centre_1 = 0.55
            self.lens_galaxies.lens_1.mass.centre_0 = -0.22
            self.lens_galaxies.lens_1.mass.centre_1 = -0.56

            self.source_galaxies.source_0.light.centre_0 = mm.GaussianPrior(mean=0.0, sigma=1.0)
            self.source_galaxies.source_0.light.centre_1 = mm.GaussianPrior(mean=0.0, sigma=1.0)
            self.source_galaxies.source_0.light.intensity = mm.UniformPrior(lower_limit=0.0, upper_limit=0.001)
            self.source_galaxies.source_1.light.centre_0 = mm.GaussianPrior(mean=0.0, sigma=1.0)
            self.source_galaxies.source_1.light.centre_1 = mm.GaussianPrior(mean=0.0, sigma=1.0)
            self.source_galaxies.source_1.light.intensity = mm.UniformPrior(lower_limit=0.0, upper_limit=0.001)

    phase1 = ParametricPhase(lens_galaxies=dict(lens_0=gm.GalaxyModel(mass=mp.SphericalIsothermal),
                                                lens_1=gm.GalaxyModel(mass=mp.SphericalIsothermal)),
                                 source_galaxies=dict(source_0=gm.GalaxyModel(light=lp.SphericalSersic),
                                                      source_1=gm.GalaxyModel(light=lp.SphericalSersic)),
                                 optimizer_class=nl.MultiNest, mask_function=mask_function,
                                 positions=[[[1.72, 0.55], [-1.63, 0.36], [0.14, -1.4], [0.0, -0.25]]],
                                 phase_name=pipeline_name + '/phase_1_fit_source')

    phase1.optimizer.n_live_points = 75
    phase1.optimizer.sampling_efficiency = 0.1
    phase1.optimizer.evidence_tolerance = 100000.0


    class ParametricPhase(ph.LensSourcePlanePhase):

        def pass_priors(self, previous_results):

            self.lens_galaxies.lens_0.mass.centre_0 = mm.GaussianPrior(mean=0.9, sigma=0.1)
            self.lens_galaxies.lens_0.mass.centre_1 = mm.GaussianPrior(mean=0.55, sigma=0.1)
            self.lens_galaxies.lens_1.mass.centre_0 = mm.GaussianPrior(mean=-0.22, sigma=0.1)
            self.lens_galaxies.lens_1.mass.centre_1 = mm.GaussianPrior(mean=-0.56, sigma=0.1)

            self.lens_galaxies.lens_0.mass.einstein_radius = previous_results[0].variable.lens_0.mass.einstein_radius
            self.lens_galaxies.lens_1.mass.einstein_radius = previous_results[0].variable.lens_1.mass.einstein_radius

            self.source_galaxies.source_0.light.centre_0 = previous_results[0].variable.source_0.light.centre_0
            self.source_galaxies.source_0.light.centre_1 = previous_results[0].variable.source_0.light.centre_1
            self.source_galaxies.source_0.light.intensity = previous_results[0].variable.source_0.light.intensity
            self.source_galaxies.source_0.light.effective_radius = previous_results[0].variable.source_0.light.effective_radius
            self.source_galaxies.source_0.light.sersic_index = previous_results[0].variable.source_0.light.sersic_index

            self.source_galaxies.source_1.light.centre_0 = previous_results[0].variable.source_1.light.centre_0
            self.source_galaxies.source_1.light.centre_1 = previous_results[0].variable.source_1.light.centre_1
            self.source_galaxies.source_1.light.intensity = previous_results[0].variable.source_1.light.intensity
            self.source_galaxies.source_1.light.effective_radius = previous_results[0].variable.source_1.light.effective_radius
            self.source_galaxies.source_1.light.sersic_index = previous_results[0].variable.source_1.light.sersic_index

    phase2 = ParametricPhase(lens_galaxies=dict(lens_0=gm.GalaxyModel(mass=mp.EllipticalIsothermal),
                                                lens_1=gm.GalaxyModel(mass=mp.EllipticalIsothermal)),
                                 source_galaxies=dict(source_0=gm.GalaxyModel(light=lp.EllipticalSersic),
                                                      source_1=gm.GalaxyModel(light=lp.EllipticalSersic)),
                                 optimizer_class=nl.MultiNest, mask_function=mask_function,
                                 positions=[[[1.72, 0.55], [-1.63, 0.36], [0.14, -1.4], [0.0, -0.25]]],
                                 phase_name=pipeline_name + '/phase_2_fit_source')

    phase2.optimizer.n_live_points = 50
    phase2.optimizer.sampling_efficiency = 0.2
    phase2.optimizer.evidence_tolerance = 1.0
    phase2.optimizer.const_efficiency_mode = True

    def mask_function(img):
        return ma.Mask.circular(shape=image.shape, pixel_scale=pixel_scale, radius_arcsec=2.9)

    class InversionPhase(ph.LensSourcePlanePhase):

        def pass_priors(self, previous_results):

            self.lens_galaxies.lens_0 = previous_results[1].constant.lens_0
            self.lens_galaxies.lens_1 = previous_results[1].constant.lens_1

            self.source_galaxies.source.pixelization.shape_0 = mm.UniformPrior(lower_limit=20.0, upper_limit=45.0)
            self.source_galaxies.source.pixelization.shape_1 = mm.UniformPrior(lower_limit=20.0, upper_limit=45.0)

            self.source_galaxies.source.regularization.coefficients_0 = \
                mm.UniformPrior(lower_limit=0.0, upper_limit=500000.0)

    phase3 = InversionPhase(lens_galaxies=dict(lens_0=gm.GalaxyModel(mass=mp.EllipticalIsothermal),
                                                lens_1=gm.GalaxyModel(mass=mp.EllipticalIsothermal)),
                            source_galaxies=dict(source=gm.GalaxyModel(pixelization=pix.AdaptiveMagnification,
                                                                      regularization=reg.Constant)),
                            mask_function=mask_function,
                            positions=[[[1.72, 0.55], [-1.63, 0.36], [0.14, -1.4], [0.0, -0.25]]],
                            optimizer_class=nl.MultiNest, phase_name=pipeline_name + '/phase_3_inversion_adaptive_init_noise_x1.5')

    phase3.optimizer.n_live_points = 20
    phase3.optimizer.sampling_efficiency = 0.8

    class InversionPhase(ph.LensSourcePlanePhase):

        def pass_priors(self, previous_results):

            self.lens_galaxies.lens_0 = previous_results[1].variable.lens_0
            self.lens_galaxies.lens_1 = previous_results[1].variable.lens_1
            self.source_galaxies.source.regularization.coefficients_0 = \
                previous_results[2].variable.source.regularization.coefficients_0
            self.source_galaxies.source.pixelization.shape_0 = previous_results[2].variable.source.pixelization.shape_0
            self.source_galaxies.source.pixelization.shape_1 = previous_results[2].variable.source.pixelization.shape_1

    phase4 = InversionPhase(lens_galaxies=dict(lens_0=gm.GalaxyModel(mass=mp.EllipticalIsothermal),
                                                lens_1=gm.GalaxyModel(mass=mp.EllipticalIsothermal)),
                            source_galaxies=dict(source=gm.GalaxyModel(pixelization=pix.AdaptiveMagnification,
                                                                      regularization=reg.Constant)),
                            mask_function=mask_function,
                            positions=[[[1.72, 0.55], [-1.63, 0.36], [0.14, -1.4], [0.0, -0.25]]],
                            optimizer_class=nl.MultiNest, phase_name=pipeline_name + '/phase_4_inversion_adaptive_noise_x1.5')

    phase4.optimizer.n_live_points = 40
    phase4.optimizer.sampling_efficiency = 0.7
    phase4.optimizer.const_efficiency_mode = True
    phase4.optimizer.n_iter_before_update = 5

    return pipeline.PipelineImaging(pipeline_name, phase1, phase2, phase3, phase4)

pipeline_chentao=make_pipeline()
pipeline_chentao.run(data=image)