# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines a helpful dataset wrapper to allow operations such as summarizing data, taking the subset or sampling."""

import pandas as pd
import scipy as sp
import numpy as np
from ..common.explanation_utils import summarize_data
from azureml.explain.model._internal.common import module_logger
from azureml.explain.model._internal.constants import Defaults


class DatasetWrapper(object):
    """A wrapper around a dataset to make dataset operations more uniform across explainers."""

    def __init__(self, dataset):
        """Initialize the dataset wrapper.

        :param dataset: A matrix of feature vector examples (# examples x # features) for
            initializing the explainer.
        :type dataset: numpy.array or pandas.DataFrame or iml.datatypes.DenseData or
            scipy.sparse.csr_matrix
        """
        self._features = None
        dataset_is_df = isinstance(dataset, pd.DataFrame)
        dataset_is_series = isinstance(dataset, pd.Series)
        if dataset_is_df or dataset_is_series:
            self._features = dataset.columns.values.tolist()
            dataset = dataset.values
        self._dataset = dataset
        self._original_dataset = dataset
        self._summary_dataset = None
        self._subset_taken = False
        self._summary_computed = False

    @property
    def dataset(self):
        """Get the dataset.

        :return: The underlying dataset.
        :rtype: numpy.array or iml.datatypes.DenseData or scipy.sparse.csr_matrix
        """
        return self._dataset

    @property
    def original_dataset(self):
        """Get the original dataset prior to performing any operations.

        Note: if the original dataset was a pandas dataframe, this will return the numpy version.

        :return: The original dataset.
        :rtype: numpy.array or iml.datatypes.DenseData or scipy.sparse.csr_matrix
        """
        return self._original_dataset

    @property
    def summary_dataset(self):
        """Get the summary dataset without any subsetting.

        :return: The original dataset or None if summary was not computed.
        :rtype: numpy.array or iml.datatypes.DenseData or scipy.sparse.csr_matrix
        """
        return self._summary_dataset

    def get_features(self, features=None, explain_subset=None, **kwargs):
        """Get the features of the dataset if None on current kwargs.

        :return: The features of the dataset if currently None on kwargs.
        :rtype: list
        """
        if features is not None:
            if explain_subset is not None:
                return np.array(features)[explain_subset].tolist()
            return features
        if explain_subset is not None and self._features is not None:
            return np.array(self._features)[explain_subset].tolist()
        return self._features

    def compute_summary(self, nclusters=10, **kwargs):
        """Summarizes the dataset if it hasn't been summarized yet."""
        if self._summary_computed:
            return
        self._summary_dataset = summarize_data(self._dataset, nclusters)
        self._dataset = self._summary_dataset
        self._summary_computed = True

    def take_subset(self, explain_subset):
        """Take a subset of the dataset if not done before.

        :param explain_subset: A list of column indexes to take from the original dataset.
        :type explain_subset: list
        """
        if self._subset_taken:
            return
        # Edge case: Take the subset of the summary in this case,
        # more optimal than recomputing the summary!
        from shap.common import DenseData
        explain_subset = np.array(explain_subset)
        if isinstance(self._dataset, DenseData):
            group_names = np.array(self._dataset.group_names)[explain_subset].tolist()
            self._dataset = DenseData(self._dataset.data[:, explain_subset], group_names)
        else:
            self._dataset = self._dataset[:, explain_subset]
        self._subset_taken = True

    def _reduce_examples(self, max_dim_clustering=Defaults.MAX_DIM):
        """Reduces the dimensionality of the examples if dimensionality is higher than max_dim_clustering.

        If the dataset is sparse, we mean-scale the data and then run
        truncated SVD to reduce the number of features to max_dim_clustering.  For dense
        dataset, we also scale the data and then run PCA to reduce the number of features to
        max_dim_clustering.
        This is used to get better clustering results in _find_k.

        :param max_dim_clustering: Dimensionality threshold for performing reduction.
        :type max_dim_clustering: int
        """
        from sklearn.decomposition import TruncatedSVD, PCA
        from sklearn.preprocessing import StandardScaler
        num_cols = self._dataset.shape[1]
        # Run PCA or SVD on input data and reduce to about MAX_DIM features prior to clustering
        components = min(max_dim_clustering, num_cols)
        reduced_examples = self._dataset
        if components != num_cols:
            if sp.sparse.issparse(self._dataset):
                module_logger.debug('Reducing sparse data with StandardScaler and TruncatedSVD')
                normalized_examples = StandardScaler(with_mean=False).fit_transform(self._dataset)
                reducer = TruncatedSVD(n_components=components)
            else:
                module_logger.debug('Reducing normal data with StandardScaler and PCA')
                normalized_examples = StandardScaler().fit_transform(self._dataset)
                reducer = PCA(n_components=components)
            module_logger.info('reducing dimensionality to {} components for clustering'.format(str(components)))
            reduced_examples = reducer.fit_transform(normalized_examples)
        return reduced_examples

    def _find_k_kmeans(self, max_dim_clustering=Defaults.MAX_DIM):
        """Use k-means to downsample the examples.

        Starting from k_upper_bound, cuts k in half each time and run k-means
        clustering on the examples.  After each run, computes the
        silhouette score and stores k with highest silhouette score.
        We use optimal k to determine how much to downsample the examples.

        :param max_dim_clustering: Dimensionality threshold for performing reduction.
        :type max_dim_clustering: int
        """
        from sklearn.cluster import KMeans
        from sklearn.metrics import silhouette_score
        from math import log, isnan, ceil
        reduced_examples = self._reduce_examples(max_dim_clustering)
        num_rows = self._dataset.shape[0]
        k_upper_bound = 2000
        k_list = []
        k = min(num_rows / 2, k_upper_bound)
        for i in range(int(ceil(log(num_rows, 2) - 7))):
            k_list.append(int(k))
            k /= 2
        prev_highest_score = -1
        prev_highest_index = 0
        opt_k = int(k)
        for k_index, k in enumerate(k_list):
            module_logger.info('running KMeans with k: {}'.format(str(k)))
            km = KMeans(n_clusters=k).fit(reduced_examples)
            clusters = km.labels_
            num_clusters = len(set(clusters))
            k_too_big = num_clusters <= 1
            if k_too_big or num_clusters == reduced_examples.shape[0]:
                score = -1
            else:
                score = silhouette_score(reduced_examples, clusters)
            if isnan(score):
                score = -1
            module_logger.info('KMeans silhouette score: {}'.format(str(score)))
            # Find k with highest silhouette score for optimal clustering
            if score >= prev_highest_score and not k_too_big:
                prev_highest_score = score
                prev_highest_index = k_index
        opt_k = k_list[prev_highest_index]
        module_logger.info('best silhouette score: {}'.format(str(prev_highest_score)))
        module_logger.info('found optimal k for KMeans: {}'.format(str(opt_k)))
        return opt_k

    def _find_k_hdbscan(self, max_dim_clustering=Defaults.MAX_DIM):
        """Use hdbscan to downsample the examples.

        We use optimal k to determine how much to downsample the examples.

        :param max_dim_clustering: Dimensionality threshold for performing reduction.
        :type max_dim_clustering: int
        """
        import hdbscan
        num_rows = self._dataset.shape[0]
        reduced_examples = self._reduce_examples(max_dim_clustering)
        hdbs = hdbscan.HDBSCAN(min_cluster_size=2).fit(reduced_examples)
        clusters = hdbs.labels_
        opt_k = len(set(clusters))
        clustering_threshold = 5
        samples = opt_k * clustering_threshold
        module_logger.info(('found optimal k for hdbscan: {},'
                            ' will use clustering_threshold * k for sampling: {}').format(str(opt_k), str(samples)))
        return min(samples, num_rows)

    def sample(self, max_dim_clustering=Defaults.MAX_DIM, sampling_method=Defaults.HDBSCAN):
        """Sample the examples.

        First does random downsampling to upper_bound rows,
        then tries to find the optimal downsample based on how many clusters can be constructed
        from the data.  If sampling_method is hdbscan, uses hdbscan to cluster the
        data and then downsamples to that number of clusters.  If sampling_method is k-means,
        uses different values of k, cutting in half each time, and chooses the k with highest
        silhouette score to determine how much to downsample the data.
        The danger of using only random downsampling is that we might downsample too much
        or too little, so the clustering approach is a heuristic to give us some idea of
        how much we should downsample to.

        :param max_dim_clustering: Dimensionality threshold for performing reduction.
        :type max_dim_clustering: int
        :param sampling_method: Method to use for sampling, can be 'hdbscan' or 'kmeans'.
        :type sampling_method: str
        """
        from sklearn.utils import resample
        # bounds are rough estimates that came from manual investigation
        lower_bound = 200
        upper_bound = 10000
        num_rows = self._dataset.shape[0]
        module_logger.info('sampling examples')
        # If less than lower_bound rows, just return the full dataset
        if num_rows < lower_bound:
            return self._dataset
        # If more than upper_bound rows, sample randomly
        elif num_rows > upper_bound:
            module_logger.info('randomly sampling to 10k rows')
            self._dataset = resample(self._dataset, n_samples=upper_bound, random_state=7)
            num_rows = upper_bound
        if sampling_method == Defaults.HDBSCAN:
            try:
                opt_k = self._find_k_hdbscan(max_dim_clustering)
            except Exception as ex:
                module_logger.warning(('Failed to use hdbscan due to error: {}'
                                      '\nEnsure hdbscan is installed with: pip install hdbscan').format(str(ex)))
                opt_k = self._find_k_kmeans(max_dim_clustering)
        else:
            opt_k = self._find_k_kmeans(max_dim_clustering)
        # Resample based on optimal number of clusters
        if (opt_k < num_rows):
            self._dataset = resample(self._dataset, n_samples=opt_k, random_state=7)
        return self._dataset
