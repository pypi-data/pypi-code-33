import numpy as np

from autolens import exc
from autolens.model.inversion import inversions
from autolens.data.fitting import fitter, fitting_util
from autolens.lens import lens_data as li
from autolens.lens import ray_tracing

minimum_value_profile = 0.1

def fit_multiple_lensing_images_with_tracer(lensing_images, tracer, padded_tracer=None):
    """Fit a list of lens unblurred_image_1d with a model tracer, automatically determining the type of fit based on the \
    properties of the galaxies in the tracer.

    Parameters
    -----------
    lensing_image : [li.LensImage] or [li.LensImage]
        List of the lens-unblurred_image_1d that are to be fitted.
    tracer : ray_tracing.AbstractTracer
        The tracer, which describes the ray-tracing of the strong lens configuration.
    padded_tracer : ray_tracing.AbstractTracer
        A tracer with an identical strong lens configuration to the tracer above, but using the lens regular's \
        padded grid_stacks such that unmasked model-unblurred_image_1d can be computed.
    """

    if tracer.has_light_profile and not tracer.has_pixelization:

        if not tracer.has_hyper_galaxy:
            return LensingProfileFit(lensing_images=lensing_images, tracer=tracer, padded_tracer=padded_tracer)
        elif tracer.has_hyper_galaxy:
            return HyperLensingProfileFit(lensing_hyper_images=lensing_images, tracer=tracer, padded_tracer=padded_tracer)

    elif not tracer.has_light_profile and tracer.has_pixelization:

        if not tracer.has_hyper_galaxy:
            return LensingInversionFit(lensing_images=lensing_images, tracer=tracer)
        elif tracer.has_hyper_galaxy:
            return HyperLensingInversionFit(lensing_hyper_images=lensing_images, tracer=tracer)

    elif tracer.has_light_profile and tracer.has_pixelization:

        if not tracer.has_hyper_galaxy:
            return LensingProfileInversionFit(lensing_images=lensing_images, tracer=tracer, padded_tracer=padded_tracer)
        elif tracer.has_hyper_galaxy:
            return HyperLensingProfileInversionFit(lensing_hyper_images=lensing_images, tracer=tracer,
                                                   padded_tracer=padded_tracer)

    else:

        raise exc.FittingException('The fit_normal routine did not call a Fit class - check the '
                                   'properties of the tracer_normal')


def fast_likelihood_from_multiple_lensing_images_and_tracer(lensing_images, tracer):
    """Fit a list of lens unblurred_image_1d with a model tracer, automatically determining the type of fit based on the \
    properties of the galaxies in the tracer.

    The likelihood is computed in the fastest, least memory-intensive, way possible, for efficient non-linear sampling.

    Parameters
    -----------
    lensing_image : [li.LensImage] or [li.LensImage]
        List of the lens-unblurred_image_1d that are to be fitted.
    tracer : ray_tracing.AbstractTracer
        The tracer, which describes the ray-tracing of the strong lens configuration.
    """
    if tracer.has_light_profile and not tracer.has_pixelization:

        if not tracer.has_hyper_galaxy:
            return LensingProfileFit.fast_likelihood(lensing_images=lensing_images, tracer=tracer)
        elif tracer.has_hyper_galaxy:
            return HyperLensingProfileFit.fast_scaled_likelihood(lensing_hyper_images=lensing_images, tracer=tracer)

    elif not tracer.has_light_profile and tracer.has_pixelization:

        if not tracer.has_hyper_galaxy:
            return LensingInversionFit.fast_evidence(lensing_images=lensing_images, tracer=tracer)
        elif tracer.has_hyper_galaxy:
            return HyperLensingInversionFit.fast_scaled_evidence(lensing_hyper_images=lensing_images, tracer=tracer)

    elif tracer.has_light_profile and tracer.has_pixelization:

        if not tracer.has_hyper_galaxy:
            return LensingProfileInversionFit.fast_evidence(lensing_images=lensing_images, tracer=tracer)
        elif tracer.has_hyper_galaxy:
            return HyperLensingProfileInversionFit.fast_scaled_evidence(lensing_hyper_images=lensing_images, tracer=tracer)

    else:

        raise exc.FittingException('The fast likelihood routine did not call a likelihood functions - check the '
                                   'properties of the tracer_normal')


