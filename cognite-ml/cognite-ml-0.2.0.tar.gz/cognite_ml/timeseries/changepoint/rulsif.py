#!/usr/bin/env python
# -*- coding: utf-8 -*-
# original source code made available under the Mozilla Public License 2.0
# https://github.com/paolodedios/shift-detect

"""
Relative Unconstrained Least Squares Importance Fitting algorithm
"""
from __future__ import print_function

import numpy as np
from scipy import linalg


class GaussianKernel:
    """
    Computes the n-dimensional Gaussian kernel/RBF matrix

    K(X,Y) = exp( -(|| X - Y ||^2) / (2 * sigma^2) )

    for X the data matrix of sample points
    and Y the matrix of Gaussian centers.
    """

    sigma_width = None

    def __init__(self, sigma=1.0):
        self.sigma_width = sigma

    def compute_distance(self, samples=None, sample_means=None):
        """
        Compute the distances between points in the sample's feature space
        to points along the center of the distribution
        """
        (sample_rows, sample_cols) = samples.shape
        (mean_rows, mean_cols) = sample_means.shape

        squared_samples = sum(samples ** 2, 0)
        squared_means = sum(sample_means ** 2, 0)

        return (
            np.tile(squared_means, (sample_cols, 1))
            + np.tile(squared_samples[:, None], (1, mean_cols))
            - 2 * np.dot(samples.T, sample_means)
        )

    def apply(self, samples=None, sample_means=None):
        """
        Computes an n-dimensional Gaussian/RBF kernel matrix by taking points
        in the sample's feature space and maps them to kernel coordinates in
        Hilbert space by calculating the distance to each point in the sample
        space and taking the Gaussian function of the distances.

           K(X,Y) = exp( -(|| X - Y ||^2) / (2 * sigma^2) )

        where X is the matrix of data points in the sample space,
              Y is the matrix of gaussian centers in the sample space
             sigma is the width of the gaussian function being used
        """
        squared_distance = self.compute_distance(samples, sample_means)

        return np.exp(-squared_distance / (2 * (self.sigma_width ** 2)))


