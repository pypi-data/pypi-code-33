from autolens.data.fitting import fitting_util
from autolens.model.inversion import inversions


class AbstractFit(object):

    def __init__(self, fitting_datas, model_datas_):
        """Abstract base class of a fit to a dataset.

        All fitting quantities (datas, model_data_set, residual_map, etc.) are stored as lists, where the different entries
        of the list correspond to different datas-sets. To signify this, all quantities are pluralized. However, if a non-
        plural term is used (e.g. residual) the residual_map of the first regular are returned. This makes the interface
        for fitting single datas-sets (the most common use-case) more intuitive.

        A fit is performed using masked datas which has been mapped to 1D arrays, even if the datas is originally a 2D
        regular. The 1D representation of a datas is followed by an underscore. For example, model_data_set gives the 2D
        unblurred_image_1d of the datas, whereas model_data_set gives the 1D datas representation.

        Parameters
        -----------
        fitting_datas : [fit_data.FitData]
            The fitting unblurred_image_1d that are fitted.
        model_datas_ : [ndarray]
            The model datas the fitting unblurred_image_1d are fitted with.

        Attributes
        -----------
        datas : [scaled_array.ScaledSquarePixelArray]
            The datas that is fitted.
        noise_maps : [scaled_array.ScaledSquarePixelArray]
            The noise_map-maps used to fit the datas.
        masks : [regular.Mask]
            The masks which define the regions of the datas that are fitted.
        model_data_set : [scaled_array.ScaledSquarePixelArray]
            The model dataset used to fit the datas
        map_to_scaled_arrays : [func]
            Functions which map the masked 1D arrays of the datas, model_data, residual_map, etc. to their 2D datas
            representation (if an regular)
        residual_map : [scaled_array.ScaledSquarePixelArray]
            The residual_map of the fit (datas - model_data).
        chi_squared_map : [scaled_array.ScaledSquarePixelArray]
            The chi-sqaureds of the fit ((datas - model_data) / noise_maps ) **2.0
        chi_squareds : [float]
            The summed chi-squared of every datas-point in a fit.
        chi_squareds_term : float
            The summed chi_squareds for all datasets.
        reduced_chi_squareds : [float]
            The reduced chi_squared of the fit to every datas-set (chi_squared / number of datas points).
        reduced_chi_squared : [float]
            The summed reduced chi_squared of the fit between datas and model for all datasets.
        noise_normalizations : [float]
            The normalization term of a likelihood function assuming Gaussian noise_map in every datas-point.
        noise_normalization : float
            The sum of all noise_normalizations for all datasets.
        likelihoods : [float]
            The likelihood of every fit between datas and model -0.5 * (chi_squared + noise_normalization)
        likelihood : float
            The summed likelihood of the fit between datas and model for all datasets.
        """

        self.datas_ = list(map(lambda fit_data : fit_data[:], fitting_datas))
        self.noise_maps_ = list(map(lambda fit_data : fit_data.noise_map_, fitting_datas))
        self.masks = list(map(lambda fit_data : fit_data.mask, fitting_datas))
        self.map_to_scaled_arrays = list(map(lambda fit_data: fit_data.grids.regular.scaled_array_from_array_1d,
                                             fitting_datas))

        self.model_datas_ = model_datas_
        self.residuals_ = fitting_util.residual_map_from_data_mask_and_model_data(data=self.datas_,
                                                                                  model_data=self.model_datas_)
        self.chi_squareds_ = fitting_util.chi_squared_map_from_residual_map_mask_and_noise_map(self.residuals_, self.noise_maps_)

    @property
    def chi_squared_terms(self):
        return fitting_util.chi_squared_from_chi_squared_map(self.chi_squareds_)

    @property
    def chi_squared_term(self):
        return sum(self.chi_squared_terms)

    @property
    def reduced_chi_squareds(self):
        return list(map(lambda chi_squared_term, mask : chi_squared_term / mask.pixels_in_mask,
                        self.chi_squared_terms, self.masks))

    @property
    def reduced_chi_squared(self):
        return sum(self.reduced_chi_squareds)

    @property
    def noise_terms(self):
        return fitting_util.noise_normalization_from_mask_and_noise_map(self.noise_maps_)

    @property
    def noise_term(self):
        return sum(self.noise_terms)

    @property
    def likelihoods(self):
        return fitting_util.likelihood_from_chi_squared_and_noise_normalization(self.chi_squared_terms, self.noise_terms)

    @property
    def likelihood(self):
        return sum(self.likelihoods)

    @property
    def noise_maps(self):
        return fitting_util.map_arrays_to_scaled_arrays(arrays_=self.noise_maps_, map_to_scaled_arrays=self.map_to_scaled_arrays)

    @property
    def model_datas(self):
        return fitting_util.map_arrays_to_scaled_arrays(arrays_=self.model_datas_, map_to_scaled_arrays=self.map_to_scaled_arrays)

    @property
    def residuals(self):
        return fitting_util.map_arrays_to_scaled_arrays(arrays_=self.residuals_, map_to_scaled_arrays=self.map_to_scaled_arrays)

    @property
    def chi_squareds(self):
        return fitting_util.map_arrays_to_scaled_arrays(arrays_=self.chi_squareds_, map_to_scaled_arrays=self.map_to_scaled_arrays)

    @property
    def noise_map(self):
        return self.noise_maps[0]

    @property
    def model_data(self):
        return self.model_datas[0]

    @property
    def residual(self):
        return self.residuals[0]

    @property
    def chi_squared(self):
        return self.chi_squareds[0]