def fit_lensing_image_with_tracer(lensing_image, tracer, padded_tracer=None):
    """Fit a lens regular with a model tracer, automatically determining the type of fit based on the \
    properties of the galaxies in the tracer.

    Parameters
    -----------
    lensing_image : li.Lensimage or li.LensingHyperImage
        List of the lens-unblurred_image_1d that are to be fitted.
    tracer : ray_tracing.AbstractTracer
        The tracer, which describes the ray-tracing of the strong lens configuration.
    padded_tracer : ray_tracing.AbstractTracer
        A tracer with an identical strong lens configuration to the tracer above, but using the lens regular's \
        padded grid_stacks such that unmasked model-unblurred_image_1d can be computed.
    """

    if tracer.has_light_profile and not tracer.has_pixelization:

        if not tracer.has_hyper_galaxy:
            return LensingProfileFit(lensing_images=[lensing_image], tracer=tracer, padded_tracer=padded_tracer)
        elif tracer.has_hyper_galaxy:
            return HyperLensingProfileFit(lensing_hyper_images=[lensing_image], tracer=tracer, padded_tracer=padded_tracer)

    elif not tracer.has_light_profile and tracer.has_pixelization:

        if not tracer.has_hyper_galaxy:
            return LensingInversionFit(lensing_images=[lensing_image], tracer=tracer)
        elif tracer.has_hyper_galaxy:
            return HyperLensingInversionFit(lensing_hyper_images=[lensing_image], tracer=tracer)

    elif tracer.has_light_profile and tracer.has_pixelization:

        if not tracer.has_hyper_galaxy:
            return LensingProfileInversionFit(lensing_images=[lensing_image], tracer=tracer, padded_tracer=padded_tracer)
        elif tracer.has_hyper_galaxy:
            return HyperLensingProfileInversionFit(lensing_hyper_images=[lensing_image], tracer=tracer,
                                                   padded_tracer=padded_tracer)

    else:

        raise exc.FittingException('The fit_normal routine did not call a Fit class - check the '
                                   'properties of the tracer_normal')


def fast_likelihood_from_lensing_image_and_tracer(lensing_image, tracer):
    """Fit a lens regular with a model tracer, automatically determining the type of fit based on the properties of \
     the galaxies in the tracer.

    The likelihood is computed in the fastest, least memory-intensive, way possible, for efficient non-linear sampling.

    Parameters
    -----------
    lensing_image : [li.LensImage] or [li.LensImage]
        List of the lens-unblurred_image_1d that are to be fitted.
    tracer : ray_tracing.AbstractTracer
        The tracer, which describes the ray-tracing of the strong lens configuration.
    padded_tracer : ray_tracing.AbstractTracer
        A tracer with an identical strong lens configuration to the tracer above, but using the lens regular's \
        padded grid_stacks such that unmasked model-unblurred_image_1d can be computed.
    """
    if tracer.has_light_profile and not tracer.has_pixelization:

        if not tracer.has_hyper_galaxy:
            return LensingProfileFit.fast_likelihood(lensing_images=[lensing_image], tracer=tracer)
        elif tracer.has_hyper_galaxy:
            return HyperLensingProfileFit.fast_scaled_likelihood(lensing_hyper_images=[lensing_image], tracer=tracer)

    elif not tracer.has_light_profile and tracer.has_pixelization:

        if not tracer.has_hyper_galaxy:
            return LensingInversionFit.fast_evidence(lensing_images=[lensing_image], tracer=tracer)
        elif tracer.has_hyper_galaxy:
            return HyperLensingInversionFit.fast_scaled_evidence(lensing_hyper_images=[lensing_image], tracer=tracer)

    elif tracer.has_light_profile and tracer.has_pixelization:

        if not tracer.has_hyper_galaxy:
            return LensingProfileInversionFit.fast_evidence(lensing_images=[lensing_image], tracer=tracer)
        elif tracer.has_hyper_galaxy:
            return HyperLensingProfileInversionFit.fast_scaled_evidence(lensing_hyper_images=[lensing_image],
                                                                        tracer=tracer)

    else:

        raise exc.FittingException('The fast likelihood routine did not call a likelihood functions - check the '
                                   'properties of the tracer_normal')


