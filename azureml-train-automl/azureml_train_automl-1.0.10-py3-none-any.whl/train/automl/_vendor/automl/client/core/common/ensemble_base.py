# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base module for ensembling previous AutoML iterations."""

import datetime
import numpy as np

from abc import ABC, abstractmethod
from collections import namedtuple
import os
import pickle
from sklearn.base import BaseEstimator
from sklearn.pipeline import make_pipeline

from . import constants
from . import datasets
from . import _ensemble_selector
from . import model_wrappers
from . import logging_utilities as log_utils
from . import metrics


class EnsembleBase(ABC):
    """
    Class for ensembling previous AutoML iterations.

    The ensemble pipeline is initialized from a collection of already fitted pipelines.
    """

    MAXIMUM_MODELS_FOR_SELECTION = 50
    PIPELINES_TUPLES_ITERATION_INDEX = 0
    PIPELINES_TUPLES_ALGORITHM_INDEX = 2
    PIPELINES_TUPLES_CHILD_RUN_INDEX = 3

    def __init__(self, automl_settings):
        """Create an Ensemble pipeline out of a collection of already fitted pipelines.

        :param automl_settings: settings for the AutoML experiments.
        """
        if isinstance(automl_settings, str):
            automl_settings = eval(automl_settings)
        if isinstance(automl_settings, dict):
            # create a type out of the dictionary
            automl_settings = namedtuple("AutoMLSettings", automl_settings.keys())(*automl_settings.values())
        self._automl_settings = automl_settings

    def fit(self, X, y):
        """Fit method not implemented.

        Use the `fit_ensemble` method instead

        Raises:
            NotImplementedError -- Not using this API for ensemble training

        """
        raise NotImplementedError("call fit_ensemble instead")

    def fit_ensemble(self, training_type: constants.TrainingType, dataset: datasets.ClientDatasets, **kwargs):
        """
        Fit the ensemble based on the existing fitted pipelines.

        :param training_type: Type of training (eg: TrainAndValidate split, CrossValidation split, MonteCarlo, etc.)
        :type training_type: constants.TrainingType enumeration
        :param dataset: The training dataset.
        :type dataset: datasets.ClientDatasets
        :return: Returns a fitted ensemble including all the selected models.
        """
        logger = self._get_logger()

        ensemble_iterations = self._automl_settings.ensemble_iterations

        ensemble_run, parent_run = self._get_ensemble_and_parent_run()
        primary_metric = self._automl_settings.primary_metric

        use_cross_validation = False
        if training_type in [constants.TrainingType.CrossValidation, constants.TrainingType.MeanCrossValidation]:
            use_cross_validation = True
            model_artifact_name = constants.MODEL_PATH_TRAIN
        else:
            model_artifact_name = constants.MODEL_PATH
        goal = metrics.minimize_or_maximize(task=self._automl_settings.task_type, metric=primary_metric)
        start = datetime.datetime.utcnow()

        fitted_pipelines = self._fetch_fitted_pipelines(logger, parent_run, model_artifact_name, goal)

        elapsed = datetime.datetime.utcnow() - start
        total_pipelines_for_ensembling = len(fitted_pipelines)
        logger.info("Fetched {} fitted pipelines in {} seconds".format(total_pipelines_for_ensembling,
                                                                       elapsed.seconds))

        if total_pipelines_for_ensembling == 0:
            raise Exception("Didn't download successfully any models for running Ensembling")

        start = datetime.datetime.utcnow()
        selector = _ensemble_selector.EnsembleSelector(logger=logger,
                                                       fitted_models=fitted_pipelines,
                                                       dataset=dataset,
                                                       training_type=training_type,
                                                       metric=primary_metric,
                                                       iterations=ensemble_iterations)

        unique_ensemble, unique_weights = selector.select()
        elapsed = datetime.datetime.utcnow() - start
        logger.info("Selected the pipelines for the ensemble in {0} seconds".format(elapsed.seconds))

        if model_artifact_name == constants.MODEL_PATH:
            ensemble_estimator_tuples = [(fitted_pipelines[i][2], fitted_pipelines[i][1]) for i in unique_ensemble]
        else:
            ensemble_estimator_tuples = self._create_fully_fitted_ensemble_estimator_tuples(logger,
                                                                                            fitted_pipelines,
                                                                                            unique_ensemble)
        self._save_ensemble_metrics(logger, ensemble_run, unique_ensemble, unique_weights, fitted_pipelines)

        self.estimator = self._get_voting_ensemble(dataset, ensemble_estimator_tuples, unique_weights)

        cross_folded_ensembles = None
        if use_cross_validation:
            # for computing all the scores of the Ensemble we'll need the ensembles of cross-validated models.
            cross_folded_ensembles = []
            for fold_index, _ in enumerate(dataset.get_CV_splits()):
                partial_fitted_estimators = [(fitted_pipelines[i][2], fitted_pipelines[i][1][fold_index])
                                             for i in unique_ensemble]
                cross_folded_ensemble = self._get_voting_ensemble(dataset,
                                                                  partial_fitted_estimators,
                                                                  unique_weights)
                cross_folded_ensembles.append(cross_folded_ensemble)
        return self.estimator, cross_folded_ensembles

    def predict(self, X):
        """
        Predicts the target for the provided input.

        :param X: Input test samples.
        :type X: numpy.ndarray or scipy.spmatrix
        :return: Prediction values.
        """
        return self.estimator.predict(X)

    def predict_proba(self, X):
        """
        Return the probability estimates for the input dataset.

        :param X: Input test samples.
        :type X: numpy.ndarray or scipy.spmatrix
        :return: Prediction probabilities values.
        """
        return self.estimator.predict_proba(X)

    def _fetch_fitted_pipelines(self, logger, parent_run, model_artifact_name, goal):
        child_runs = parent_run.get_children()
        # first we'll filter out any other Ensemble iteration models or failed iterations (with score = nan)
        run_scores = []
        for child in child_runs:
            properties = child.get_properties()
            if properties.get('pipeline_id', constants.ENSEMBLE_PIPELINE_ID) == constants.ENSEMBLE_PIPELINE_ID or \
                    properties.get('score', 'nan') == 'nan':
                continue
            run_scores.append((child, float(properties.get('score'))))
        num_models_for_ensemble = min(EnsembleBase.MAXIMUM_MODELS_FOR_SELECTION, len(run_scores))

        sort_reverse_order = False
        if goal == constants.OptimizerObjectives.MAXIMIZE:
            sort_reverse_order = True
        # we'll sort the iterations based on their score from best to worst depending on the goal
        # and then we'll prune the list
        candidates = sorted(run_scores, key=lambda tup: tup[1], reverse=sort_reverse_order)[0:num_models_for_ensemble]
        logger.info("Fetching fitted models for best {0} previous iterations".format(num_models_for_ensemble))

        results = self._download_fitted_models_for_child_runs(logger,
                                                              [run for run, score in candidates],
                                                              model_artifact_name)

        fitted_pipelines = []
        for (child_run, fitted_pipeline, ex) in results:
            if ex is not None:
                logger.warning("Failed to read the fitted model for iteration {0}".format(child_run.id))
                log_utils.log_traceback(ex, logger)
                continue
            properties = child_run.get_properties()
            iteration = int(properties.get('iteration', 0))
            algo_name = properties.get('run_algorithm', 'Unknown')
            fitted_pipelines.append((iteration, fitted_pipeline, algo_name, child_run))
        return fitted_pipelines

    def _download_fitted_models_for_child_runs(self, logger, child_runs, model_remote_path):
        # return result of type tuple(child_run, fitted_pipeline, ex)
        result = []
        for index, run in enumerate(child_runs):
            result.append(EnsembleBase._download_model(run, index, model_remote_path))
        return result

    def _create_fully_fitted_ensemble_estimator_tuples(self, logger, fitted_pipelines, unique_ensemble):
        ensemble_estimator_tuples = []
        # we need to download the fully trained models
        ensemble_child_runs = [fitted_pipelines[index][EnsembleBase.PIPELINES_TUPLES_CHILD_RUN_INDEX]
                               for index in unique_ensemble]
        results = self._download_fitted_models_for_child_runs(logger, ensemble_child_runs, constants.MODEL_PATH)

        for (child_run, fitted_pipeline, ex) in results:
            if ex is not None:
                logger.warning("Failed to read the fully fitted model for iteration {0}".format(child_run.id))
                log_utils.log_traceback(ex, logger)
                continue
            properties = child_run.get_properties()
            algo_name = properties.get('run_algorithm', 'Unknown')
            ensemble_estimator_tuples.append((algo_name, fitted_pipeline))
        return ensemble_estimator_tuples

    @staticmethod
    def _download_model(child_run, index, remote_path):
            # we'll download the model, deserialize it and then remove the temp file afterwards
            try:
                local_model_file = "model_{0}.pkl".format(index)
                child_run.download_file(name=remote_path, output_file_path=local_model_file)
                with open(local_model_file, "rb") as model_file:
                    fitted_pipeline = pickle.load(model_file)
                os.remove(local_model_file)
                if isinstance(fitted_pipeline, list):
                    # for the case of CV split trained pipeline list
                    fitted_pipeline = list([EnsembleBase._transform_single_fitted_pipeline(pip) for pip
                                            in fitted_pipeline])
                else:
                    fitted_pipeline = EnsembleBase._transform_single_fitted_pipeline(fitted_pipeline)
                return child_run, fitted_pipeline, None
            except Exception as e:
                return child_run, None, e

    def _get_voting_ensemble(self, dataset, ensemble_estimator_tuples, unique_weights):
        if self._automl_settings.task_type == constants.Tasks.CLASSIFICATION:
            unique_labels = dataset.get_meta("class_labels")
            estimator = model_wrappers.PreFittedSoftVotingClassifier(estimators=ensemble_estimator_tuples,
                                                                     weights=unique_weights,
                                                                     classification_labels=unique_labels)
        elif self._automl_settings.task_type == constants.Tasks.REGRESSION:
            estimator = model_wrappers.PreFittedSoftVotingRegressor(estimators=ensemble_estimator_tuples,
                                                                    weights=unique_weights)
        else:
            raise ValueError("Invalid task_type ({0})".format(self._automl_settings.task_type))
        return estimator

    def _save_ensemble_metrics(self, logger, ensemble_run, unique_ensemble, unique_weights, fitted_pipelines):
        try:
            chosen_iterations = []
            chosen_algorithms = []
            for index in unique_ensemble:
                chosen_iterations.append(fitted_pipelines[index][EnsembleBase.PIPELINES_TUPLES_ITERATION_INDEX])
                chosen_algorithms.append(fitted_pipelines[index][EnsembleBase.PIPELINES_TUPLES_ALGORITHM_INDEX])
            best_individual_pipeline = fitted_pipelines[0][EnsembleBase.PIPELINES_TUPLES_CHILD_RUN_INDEX]
            ensemble_tags = {}
            str_chosen_iterations = str(chosen_iterations)
            str_chosen_algorithms = str(chosen_algorithms)
            ensemble_tags['ensembled_iterations'] = str_chosen_iterations
            ensemble_tags['ensembled_algorithms'] = str_chosen_algorithms
            ensemble_tags['ensemble_weights'] = str(unique_weights)
            # because the pipelines are sorted based on their score, we can get the best individual iteration easily
            best_individual_score = best_individual_pipeline.get_properties().get('score', 'nan')
            ensemble_tags['best_individual_pipeline_score'] = best_individual_score
            ensemble_run.set_tags(ensemble_tags)
            logger.info("Ensembled iterations: {0}. Ensembled algos: {1}"
                        .format(str_chosen_iterations, str_chosen_algorithms))
        except Exception as ex:
            logger.warning("Failed to save the ensemble metrics into the ensemble iteration object")
            log_utils.log_traceback(ex, logger)

    @staticmethod
    def _transform_single_fitted_pipeline(fitted_pipeline):
        # for performance reasons we'll transform the data only once inside the ensemble,
        # by adding the transformers to the ensemble pipeline (as preprocessor steps, inside automl.py).
        # Because of this, we need to remove any AutoML transformers from all the fitted pipelines here.
        modified_steps = [step[1] for step in fitted_pipeline.steps
                          if step[0] not in constants.Transformers.ALL]
        if len(modified_steps) != len(fitted_pipeline.steps):
            return make_pipeline(*[s for s in modified_steps])
        else:
            return fitted_pipeline

    # abstract methods
    @abstractmethod
    def _get_logger(self):
        pass

    @abstractmethod
    def _get_ensemble_and_parent_run(self):
        pass