class AbstractDataFit(AbstractFit):

    def __init__(self, fitting_datas, model_datas_):
        """Abstract Base class of a fit between datas-set and model, see *AbstractFitter*.

        Parameters
        -----------
        fitting_datas : [fit_data.FitData]
            The fitting unblurred_image_1d that are fitted.
        model_datas_ : [ndarray]
            The model datas the fitting unblurred_image_1d are fitted with."""

        self.datas = list(map(lambda fit_data : fit_data.array, fitting_datas))
        super(AbstractDataFit, self).__init__(fitting_datas=fitting_datas, model_datas_=model_datas_)


class AbstractImageFit(AbstractFit):

    def __init__(self, fitting_images, model_images_):
        """Abstract Base class of a fit between datas-set and model, see *AbstractFitter*.

        This class is used to add the terms 'unblurred_image_1d' and 'model_images' to the attributes of a fit. However, they
        function identical to datas and model_data_set, and this is done onoly for the user interface.

        Parameters
        -----------
        fitting_images : [fit_data.FitData]
            The fitting unblurred_image_1d that are fitted.
        model_data_set : [ndarray]
            The model unblurred_image_1d the fitting unblurred_image_1d are fitted with.
        """

        self.images = list(map(lambda fit_image : fit_image.image, fitting_images))
        super(AbstractImageFit, self).__init__(fitting_datas=fitting_images, model_datas_=model_images_)

    @property
    def model_images(self):
        return self.model_datas

    @property
    def model_image(self):
        return self.model_datas[0]