class AbstractLensingFit(object):

    def __init__(self, tracer, padded_tracer=None):

        self.tracer = tracer
        self.padded_tracer = padded_tracer

    @property
    def total_inversions(self):
        return len(self.tracer.mappers_of_planes)


class LensingProfileFit(fitter.AbstractConvolutionFit, AbstractLensingFit):

    def __init__(self, lensing_images, tracer, padded_tracer=None):
        """
        Class to evaluate the fit_normal between a model described by a tracer_normal and an actual lensing_image.

        Parameters
        ----------
        lensing_images : [li.LensImage]
            List of the lens-unblurred_image_1d that are to be fitted.
        tracer : ray_tracing.AbstractTracer
            The tracer, which describes the ray-tracing of the strong lens configuration.
        padded_tracer : ray_tracing.AbstractTracer
            A tracer with an identical strong lens configuration to the tracer above, but using the lens regular's \
            padded grid_stacks such that unmasked model-unblurred_image_1d can be computed.
        """
        AbstractLensingFit.__init__(self=self, tracer=tracer, padded_tracer=padded_tracer)
        super(LensingProfileFit, self).__init__(fitting_images=lensing_images, images_=tracer.image_plane_images_1d,
                                                blurring_images_=tracer.image_plane_blurring_images_1d)

    @classmethod
    def fast_likelihood(cls, lensing_images, tracer):
        """Perform the fit of this class as described above, but storing no results as class instances, thereby \
        minimizing memory use and maximizing run-speed."""
        convolvers = list(map(lambda lensing_image : lensing_image.convolver_image, lensing_images))
        noise_maps_ = list(map(lambda lensing_image : lensing_image.noise_map_, lensing_images))
        model_images_ = fitting_util.blur_image_including_blurring_region(image_=tracer.image_plane_image_1d,
                                                                          blurring_image_=tracer.image_plane_blurring_image_1d, convolver=convolvers)
        residuals_ = fitting_util.residual_map_from_data_mask_and_model_data(data=lensing_images, model_data=model_images_),
        chi_squareds_ = fitting_util.chi_squared_map_from_residual_map_mask_and_noise_map(residual_map=residuals_, noise_map=noise_maps_),
        chi_squared_terms = fitting_util.chi_squared_from_chi_squared_map(chi_squared_map=chi_squareds_)
        noise_terms = fitting_util.noise_normalization_from_mask_and_noise_map(noise_map=noise_maps_)
        return sum(fitting_util.likelihood_from_chi_squared_and_noise_normalization(chi_squared=chi_squared_terms,
                                                                                    noise_normalization=noise_terms))

    @property
    def model_images_of_planes(self):

        image_plane_images_of_planes_ = self.tracer.image_plane_images_1d_of_planes
        image_plane_blurring_images_of_planes_ = self.tracer.image_plane_blurring_images_1d_of_planes

        model_images_of_planes = [[] for _ in range(self.tracer.total_grid_stacks)]

        for image_index in range(self.tracer.total_grid_stacks):
            convolver = self.convolvers_image[image_index]
            map_to_scaled_array = self.map_to_scaled_arrays[image_index]
            for plane_index in range(self.tracer.total_planes):
                _image = image_plane_images_of_planes_[image_index][plane_index]
                if np.count_nonzero(_image): # If all entries are zero, there was no light profile
                    _blurring_image = image_plane_blurring_images_of_planes_[image_index][plane_index]
                    _blurred_image = (convolver.convolve_image(image_array=_image, blurring_array=_blurring_image))
                    _blurred_image = map_to_scaled_array(_blurred_image)
                    model_images_of_planes[image_index].append(_blurred_image)
                else:
                    model_images_of_planes[image_index].append(None)

        return model_images_of_planes

    @property
    def unmasked_model_profile_images(self):
        if self.padded_tracer is None:
            return None
        elif self.padded_tracer is not None:
            return fitting_util.unmasked_blurred_images_from_fitting_images(fitting_images=self.datas_,
                                                                            unmasked_images_=self.padded_tracer.image_plane_image_1d)

    @property
    def unmasked_model_profile_images_of_galaxies(self):
        if self.padded_tracer is None:
            return None
        elif self.padded_tracer is not None:
            return unmasked_model_images_of_galaxies_from_lensing_images_and_tracer(lensing_images=self.datas_,
                                                                                    tracer=self.padded_tracer)

    @property
    def unmasked_model_profile_image(self):
        if self.padded_tracer is None:
            return None
        elif self.padded_tracer is not None:
            return self.unmasked_model_profile_images[0]