class AlphaRelativeDensityRatioEstimator:
    """
    Computes the alpha-relative density ratio estimate of P(X_ref) and P(X_test)

    The alpha-relative density ratio estimator, r_alpha(X), is given by the
    following kernel model:

    g(X; theta) = SUM( (theta_l * K(X, X_centers_l)), l=0, n )

    where theta is a vector of parameters [theta_1, theta_2, ..., theta_l]^T
    to be learned from the data samples. The parameters theta in the model
    g(X; theta) is calculated by solving the following optimization problem:

      theta_hat = argmin [ ( (1/2) * theta^T * H_hat * theta) -
                    (h_hat^T * theta) + ( lambda/2 * theta^T * theta) ]

    where the expression (lamba/2 * theta^T * theta), with lambda >= 0, is
    a regularization term used to penalize against overfitting

    Reference:
    Relative Density-Ratio Estimation for Robust Distribution Comparison. Makoto Yamada,
    Taiji Suzuki, Takafumi Kanamori, Hirotaka Hachiya, and Masashi Sugiyama. NIPS,
    page 594-602. (2011)
    """

    alpha_constraint = None
    sigma_width = None
    lambda_regularizer = None
    kernel_basis = None

    def __init__(self, alpha_constraint=0.0, sigma_width=1.0, lambda_regularizer=0.0, kernel_basis=1):
        self.alpha_constraint = alpha_constraint
        self.sigma_width = sigma_width
        self.lambda_regularizer = lambda_regularizer
        self.kernel_basis = kernel_basis

    def apply(self, reference_samples=None, test_samples=None, gaussian_centers=None):
        """
        Computes the alpha-relative density ratio, r_alpha(X), of P(X_ref) and P(X_test)

          r_alpha(X) = P(Xref) / (alpha * P(Xref) + (1 - alpha) * P(X_test)

        Returns density ratio estimate at X_ref, r_alpha_ref, and at X_test, r_alpha_test
        """
        # Apply the kernel function to the reference and test samples
        K_ref = GaussianKernel(self.sigma_width).apply(reference_samples, gaussian_centers).T
        K_test = GaussianKernel(self.sigma_width).apply(test_samples, gaussian_centers).T

        # Compute the parameters, theta_hat, of the density ratio estimator
        H_hat = AlphaRelativeDensityRatioEstimator.H_hat(self.alpha_constraint, K_ref, K_test)
        h_hat = AlphaRelativeDensityRatioEstimator.h_hat(K_ref)
        theta_hat = AlphaRelativeDensityRatioEstimator.theta_hat(
            H_hat, h_hat, self.lambda_regularizer, self.kernel_basis
        )

        # Estimate the density ratio, r_alpha_ref = r_alpha(X_ref)
        r_alpha_ref = AlphaRelativeDensityRatioEstimator.g_of_X_theta(K_ref, theta_hat).T
        # Estimate the density ratio, r_alpha_test = r_alpha(X_test)
        r_alpha_test = AlphaRelativeDensityRatioEstimator.g_of_X_theta(K_test, theta_hat).T

        return (r_alpha_ref, r_alpha_test)

    @staticmethod
    def H_hat(alpha=0.0, kernel_matrix_reference_samples=None, kerne_matrix_test_samples=None):
        """
        Calculates the H_hat term of the theta_hat
        optimization problem.
        """
        N_ref = kernel_matrix_reference_samples.shape[1]
        N_test = kerne_matrix_test_samples.shape[1]

        H_hat = (alpha / N_ref) * np.dot(kernel_matrix_reference_samples, kernel_matrix_reference_samples.T) + (
            (1.0 - alpha) / N_test
        ) * np.dot(kerne_matrix_test_samples, kerne_matrix_test_samples.T)

        return H_hat

    @staticmethod
    def h_hat(kernel_matrix_reference_samples):
        """
        Calculates the h_hat term of the theta_hat optimization problem
        """
        h_hat = np.mean(kernel_matrix_reference_samples, 1)

        return h_hat

    @staticmethod
    def theta_hat(H_hat=None, h_hat=None, lambda_regularizer=0.0, kernel_basis=None):
        """
        Calculates theta_hat given H_hat, h_hat, lambda, and the kernel basis function
        Treat as a system of lienar equations and find the exact, optimal
        solution
        """
        theta_hat = linalg.solve(H_hat + (lambda_regularizer * np.eye(kernel_basis)), h_hat)

        return theta_hat

    @staticmethod
    def J_of_theta(alpha=0.0, g_X_ref_theta=None, g_X_test_theta=None):
        """
        Calculates the squared error criterion, J
        """
        return (
            (alpha / 2.0) * (np.mean(g_X_ref_theta ** 2))
            + ((1 - alpha) / 2.0) * (np.mean(g_X_test_theta ** 2))
            - np.mean(g_X_ref_theta)
        )

    @staticmethod
    def g_of_X_theta(kernel_matrix_samples=None, theta_hat=None):
        """
        Calculate the alpha-relative density ratio kernel model
        """
        return np.dot(kernel_matrix_samples.T, theta_hat)