class AbstractHyperFit(object):

    def __init__(self, fitting_hyper_images, hyper_galaxies):
        """Abstract base class of a hyper-fit.

        A hyper-fit is a fit which performs a fit as described in the *AbstractFitter*, but also includes a set of
        parameters which allow the noise_map-map of the datas-set to be scaled. This is done to prevent over-fitting
        small regions of a datas-set with high chi-squared values and therefore provide a global fit to the overall
        datas-set.

        This is performed using an existing model of the datas-set to compute a contribution_maps regular, which a set of
        hyper-parameters then use to increase the noise_map in localized regions of the datas-set.

        Parameters
        -----------
        fitting_hyper_images : [fit_data.FitDataHyper]
            The fitting unblurred_image_1d that are fitted, which include the hyper-unblurred_image_1d used for scaling the noise_map-map.
        hyper_galaxies : [galaxy.Galaxy]
            The hyper-galaxies which represent the model components used to scale the noise_map, which correspond to
            individual galaxies in the regular.

        Attributes
        -----------
        contribution_maps : [[scaled_array.ScaledSquarePixelArray]]
            The contribution map of every regular, where there is an individual contribution map for each hyper-galaxy in
            the model.
        scaled_noise_maps : [scaled_array.ScaledSquarePixelArray]
            The scaled noise_map maps of the regular, computed after using the hyper-galaxies.
        scaled_chi_squared_terms : [float]
            The summed scaled chi-squared of every datas-point in a fit.
        scaled_chi_squareds_term : float
            The sum of all scaled_chi_squared_terms for all unblurred_image_1d.
        scaled_noise_terms : [float]
            The normalization term of a likelihood function assuming Gaussian noise_map in every datas-point, using the
            scaled noise_map-map.
        scaled_noise_term : float
            The sum of all scaled_noise_terms for all unblurred_image_1d.
        scaled_likelihoods : [float]
            The likelihood of every fit between datas and model using the scaled noise_map-map's fit \
            -0.5 * (scaled_chi_squared_term + scaled_noise_term)
        scaled_likelihood : float
            The summed scaled likelihood of the fit between datas and model for all unblurred_image_1d.
        """

        self.is_hyper_fit = True
        self.contributions_ = \
            fitting_util.contributions_from_fitting_hyper_images_and_hyper_galaxies(fitting_hyper_images=fitting_hyper_images,
                                                                                    hyper_galaxies=hyper_galaxies)


        self.scaled_noise_maps_ =\
            fitting_util.scaled_noise_maps_from_fitting_hyper_images_contributions_and_hyper_galaxies(
                fitting_hyper_images=fitting_hyper_images, contributions_=self.contributions_,
                hyper_galaxies=hyper_galaxies)

    @property
    def scaled_chi_squared_terms(self):
        return fitting_util.chi_squared_from_chi_squared_map(self.scaled_chi_squareds_)

    @property
    def scaled_noise_terms(self):
        return fitting_util.noise_normalization_from_mask_and_noise_map(self.scaled_noise_maps_)

    @property
    def scaled_noise_maps(self):
        return fitting_util.map_arrays_to_scaled_arrays(arrays_=self.scaled_noise_maps_,
                                                        map_to_scaled_arrays=self.map_to_scaled_arrays)

    @property
    def scaled_chi_squareds(self):
        return fitting_util.map_arrays_to_scaled_arrays(arrays_=self.scaled_chi_squareds_,
                                                        map_to_scaled_arrays=self.map_to_scaled_arrays)

    @property
    def contributions(self):
        contributions = [[] for _ in range(len(self.contributions_))]
        for image_index in range(len(contributions)):
            contributions[image_index] = list(map(lambda _contributions :
                                                  self.map_to_scaled_arrays[image_index](_contributions),
                                                  self.contributions_[image_index]))
        return contributions

    @property
    def scaled_noise_map(self):
        return self.scaled_noise_maps[0]

    @property
    def scaled_chi_squared(self):
        return self.scaled_chi_squareds[0]


class AbstractHyperImageFit(AbstractImageFit, AbstractHyperFit):

    def __init__(self, fitting_hyper_images, model_images_, hyper_galaxies):
       """Abstract base class for an regular datas-set which includes hyper noise_map-scaling. Seee *AbstractFitter* and
       *AbstractLensHyperFit* for more details."""
       AbstractHyperFit.__init__(self=self, fitting_hyper_images=fitting_hyper_images, hyper_galaxies=hyper_galaxies)
       super(AbstractHyperImageFit, self).__init__(fitting_images=fitting_hyper_images, model_images_=model_images_)
       self.scaled_chi_squareds_ = fitting_util.chi_squared_map_from_residual_map_mask_and_noise_map(self.residuals_, self.scaled_noise_maps_)


class AbstractConvolutionFit(AbstractImageFit):

    def __init__(self, fitting_images, images_, blurring_images_):
        """Abstract base class for a fit to an regular using a light-profile.

        This includes the blurring of the light-profile model regular with the instrumental PSF.

        Parameters
        -----------
        fitting_images : [fit_data.FitData]
            The fitting unblurred_image_1d that are fitted.
        images_ : [ndarray]
            The masked 1D representation of the light profile model unblurred_image_1d before PSF blurring.
        blurring_images_ : [ndarray]
            The 1D representation of the light profile model unblurred_image_1d blurring region, which corresponds to all pixels \
            which are not inside the masks but close enough that their light will be blurred into it via PSF convolution.
        """

        self.convolvers_image = list(map(lambda fit_image : fit_image.convolver_image, fitting_images))

        model_images_ = fitting_util.blur_image_including_blurring_region(image_=images_, blurring_image_=blurring_images_,
                                                                          convolver=self.convolvers_image)

        super(AbstractConvolutionFit, self).__init__(fitting_images=fitting_images, model_images_=model_images_)