class HyperLensingProfileFit(LensingProfileFit, fitter.AbstractHyperFit):

    def __init__(self, lensing_hyper_images, tracer, padded_tracer=None):
        """
        Class to evaluate the fit_normal between a model described by a tracer_normal and an actual lensing_image.

        Parameters
        ----------
        lensing_hyper_images : [li.LensImage]
            List of the lens hyper unblurred_image_1d that are to be fitted.
        tracer : ray_tracing.AbstractTracer
            The tracer, which describes the ray-tracing of the strong lens configuration.
        padded_tracer : ray_tracing.AbstractTracer
            A tracer with an identical strong lens configuration to the tracer above, but using the lens regular's \
            padded grid_stacks such that unmasked model-unblurred_image_1d can be computed.
        """

        fitter.AbstractHyperFit.__init__(self=self, fitting_hyper_images=lensing_hyper_images,
                                         hyper_galaxies=tracer.hyper_galaxies)
        super(HyperLensingProfileFit, self).__init__(lensing_hyper_images, tracer, padded_tracer)

        self.scaled_chi_squareds_ = fitting_util.chi_squared_map_from_residual_map_mask_and_noise_map(self.residuals,
                                                                                                      self.scaled_noise_maps_)

    @classmethod
    def fast_scaled_likelihood(cls, lensing_hyper_images, tracer):
        """Perform the fit of this class as described above, but storing no results as class instances, thereby \
        minimizing memory use and maximizing run-speed."""

        contributions_ = fitting_util.contributions_from_fitting_hyper_images_and_hyper_galaxies(
            fitting_hyper_images=lensing_hyper_images, hyper_galaxies=tracer.hyper_galaxies)

        scaled_noise_maps_ = fitting_util.scaled_noise_maps_from_fitting_hyper_images_contributions_and_hyper_galaxies(
            fitting_hyper_images=lensing_hyper_images, contributions_=contributions_,
            hyper_galaxies=tracer.hyper_galaxies)

        convolvers = list(map(lambda lensing_image : lensing_image.convolver_image, lensing_hyper_images))
        model_images_ = fitting_util.blur_image_including_blurring_region(image_=tracer.image_plane_image_1d,
                                                                          blurring_image_=tracer.image_plane_blurring_image_1d, convolver=convolvers)
        residuals_ = fitting_util.residual_map_from_data_mask_and_model_data(data=lensing_hyper_images, model_data=model_images_),
        scaled_chi_squareds_ = fitting_util.chi_squared_map_from_residual_map_mask_and_noise_map(residual_map=residuals_,
                                                                                                 noise_map=scaled_noise_maps_)

        scaled_chi_squared_terms = fitting_util.chi_squared_from_chi_squared_map(
            chi_squared_map=scaled_chi_squareds_)
        scaled_noise_terms = fitting_util.noise_normalization_from_mask_and_noise_map(noise_map=scaled_noise_maps_)
        return sum(
            fitting_util.likelihood_from_chi_squared_and_noise_normalization(scaled_chi_squared_terms, scaled_noise_terms))

    @property
    def scaled_likelihoods(self):
        return fitting_util.likelihood_from_chi_squared_and_noise_normalization(self.scaled_chi_squared_terms,
                                                                                self.scaled_noise_terms)

    @property
    def scaled_likelihood(self):
        return sum(self.scaled_likelihoods)