class PearsonRelativeDivergenceEstimator:
    """
    Calculates the alpha-relative Pearson divergence score

    The alpha-relative Pearson divergence is given by the following expression:

      PE_alpha = -(alpha/2(n_ref)) * SUM(r_alpha(X_ref_i)^2, i=0, n_ref)        -
                  ((1-alpha)/2(n_test)) * SUM(r_alpha(X_test_j)^2, j=0, n_test) +
                  (1/n_ref) * SUM(r_alpha(X_ref_i), i=0, n_ref)                 -
                  1/2

    where r_alpha(X) is the alpha-relative density ratio estimator and is given by
    the following kernel model:

      g(X; theta) = SUM( (theta_l * K(X, X_centers_l)), l=0, n )

    Reference:
    Relative Density-Ratio Estimation for Robust Distribution Comparison. Makoto
    Yamada, Taiji Suzuki, Takafumi Kanamori, Hirotaka Hachiya, and Masashi Sugiyama.
    NIPS, page 594-602. (2011)
    """

    alpha_constraint = None
    sigma_width = None
    lambda_regularizer = None
    kernel_basis = None

    def __init__(self, alpha_constraint=0.0, sigma_width=1.0, lambda_regularizer=0.0, kernel_basis=1):
        self.alpha_constraint = alpha_constraint
        self.sigma_width = sigma_width
        self.lambda_regularizer = lambda_regularizer
        self.kernel_basis = kernel_basis

    def apply(self, reference_samples=None, test_samples=None, gaussian_centers=None):
        """
        Calculates the alpha-relative Pearson divergence score
        """
        density_ratio_estimator = AlphaRelativeDensityRatioEstimator(
            self.alpha_constraint, self.sigma_width, self.lambda_regularizer, self.kernel_basis
        )

        # Estimate alpha relative density ratio and pearson divergence score
        (r_alpha_X_ref, r_alpha_X_test) = density_ratio_estimator.apply(
            reference_samples, test_samples, gaussian_centers
        )

        PE_divergence = (
            np.mean(r_alpha_X_ref)
            - (
                0.5
                * (
                    self.alpha_constraint * np.mean(r_alpha_X_ref ** 2)
                    + (1.0 - self.alpha_constraint) * np.mean(r_alpha_X_test ** 2)
                )
            )
            - 0.5
        )

        return (PE_divergence, r_alpha_X_test)


