# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines helpful utilities for summarizing and uploading data."""

import os
import scipy as sp
import shap
from math import ceil
import json
import io

from azureml._restclient.constants import RUN_ORIGIN
from azureml.explain.model._internal.common import module_logger
from azureml.explain.model._internal.constants import History, IO
from azureml._logging import ChainedIdentity
from sklearn.utils.sparsefuncs import csc_median_axis_0


def summarize_data(X, k=10, to_round_values=True):
    """Summarize a dataset.

    For dense dataset, use k mean samples weighted by the number of data points they
    each represent.
    For sparse dataset, use a sparse row for the background with calculated
    median for dense columns.

    :param X: Matrix of data samples to summarize (# samples x # features).
    :type X: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
    :param k: Number of cluster centroids to use for approximation.
    :type k: int
    :param to_round_values: When using kmeans, for each element of every cluster centroid to match the nearest value
        from X in the corresponding dimension. This ensures discrete features
        always get a valid value.  Ignored for sparse data sample.
    :type to_round_values: bool
    :return: DenseData or SparseData object.
    :rtype: iml.datatypes.DenseData or iml.datatypes.SparseData
    """
    from shap.common import DenseData
    is_sparse = sp.sparse.issparse(X)
    if not isinstance(X, DenseData):
        if is_sparse:
            module_logger.debug('Creating sparse data summary as csr matrix')
            # calculate median of sparse background data
            median_dense = csc_median_axis_0(X.tocsc())
            return sp.sparse.csr_matrix(median_dense)
        elif len(X) > 10 * k:
            module_logger.debug('Create dense data summary with k-means')
            # use kmeans to summarize the examples for initialization
            # if there are more than 10 x k of them
            return shap.kmeans(X, k, to_round_values)
    return X


def _get_dense_examples(examples):
    if sp.sparse.issparse(examples):
        module_logger.debug('converting sparse examples to regular array')
        return examples.toarray()
    return examples


def _convert_to_list(shap_values):
    module_logger.debug('converting numpy array of list of numpy array to list')
    classification = isinstance(shap_values, list)
    if classification:
        # shap_values is a list of ndarrays
        shap_values_numpy_free = []
        for array in shap_values:
            shap_values_numpy_free.append(array.tolist())
        return shap_values_numpy_free
    else:
        # shap_values is a single ndarray
        return shap_values.tolist()


class ArtifactUploader(ChainedIdentity):
    """A class for uploading explanation data to run history."""

    def __init__(self, run, max_num_blocks=None, block_size=None, **kwargs):
        """Initialize the upload mixin by setting up the storage policy."""
        self.storage_policy = {History.MAX_NUM_BLOCKS: 3, History.BLOCK_SIZE: 100}
        self._update_storage_policy(max_num_blocks, block_size)
        super(ArtifactUploader, self).__init__(**kwargs)
        self._logger.debug('Initializing ArtifactUploader')
        self.run = run

    def _update_storage_policy(self, max_num_blocks, block_size):
        if max_num_blocks is not None:
            self.storage_policy[History.MAX_NUM_BLOCKS] = max_num_blocks
        if block_size is not None:
            self.storage_policy[History.BLOCK_SIZE] = block_size

    def _create_upload_dir(self):
        self._logger.debug('Creating upload directory')
        # create the outputs folder
        upload_dir = './explanation/'
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir

    def _upload_artifact(self, upload_dir, artifact_name, values):
        self._logger.debug('Uploading artifact')
        try:
            json_string = json.dumps(values)
            stream = io.BytesIO(json_string.encode(IO.UTF8))
            self.run.upload_file('{}{}.json'.format(upload_dir.lstrip('./'), artifact_name), stream)
        except ValueError as exp:
            self._logger.error('Cannot serialize numpy arrays as JSON')

    def _get_num_of_blocks(self, num_of_columns):
        block_size = self.storage_policy[History.BLOCK_SIZE]
        num_blocks = ceil(num_of_columns / block_size)
        max_num_blocks = self.storage_policy[History.MAX_NUM_BLOCKS]
        if num_blocks > max_num_blocks:
            num_blocks = max_num_blocks
        return num_blocks

    def _get_model_summary_artifacts(self, upload_dir, name, summary):
        self._logger.debug('Uploading model summary')
        num_columns = summary.shape[len(summary.shape) - 1]
        num_blocks = self._get_num_of_blocks(num_columns)
        block_size = self.storage_policy[History.BLOCK_SIZE]
        storage_metadata = {
            History.NAME: name,
            History.MAX_NUM_BLOCKS: self.storage_policy[History.MAX_NUM_BLOCKS],
            History.BLOCK_SIZE: self.storage_policy[History.BLOCK_SIZE],
            History.NUM_FEATURES: num_columns,
            History.NUM_BLOCKS: num_blocks
        }
        artifacts = [{} for _ in range(num_blocks)]
        # Chunk the summary and save it to Artifact
        start = 0
        for idx in range(num_blocks):
            if idx == num_blocks - 1:
                # on last iteration, grab everything that's left for the last block
                cols = slice(start, num_columns)
            else:
                cols = slice(start, start + block_size)
            block = summary[..., cols]
            block_name = '{}_{}'.format(name, str(idx))
            self._logger.debug('Uploading artifact for block: {}'.format(block_name))
            self._upload_artifact(upload_dir, block_name, block.tolist())
            artifacts[idx][History.PREFIX] = os.path.normpath('{}/{}/{}/{}'.format(RUN_ORIGIN,
                                                                                   self.run.id,
                                                                                   upload_dir,
                                                                                   block_name))
            start += block_size
        return artifacts, storage_metadata