class LensingInversionFit(fitter.AbstractInversionFit, AbstractLensingFit):

    def __init__(self, lensing_images, tracer):
        """
        Class to evaluate the fit_normal between a model described by a tracer_normal and an actual lensing_image.

        Parameters
        ----------
        lensing_images : [li.LensImage]
            List of the lens-unblurred_image_1d that are to be fitted.
        tracer : ray_tracing.AbstractTracer
            The tracer, which describes the ray-tracing of the strong lens configuration.
        """

        AbstractLensingFit.__init__(self=self, tracer=tracer)

        self.mapper = tracer.mappers_of_planes[0]
        self.regularization = tracer.regularizations_of_planes[0]

        super(LensingInversionFit, self).__init__(fitting_images=lensing_images, mapper=self.mapper,
                                                  regularization=self.regularization)

    @classmethod
    def fast_evidence(cls, lensing_images, tracer):
        """Perform the fit of this class as described above, but storing no results as class instances, thereby \
        minimizing memory use and maximizing run-speed."""

        noise_maps_ = list(map(lambda lensing_image : lensing_image.noise_map_, lensing_images))

        mapper = tracer.mappers_of_planes[0]
        regularization = tracer.regularizations_of_planes[0]
        inversion = inversions.inversion_from_image_mapper_and_regularization(lensing_images[0][:], noise_maps_[0],
                                                                              lensing_images[0].convolver_mapping_matrix,
                                                                              mapper, regularization)
        model_images_ = [inversion.reconstructed_data_vector]
        residuals_ = fitting_util.residual_map_from_data_mask_and_model_data(data=lensing_images, model_data=model_images_),
        chi_squareds_ = fitting_util.chi_squared_map_from_residual_map_mask_and_noise_map(residual_map=residuals_, noise_map=noise_maps_),
        chi_squared_terms = fitting_util.chi_squared_from_chi_squared_map(chi_squared_map=chi_squareds_)
        noise_terms = fitting_util.noise_normalization_from_mask_and_noise_map(noise_map=noise_maps_)
        return sum(fitting_util.evidence_from_reconstruction_terms(chi_squared_terms, [inversion.regularization_term],
                                                                   [inversion.log_det_curvature_reg_matrix_term],
                                                                   [inversion.log_det_regularization_matrix_term], noise_terms))

    @property
    def model_images_of_planes(self):
        return [[None, self.map_to_scaled_arrays[0](self.model_data_set[0])]]


class HyperLensingInversion(fitter.AbstractHyperFit):

    @property
    def scaled_model_images(self):
        return fitting_util.map_arrays_to_scaled_arrays(arrays_=self.scaled_model_images_,
                                                        map_to_scaled_arrays=self.map_to_scaled_arrays)

    @property
    def scaled_residuals(self):
        return fitting_util.map_arrays_to_scaled_arrays(arrays_=self.scaled_residuals_,
                                                        map_to_scaled_arrays=self.map_to_scaled_arrays)

    @property
    def scaled_evidences(self):
        return fitting_util.evidence_from_reconstruction_terms(self.scaled_chi_squared_terms,
                                                               [self.scaled_inversion.regularization_term],
                                                               [self.scaled_inversion.log_det_curvature_reg_matrix_term],
                                                               [self.scaled_inversion.log_det_regularization_matrix_term],
                                                               self.scaled_noise_terms)

    @property
    def scaled_evidence(self):
        return sum(self.scaled_evidences)

    @property
    def scaled_model_image(self):
        return self.scaled_model_images[0]

    @property
    def scaled_residual(self):
        return self.scaled_residuals[0]