class RULSIF:
    """
    Estimates the alpha-relative Pearson Divergence via Least Squares Relative
    Density Ratio Approximation

    Reference:
    Relative Density-Ratio Estimation for Robust Distribution Comparison. Makoto
    Yamada, Taiji Suzuki, Takafumi Kanamori, Hirotaka Hachiya, and Masashi Sugiyama.
    NIPS, page 594-602. (2011)
    """

    alpha_constraint = None
    sigma_width = None
    lambda_regularizer = None
    kernel_basis = None
    cross_folds = None
    gaussian_centers = None

    def __init__(self, alpha_constraint=0.0, sigma_width=1.0, lambda_regularizer=0.0, kernel_basis=100, cross_folds=5):

        self.alpha_constraint = alpha_constraint
        self.sigma_width = sigma_width
        self.lambda_regularizer = lambda_regularizer
        self.kernel_basis = kernel_basis
        self.cross_folds = cross_folds
        self.gaussian_centers = None

    def get_median_distance_between_samples(self, sample_set=None):
        """
        Jaakkola's heuristic method for setting the width parameter of the Gaussian
        radial basis function kernel is to pick a quantile (usually the median) of
        the distribution of Euclidean distances between points having different
        labels.

        Reference:
        Jaakkola, M. Diekhaus, and D. Haussler. Using the Fisher kernel method to detect
        remote protein homologies. In T. Lengauer, R. Schneider, P. Bork, D. Brutlad, J.
        Glasgow, H.- W. Mewes, and R. Zimmer, editors, Proceedings of the Seventh
        International Conference on Intelligent Systems for Molecular Biology.
        """
        numrows = sample_set.shape[0]
        samples = sample_set

        G = np.sum((samples * samples), 1)
        Q = np.tile(G[:, np.newaxis], (1, numrows))
        R = np.tile(G, (numrows, 1))

        distances = Q + R - 2 * np.dot(samples, samples.T)
        distances = distances - np.tril(distances)
        distances = distances.reshape(numrows ** 2, 1, order="F").copy()

        return np.sqrt(0.5 * np.median(distances[distances > 0]))

    def compute_gaussian_width_candidates(self, reference_samples=None, test_samples=None):
        """
        Compute a candidate list of Gaussian kernel widths. The best width will be
        selected via cross-validation
        """
        all_samples = np.c_[reference_samples, test_samples]
        median_distance = self.get_median_distance_between_samples(all_samples.T)

        return median_distance * np.array([0.6, 0.8, 1, 1.2, 1.4])

    def generate_regularization_params(self):
        """
        Generatees a candidate list of regularization parameters to be used
        with the L1 regularizer term of RULSIF optimization problem.  The
        best regularizer parameter will be chosen via cross-validation
        """
        return 10.0 ** np.array([-3, -2, -1, 0, 1])

    def generate_all_gaussian_centers(self, reference_samples=None):
        """
        Generates kernels in the region where the P(X_reference) takes large values
        """
        self.kernel_basis = reference_samples.shape[1]

        return reference_samples[:, np.r_[0 : self.kernel_basis]]

    def generate_random_gaussian_centers(self, reference_samples=None):
        """
        Randomly chooses Gaussian centers as an optimization
        """
        numcols = reference_samples.shape[1]
        reference_sample_idxs = np.random.permutation(numcols)
        self.kernel_basis = min(self.kernel_basis, numcols)

        return reference_samples[:, reference_sample_idxs[0 : self.kernel_basis]]

    def generate_first_N_gaussian_centers(self, reference_samples=None):
        """
        Chooses the firts N samples as Gaussian centers as an optimization
        """
        numcols = reference_samples.shape[1]
        self.kernel_basis = min(self.kernel_basis, numcols)

        return reference_samples[:, np.r_[0 : self.kernel_basis]]

    def generate_gaussian_centers(self, reference_samples=None):
        """
        Choose Gaussian centers based on a strategy
        """
        # gaussianCenters = self.generateAllGaussianCenters(referenceSamples)
        gaussian_centers = self.generate_random_gaussian_centers(reference_samples)

        return gaussian_centers

    def compute_model_parameters(self, reference_samples=None, test_samples=None, gaussian_centers=None):
        """
        Computes model parameters via k-fold cross validation process
        """
        (ref_rows, ref_cols) = reference_samples.shape
        (test_rows, test_cols) = test_samples.shape

        sigma_widths = self.compute_gaussian_width_candidates(reference_samples, test_samples)
        lambda_candidates = self.generate_regularization_params()

        # Initialize cross validation scoring matrix
        cross_validation_scores = np.zeros((np.size(sigma_widths), np.size(lambda_candidates)))

        # Initialize a cross validation index assignment list
        reference_samples_cv_idxs = np.random.permutation(ref_cols)
        reference_samples_cv_split = np.floor(np.r_[0:ref_cols] * self.cross_folds / ref_cols)
        test_samples_cv_idxs = np.random.permutation(test_cols)
        test_samples_cv_split = np.floor(np.r_[0:test_cols] * self.cross_folds / test_cols)

        # Initiate k-fold cross-validation procedure. Using variable
        # notation similar to the RULSIF formulas.
        for sigma_idx in np.r_[0 : np.size(sigma_widths)]:

            # (re-)Calculate the kernel matrix using the candidate sigma width
            sigma = sigma_widths[sigma_idx]
            K_ref = GaussianKernel(sigma).apply(reference_samples, gaussian_centers).T
            K_test = GaussianKernel(sigma).apply(test_samples, gaussian_centers).T

            # Initialize a new result matrix for the current sigma candidate
            fold_result = np.zeros((self.cross_folds, np.size(lambda_candidates)))

            for fold_idx in np.r_[0 : self.cross_folds]:

                K_ref_training_set = K_ref[:, reference_samples_cv_idxs[reference_samples_cv_split != fold_idx]]
                K_test_training_set = K_test[:, test_samples_cv_idxs[test_samples_cv_split != fold_idx]]

                H_h_kth_fold = AlphaRelativeDensityRatioEstimator.H_hat(
                    self.alpha_constraint, K_ref_training_set, K_test_training_set
                )
                h_h_kth_fold = AlphaRelativeDensityRatioEstimator.h_hat(K_ref_training_set)

                for lambda_idx in np.r_[0 : np.size(lambda_candidates)]:
                    lambda_candidate = lambda_candidates[lambda_idx]

                    theta_h_kth_fold = AlphaRelativeDensityRatioEstimator.theta_hat(
                        H_h_kth_fold, h_h_kth_fold, lambda_candidate, self.kernel_basis
                    )

                    # Select the subset of the kernel matrix not used in the training set
                    # for use as the test set to validate against
                    k_ref_test_set = K_ref[:, reference_samples_cv_idxs[reference_samples_cv_split == fold_idx]]
                    k_test_test_set = K_test[:, test_samples_cv_idxs[test_samples_cv_split == fold_idx]]

                    r_alpha_X_ref = AlphaRelativeDensityRatioEstimator.g_of_X_theta(k_ref_test_set, theta_h_kth_fold)
                    r_alpha_X_test = AlphaRelativeDensityRatioEstimator.g_of_X_theta(k_test_test_set, theta_h_kth_fold)

                    # Calculate the objective function J(theta) under the current parameters
                    J = AlphaRelativeDensityRatioEstimator.J_of_theta(
                        self.alpha_constraint, r_alpha_X_ref, r_alpha_X_test
                    )

                    fold_result[fold_idx, lambda_idx] = J

                cross_validation_scores[sigma_idx, :] = np.mean(fold_result, 0)

        cross_validation_min_scores = cross_validation_scores.min(1)
        cross_validation_min_idx_for_lambda = cross_validation_scores.argmin(1)
        cross_validation_min_idx_for_sigma = cross_validation_min_scores.argmin()

        optimal_sigma = sigma_widths[cross_validation_min_idx_for_sigma]
        optimal_lambda = lambda_candidates[cross_validation_min_idx_for_lambda[cross_validation_min_idx_for_sigma]]

        return (optimal_sigma, optimal_lambda)

    def fit(self, reference_samples=None, test_samples=None):
        """
        Learn the proper model parameters
        """

        # Reset RNG to ensure consistency of experimental results.  In a production
        # environment, the RNG should use a truly random seed and hyper-parameters
        np.random.seed(0)

        gaussian_centers = self.generate_gaussian_centers(reference_samples)

        (optimal_sigma, optimal_lambda) = self.compute_model_parameters(
            reference_samples, test_samples, gaussian_centers
        )

        self.sigma_width = optimal_sigma
        self.lambda_regularizer = optimal_lambda
        self.gaussian_centers = gaussian_centers

    def predict(self, reference_samples=None, test_samples=None):
        """
        Estimates the alpha-relative Pearson divergence as determined by the relative
        ratio of probability densities:

           P(ReferenceSamples[x]) / (alpha * P(ReferenceSamples[x]) + (1 - alpha) * P(TestSamples[x]))

        from samples:
           ReferenceSamples[x_i] | ReferenceSamples[x_i] in R^{d}, with i=1 to ReferenceSamples{N}

        drawn independently from P(ReferenceSamples[x])

        and from samples:
           TestSamples[x_j] | TestSamples[x_j] in R^{d}, with j=1 to TestSamples{N}

        drawn independently from P(TestSamples[x])

        After the model hyper-parameters have been learned and chosen by the train()
        method, the RULSIF algorithm can be applied repeatedly on both in-sample and out
        of sample data
        """

        if self.gaussian_centers is None or self.kernel_basis is None:
            raise Exception("Missing kernel basis function parameters")

        if self.sigma_width == 0.0 or self.lambda_regularizer == 0.0:
            raise Exception("Missing model selection parameters")

        divergence_estimator = PearsonRelativeDivergenceEstimator(
            self.alpha_constraint, self.sigma_width, self.lambda_regularizer, self.kernel_basis
        )
        (PE_alpha, r_alpha_X_test) = divergence_estimator.apply(reference_samples, test_samples, self.gaussian_centers)

        return PE_alpha