class AbstractInversionFit(AbstractImageFit):

    def __init__(self, fitting_images, mapper, regularization):
        """Abstract base class for a fit to an regular which uses a linear inversion.

        This includes passing the regular / noise_maps / PSF and inversion objects to the inversons module to perform \
        the inversion.

        Parameters
        -----------
        fitting_images : [fit_data.FitData]
            The fitting unblurred_image_1d that are fitted.
        mapper : inversion.mapper.Mapper
            Class storing the mappings between observed regular-pixels and inversion's pixelization pixels.
        regularization : inversion.regularization.Regularization
            Class storing the regularization scheme of the inversion's pixelization.

        Attributes
        -----------
        likelihoods_with_regularization : [float]
            The likelihood of each fit to the regular, including jsut 3 terms, the chi-squared term, regularization
            penalty factor and noise_map normalization term.
        likelihood_with_regularization : float
            The sum of all likelihoods_with_regularization for all unblurred_image_1d.
        evidences : [float]
            The Bayesian evidence of each fit to the regular. The Bayesian evidence is described in Suyu et al. 2006 and
            the howtolens inversion tutorial chapter_4_inversions/tutorial_4_bayesian_regularization.
        evidence : float
            The sum of evidence values for all unblurred_image_1d.
        """

        self.inversion = inversions.inversion_from_image_mapper_and_regularization(
            image_1d=fitting_images[0][:],
            noise_map_1d=fitting_images[0].noise_map_, convolver=fitting_images[0].convolver_mapping_matrix,
            mapper=mapper, regularization=regularization)

        super(AbstractInversionFit, self).__init__(fitting_images=fitting_images,
                                                   model_images_=[self.inversion.reconstructed_data_vector])

    @property
    def likelihoods_with_regularization(self):
        return fitting_util.likelihood_with_regularization_from_chi_squared_term_regularization_and_noise_term(self.chi_squared_terms,
                                                                                                               [self.inversion.regularization_term], self.noise_terms)

    @property
    def likelihood_with_regularization(self):
        return sum(self.likelihoods_with_regularization)

    @property
    def evidences(self):
        return fitting_util.evidence_from_reconstruction_terms(self.chi_squared_terms,
                                                               [self.inversion.regularization_term],
                                                               [self.inversion.log_det_curvature_reg_matrix_term],
                                                               [self.inversion.log_det_regularization_matrix_term],
                                                               self.noise_terms)

    @property
    def evidence(self):
        return sum(self.evidences)


class AbstractConvolutionInversionFit(AbstractImageFit):
    
    def __init__(self, fitting_images, images_, blurring_images_, mapper, regularization):
        
        self.convolvers_image = list(map(lambda fit_image : fit_image.convolver_image, fitting_images))

        self.profile_model_images_ = fitting_util.blur_image_including_blurring_region(image_=images_,
                                                                                       blurring_image_=blurring_images_,
                                                                                       convolver=self.convolvers_image)

        self.profile_subtracted_images_ = list(map(lambda fitting_image, profile_model_image_ :
                                                   fitting_image[:] - profile_model_image_,
                                                   fitting_images, self.profile_model_images_))

        self.inversion = inversions.inversion_from_image_mapper_and_regularization(
            image_1d=self.profile_subtracted_images_[0], noise_map_1d=fitting_images[0].noise_map_,
            convolver=fitting_images[0].convolver_mapping_matrix, mapper=mapper, regularization=regularization)
        
        self.inversion_model_images_ = [self.inversion.reconstructed_data_vector]

        model_images_ = list(map(lambda profile_model_image_, inversion_model_image_ :
                                 profile_model_image_ + inversion_model_image_,
                                 self.profile_model_images_, self.inversion_model_images_))

        super(AbstractConvolutionInversionFit, self).__init__(fitting_images=fitting_images, model_images_=model_images_)

    @property
    def profile_subtracted_images(self):
        return fitting_util.map_arrays_to_scaled_arrays(arrays_=self.profile_subtracted_images_,
                                                        map_to_scaled_arrays=self.map_to_scaled_arrays)

    @property
    def profile_model_images(self):
        return fitting_util.map_arrays_to_scaled_arrays(arrays_=self.profile_model_images_,
                                                        map_to_scaled_arrays=self.map_to_scaled_arrays)

    @property
    def inversion_model_images(self):
        return fitting_util.map_arrays_to_scaled_arrays(arrays_=self.inversion_model_images_,
                                                        map_to_scaled_arrays=self.map_to_scaled_arrays)

    @property
    def profile_subtracted_image(self):
        return self.profile_subtracted_images[0]

    @property
    def profile_model_image(self):
        return self.profile_model_images[0]

    @property
    def inversion_model_image(self):
        return self.inversion_model_images[0]

    @property
    def evidences(self):
        return fitting_util.evidence_from_reconstruction_terms(self.chi_squared_terms, [self.inversion.regularization_term],
                                                               [self.inversion.log_det_curvature_reg_matrix_term],
                                                               [self.inversion.log_det_regularization_matrix_term],
                                                               self.noise_terms)

    @property
    def evidence(self):
        return sum(self.evidences)