class HyperLensingInversionFit(LensingInversionFit, HyperLensingInversion):

    def __init__(self, lensing_hyper_images, tracer):
        """
        Class to evaluate the fit_normal between a model described by a tracer_normal and an actual lensing_image.

        Parameters
        ----------
        lensing_hyper_images : [li.LensImage]
            List of the lens hyper unblurred_image_1d that are to be fitted.
        tracer : ray_tracing.AbstractTracer
            The tracer, which describes the ray-tracing of the strong lens configuration.
        """

        fitter.AbstractHyperFit.__init__(self=self, fitting_hyper_images=lensing_hyper_images,
                                         hyper_galaxies=tracer.hyper_galaxies)
        super(HyperLensingInversionFit, self).__init__(lensing_hyper_images, tracer)

        self.scaled_inversion = inversions.inversion_from_image_mapper_and_regularization(
            lensing_hyper_images[0][:], self.scaled_noise_maps_[0], lensing_hyper_images[0].convolver_mapping_matrix,
            self.inversion.mapper, self.inversion.regularization)

        self.scaled_model_images_ = [self.scaled_inversion.reconstructed_data_vector]
        self.scaled_residuals_ = fitting_util.residual_map_from_data_mask_and_model_data(self.datas_, self.scaled_model_images_)
        self.scaled_chi_squareds_ = fitting_util.chi_squared_map_from_residual_map_mask_and_noise_map(self.scaled_residuals_,
                                                                                                      self.scaled_noise_maps_)

    @classmethod
    def fast_scaled_evidence(cls, lensing_hyper_images, tracer):
        """Perform the fit of this class as described above, but storing no results as class instances, thereby \
        minimizing memory use and maximizing run-speed."""

        contributions_ = fitting_util.contributions_from_fitting_hyper_images_and_hyper_galaxies(
            fitting_hyper_images=lensing_hyper_images, hyper_galaxies=tracer.hyper_galaxies)

        scaled_noise_maps_ = fitting_util.scaled_noise_maps_from_fitting_hyper_images_contributions_and_hyper_galaxies(
            fitting_hyper_images=lensing_hyper_images, contributions_=contributions_,
            hyper_galaxies=tracer.hyper_galaxies)

        convolvers = list(map(lambda lensing_image : lensing_image.convolver_mapping_matrix, lensing_hyper_images))

        mapper = tracer.mappers_of_planes[0]
        regularization = tracer.regularizations_of_planes[0]

        scaled_inversion = inversions.inversion_from_image_mapper_and_regularization(
            lensing_hyper_images[0][:], scaled_noise_maps_[0], convolvers[0], mapper, regularization)

        scaled_residuals_ = fitting_util.residual_map_from_data_mask_and_model_data(lensing_hyper_images,
                                                                                    [scaled_inversion.reconstructed_data_vector])
        scaled_chi_squareds_ = fitting_util.chi_squared_map_from_residual_map_mask_and_noise_map(scaled_residuals_, scaled_noise_maps_)
        scaled_chi_squared_terms = fitting_util.chi_squared_from_chi_squared_map(scaled_chi_squareds_)
        scaled_noise_terms = fitting_util.noise_normalization_from_mask_and_noise_map(scaled_noise_maps_)
        return sum(fitting_util.evidence_from_reconstruction_terms(scaled_chi_squared_terms,
                                                                   [scaled_inversion.regularization_term],
                                                                   [scaled_inversion.log_det_curvature_reg_matrix_term],
                                                                   [scaled_inversion.log_det_regularization_matrix_term],
                                                                   scaled_noise_terms))


class LensingProfileInversionFit(fitter.AbstractConvolutionInversionFit, AbstractLensingFit):

    def __init__(self, lensing_images, tracer, padded_tracer=None):
        """
        Class to evaluate the fit_normal between a model described by a tracer_normal and an actual lensing_image.

        Parameters
        ----------
        lensing_images : [li.LensImage]
            List of the lens-unblurred_image_1d that are to be fitted.
        tracer : ray_tracing.AbstractTracer
            The tracer, which describes the ray-tracing of the strong lens configuration.
        padded_tracer : ray_tracing.AbstractTracer
            A tracer with an identical strong lens configuration to the tracer above, but using the lens regular's \
            padded grid_stacks such that unmasked model-unblurred_image_1d can be computed.
        """

        self.mapper = tracer.mappers_of_planes[0]
        self.regularization = tracer.regularizations_of_planes[0]

        AbstractLensingFit.__init__(self=self, tracer=tracer, padded_tracer=padded_tracer)
        super(LensingProfileInversionFit, self).__init__(fitting_images=lensing_images, images_=tracer.image_plane_images_1d,
                                                         blurring_images_=tracer.image_plane_blurring_images_1d,
                                                         mapper=self.mapper, regularization=self.regularization)

    @classmethod
    def fast_evidence(cls, lensing_images, tracer):
        """Perform the fit of this class as described above, but storing no results as class instances, thereby \
        minimizing memory use and maximizing run-speed."""
        convolvers_image = list(map(lambda lensing_image : lensing_image.convolver_image, lensing_images))
        convolvers_mapping_matrix = list(map(lambda lensing_image : lensing_image.convolver_mapping_matrix,
                                             lensing_images))

        noise_maps_ = list(map(lambda lensing_image : lensing_image.noise_map_, lensing_images))

        profile_model_images_ = fitting_util.blur_image_including_blurring_region(image_=tracer.image_plane_image_1d,
                                                                                  blurring_image_=tracer.image_plane_blurring_image_1d, convolver=convolvers_image)

        profile_subtracted_images_ = list(map(lambda lensing_image, profile_model_image_ :
                                              lensing_image[:] - profile_model_image_,
                                              lensing_images, profile_model_images_))

        mapper = tracer.mappers_of_planes[0]
        regularization = tracer.regularizations_of_planes[0]
        inversion = inversions.inversion_from_image_mapper_and_regularization(profile_subtracted_images_[0],
                                                                              noise_maps_[0], convolvers_mapping_matrix[0], mapper, regularization)
        model_images_ = [profile_model_images_[0] + inversion.reconstructed_data_vector]
        residuals_ = fitting_util.residual_map_from_data_mask_and_model_data(lensing_images[:], model_images_)
        chi_squareds_ = fitting_util.chi_squared_map_from_residual_map_mask_and_noise_map(residuals_, noise_maps_)
        chi_squared_terms = fitting_util.chi_squared_from_chi_squared_map(chi_squareds_)
        noise_terms = fitting_util.noise_normalization_from_mask_and_noise_map(noise_maps_)
        return sum(fitting_util.evidence_from_reconstruction_terms(chi_squared_terms, [inversion.regularization_term],
                                                                   [inversion.log_det_curvature_reg_matrix_term],
                                                                   [inversion.log_det_regularization_matrix_term], noise_terms))

    @property
    def model_images_of_planes(self):
        return [[self.profile_model_image, self.inversion_model_image]]


