
from .AbstractEstimator import AbstractEstimator
import numpy as np
import scipy.linalg as la
from ..Norms import frobenius_norm_squared


class LinearShrinkageEstimator(AbstractEstimator):

    def __init__(self):
        super().__init__()

    def get_lse_alpha_oracle(self, sample_estimator_eigenvalues, sample_estimator_eigenvectors, C):

        n_iter, N = sample_estimator_eigenvalues.shape
        beta_squared_oracle_arr = np.zeros(n_iter)
        delta_squared_oracle_arr = np.zeros(n_iter)

        mu_oracle = C.trace() / N
        alpha_squared_oracle = frobenius_norm_squared(C - mu_oracle * np.eye(N))

        for it in range(n_iter):
            S = sample_estimator_eigenvectors[it] @ \
                np.diag(sample_estimator_eigenvalues[it]) @ \
                sample_estimator_eigenvectors[it].T
            beta_squared_oracle_arr[it] = frobenius_norm_squared(S - C)
            delta_squared_oracle_arr[it] = frobenius_norm_squared(S - mu_oracle * np.eye(N))

        beta_squared_oracle = beta_squared_oracle_arr.mean()
        delta_squared_oracle = delta_squared_oracle_arr.mean()

        alpha_1_oracle = mu_oracle * beta_squared_oracle / delta_squared_oracle
        alpha_2_oracle = alpha_squared_oracle / delta_squared_oracle

        return alpha_1_oracle, alpha_2_oracle

    def get_lse_alpha_bonafide(self, sample_estimator_eigenvalues, sample_estimator_eigenvectors, time_series_array):

        n_iter, N, T = time_series_array.shape

        mu_bonafide_arr = sample_estimator_eigenvalues.mean(axis=1).reshape(n_iter, 1)
        delta_squared_bonafide_arr = ((sample_estimator_eigenvalues - mu_bonafide_arr) ** 2).mean(axis=1)

        beta_tilde_squared_bonafide_summands_arr = np.zeros((n_iter, T))
        for it in range(n_iter):
            S = sample_estimator_eigenvectors[it] @ \
                np.diag(sample_estimator_eigenvalues[it]) @ \
                sample_estimator_eigenvectors[it].T
            for a in range(T):
                X_cols = time_series_array[it, :, a].reshape((N, 1)) @ time_series_array[it, :, a].reshape((N, 1)).T
                beta_tilde_squared_bonafide_summands_arr[it, a] = frobenius_norm_squared(S - X_cols)
        beta_tilde_squared_bonafide_arr = beta_tilde_squared_bonafide_summands_arr.sum(axis=1) / (T ** 2)
        beta_squared_bonafide_arr = np.minimum(beta_tilde_squared_bonafide_arr, delta_squared_bonafide_arr)

        alpha_squared_bonafide_arr = delta_squared_bonafide_arr - beta_squared_bonafide_arr

        mu_bonafide = mu_bonafide_arr.mean()
        delta_squared_bonafide = delta_squared_bonafide_arr.mean()
        beta_squared_bonafide = beta_squared_bonafide_arr.mean()
        alpha_squared_bonafide = alpha_squared_bonafide_arr.mean()

        alpha_1_bonafide = mu_bonafide * beta_squared_bonafide / delta_squared_bonafide
        alpha_2_bonafide = alpha_squared_bonafide / delta_squared_bonafide

        return alpha_1_bonafide, alpha_2_bonafide

    def estimate_eigenvalues(self, sample_estimator_eigenvalues, alpha1, alpha2, verbose=False):
        return alpha1 * np.ones_like(sample_estimator_eigenvalues) + alpha2 * sample_estimator_eigenvalues