class HyperLensingProfileInversionFit(LensingProfileInversionFit, HyperLensingInversion):

    def __init__(self, lensing_hyper_images, tracer, padded_tracer=None):
        """
        Class to evaluate the fit_normal between a model described by a tracer_normal and an actual lensing_image.

        Parameters
        ----------
        lensing_hyper_images : [li.LensImage]
            List of the lens hyper unblurred_image_1d that are to be fitted.
        tracer : ray_tracing.AbstractTracer
            The tracer, which describes the ray-tracing of the strong lens configuration.
        padded_tracer : ray_tracing.AbstractTracer
            A tracer with an identical strong lens configuration to the tracer above, but using the lens regular's \
            padded grid_stacks such that unmasked model-unblurred_image_1d can be computed.
        """

        fitter.AbstractHyperFit.__init__(self=self, fitting_hyper_images=lensing_hyper_images,
                                         hyper_galaxies=tracer.hyper_galaxies)
        super(HyperLensingProfileInversionFit, self).__init__(lensing_hyper_images, tracer, padded_tracer)

        self.scaled_inversion = inversions.inversion_from_image_mapper_and_regularization(
            self.profile_subtracted_images_[0], self.scaled_noise_maps_[0],
            lensing_hyper_images[0].convolver_mapping_matrix, self.inversion.mapper, self.inversion.regularization)

        self.scaled_model_images_ = list(map(lambda _profile_model_image :
                                             _profile_model_image + self.scaled_inversion.reconstructed_data_vector,
                                             self.profile_model_images_))

        self.scaled_residuals_ = fitting_util.residual_map_from_data_mask_and_model_data(self.datas_, self.scaled_model_images_)
        self.scaled_chi_squareds_ = fitting_util.chi_squared_map_from_residual_map_mask_and_noise_map(self.scaled_residuals_,
                                                                                                      self.scaled_noise_maps_)

    @classmethod
    def fast_scaled_evidence(cls, lensing_hyper_images, tracer):
        """Perform the fit of this class as described above, but storing no results as class instances, thereby \
        minimizing memory use and maximizing run-speed."""
        contributions_ = fitting_util.contributions_from_fitting_hyper_images_and_hyper_galaxies(
            fitting_hyper_images=lensing_hyper_images, hyper_galaxies=tracer.hyper_galaxies)

        scaled_noise_maps_ = fitting_util.scaled_noise_maps_from_fitting_hyper_images_contributions_and_hyper_galaxies(
            fitting_hyper_images=lensing_hyper_images, contributions_=contributions_,
            hyper_galaxies=tracer.hyper_galaxies)

        convolvers_image = list(map(lambda lensing_image : lensing_image.convolver_image, lensing_hyper_images))
        convolvers_mapping_matrix = list(map(lambda lensing_image : lensing_image.convolver_mapping_matrix,
                                             lensing_hyper_images))

        profile_model_images_ = fitting_util.blur_image_including_blurring_region(image_=tracer.image_plane_image_1d,
                                                                                  blurring_image_=tracer.image_plane_blurring_image_1d, convolver=convolvers_image)

        profile_subtracted_images_ = list(map(lambda lensing_image, profile_model_image_ :
                                              lensing_image[:] - profile_model_image_,
                                              lensing_hyper_images, profile_model_images_))

        mapper = tracer.mappers_of_planes[0]
        regularization = tracer.regularizations_of_planes[0]

        scaled_inversion = inversions.inversion_from_image_mapper_and_regularization(
            profile_subtracted_images_[0], scaled_noise_maps_[0], convolvers_mapping_matrix[0], mapper,
            regularization)

        scaled_model_images_ = list(map(lambda profile_model_image_ :
                                        profile_model_image_ + scaled_inversion.reconstructed_data_vector,
                                        profile_model_images_))

        scaled_residuals_ = fitting_util.residual_map_from_data_mask_and_model_data(lensing_hyper_images, scaled_model_images_)
        scaled_chi_squareds_ = fitting_util.chi_squared_map_from_residual_map_mask_and_noise_map(scaled_residuals_, scaled_noise_maps_)
        scaled_chi_squared_terms = fitting_util.chi_squared_from_chi_squared_map(scaled_chi_squareds_)
        scaled_noise_terms = fitting_util.noise_normalization_from_mask_and_noise_map(scaled_noise_maps_)
        return sum(fitting_util.evidence_from_reconstruction_terms(scaled_chi_squared_terms,
                                                                   [scaled_inversion.regularization_term],
                                                                   [scaled_inversion.log_det_curvature_reg_matrix_term],
                                                                   [scaled_inversion.log_det_regularization_matrix_term],
                                                                   scaled_noise_terms))


class PositionFit:

    def __init__(self, positions, noise):

        self.positions = positions
        self.noise = noise

    @property
    def chi_squareds(self):
        return np.square(np.divide(self.maximum_separations, self.noise))

    @property
    def likelihood(self):
        return -0.5 * sum(self.chi_squareds)

    def maximum_separation_within_threshold(self, threshold):
        if max(self.maximum_separations) > threshold:
            return False
        else:
            return True

    @property
    def maximum_separations(self):
        return list(map(lambda positions: self.max_separation_of_grid(positions), self.positions))

    def max_separation_of_grid(self, grid):
        rdist_max = np.zeros((grid.shape[0]))
        for i in range(grid.shape[0]):
            xdists = np.square(np.subtract(grid[i, 0], grid[:, 0]))
            ydists = np.square(np.subtract(grid[i, 1], grid[:, 1]))
            rdist_max[i] = np.max(np.add(xdists, ydists))
        return np.max(np.sqrt(rdist_max))


# TODO : The [plane_index][galaxy_index] datas structure is going to be key to tracking galaxies / hyper galaxies in
# TODO : Multi-plane ray tracing. I never felt it was easy to follow using list comprehensions from ray_tracing.
# TODO : Can we make this neater?


def unmasked_model_images_of_galaxies_from_lensing_images_and_tracer(lensing_images, tracer):
    return list(map(lambda lensing_image, image_index :
                    unmasked_model_images_of_galaxies_from_lensing_image_and_tracer(lensing_image, tracer, image_index),
                    lensing_images, list(range(tracer.total_grid_stacks))))

def unmasked_model_images_of_galaxies_from_lensing_image_and_tracer(lensing_image, tracer, image_index):


    padded_model_images_of_galaxies = [[] for _ in range(len(tracer.all_planes))]

    for plane_index, plane in enumerate(tracer.all_planes):
        for galaxy_index in range(len(plane.galaxies)):

            _galaxy_image_plane_image = plane.image_plane_image_1d_of_galaxies[image_index][galaxy_index]

            galaxy_model_image = fitting_util.unmasked_model_image_from_fitting_image(fitting_image=lensing_image,
                                                                                      unmasked_image_=_galaxy_image_plane_image)

            padded_model_images_of_galaxies[plane_index].append(galaxy_model_image)

    return padded_model_images_of_galaxies