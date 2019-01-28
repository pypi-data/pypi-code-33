# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class for running experiments."""
import copy
import datetime
import json
import logging
import signal
import time
import traceback

import numpy as np
import scipy
import sklearn.pipeline

from automl.client.core.common import logging_utilities as log_utils
from automl.client.core.common import constants
from automl.client.core.common import metrics as mt
from automl.client.core.common import resource_limits
from automl.client.core.common.constants import (Sample_Weights_Unsupported,
                                                 Tasks, TrainingResultsType,
                                                 TrainingType)
from automl.client.core.common.resource_limits import (default_resource_limits,
                                                       safe_enforce_limits)


class ClientRunner(object):
    """Runner which encapsulates the fit() method for various AutoML models."""

    def __init__(self,
                 datasets,
                 metrics=None,
                 run_as_spawn=True,
                 task=constants.Tasks.CLASSIFICATION,
                 log_config=None):
        """
        Construct the ClientRunner.

        :param datasets: A ClientDatasets object.
        :param metrics: The metric that AutoML will optimize for model selection.
        :param run_as_spawn: If uses the limit_function_call_spawn as resource limitation method.
        :param task: string, 'classification' or 'regression'
        """
        assert task in ['classification', 'regression']
        self.task = task

        if metrics is None:
            metrics = mt.get_scalar_metrics(self.task)

        self.metrics = metrics
        self.datasets = datasets
        self.run_as_spawn = run_as_spawn

        self._log_config = log_config

    def time_fit(self, m, X, y, sample_weight=None):
        """
        Run the fit and calculate the time elapsed.

        :param m: The model to run the fit.
        :param X: Input data.
        :param y: Target values.
        :param sample_weight: Sample weights for training data.
        :return: The time elapsed for fit.
        """
        t = datetime.datetime.utcnow()  # time.process_time()
        kwargs = {}
        if sample_weight is not None:
            # get model's name in steps array
            clf = m.steps[-1][0]
            if clf not in Sample_Weights_Unsupported:
                # pipeline expects kwargs to be formatted as stepname__arg.
                # The arg is then passed to fit of stepname
                kwargs = {clf + "__sample_weight": sample_weight}
        m.fit(X, y.ravel(), **kwargs)
        elapsed_time = datetime.datetime.utcnow() - t

        return elapsed_time.total_seconds()

    def _run_train_valid(self, dataset, pipeline_spec,
                         problem_info,
                         random_state=None):
        """
        Run the training and validation.

        :param dataset: The ClientDatasets object used for the run.
        :param pipeline_spec: The PipelineSpec object used for the run.
        :return: A dictionary of metric name -> score, fit time and the instantiated pipeline.
        """
        X_train, y_train, sample_weight_train = dataset.get_train_set()
        X_valid, y_valid, _ = dataset.get_valid_set()

        pipeline = pipeline_spec.instantiate_pipeline_spec(
            problem_info, random_state=random_state, is_sparse=dataset.get_is_sparse())

        fit_time = self.time_fit(
            pipeline, X_train, y_train, sample_weight=sample_weight_train)
        score_valid = self._compute_metrics(X_valid, y_valid, y_train,
                                            pipeline, dataset,
                                            sample_weight=sample_weight_train)
        return score_valid, fit_time, pipeline

    def _run_train_full(self, dataset, pipeline_spec,
                        problem_info,
                        random_state=None):
        """
        Run the full training.

        :param dataset: The ClientDatasets object used for the run.
        :param pipeline_spec: The PipelineSpec object used for the run.
        :return: A dictionary of metric name -> score, fit time and the instantiated pipeline.
        """
        if dataset.has_training_set():
            X_train, y_train, sample_weight_train = dataset.get_train_set()
            X_valid, y_valid, sample_weight_valid = dataset.get_valid_set()
            X_full = (
                scipy.sparse.vstack((X_train, X_valid))
                if scipy.sparse.issparse(X_train)
                else np.concatenate((X_train, X_valid)))
            y_full = np.concatenate((y_train, y_valid))

            if sample_weight_valid is not None:
                sample_weight_full = np.concatenate(
                    (sample_weight_train, sample_weight_valid))
            else:
                sample_weight_full = None
        else:
            X_full, y_full, sample_weight_full = dataset.get_full_set()

        pipeline = pipeline_spec.instantiate_pipeline_spec(
            problem_info, random_state=random_state, is_sparse=dataset.get_is_sparse())

        fit_time = self.time_fit(
            pipeline, X_full, y_full, sample_weight=sample_weight_full)

        score_full = self._compute_metrics(X_full, y_full, None,
                                           pipeline, dataset,
                                           sample_weight=sample_weight_full)

        return score_full, fit_time, pipeline

    def _run_cv(self, dataset, pipeline_spec, problem_info,
                random_state=None):
        """
        Run the fit of given pipeline spec with CV splits of the input dataset.

        :param dataset: The ClientDatasets object used for the run.
        :param pipeline_spec: The PipelineSpec object used for the run.
        :param problem_info: The ProblemInfo object used for the run.
        :param random_state: RandomState instance or None, optional, default = None.
        :return: Dictionaries of metric name -> score, fit times and the instantiated pipelines.
        """
        scores = []
        fit_times = []
        models = []

        for X_train, y_train, sample_wt_train, X_test, y_test, \
                sample_wt_test in dataset.get_CV_splits():
            m = pipeline_spec.instantiate_pipeline_spec(
                problem_info, random_state=random_state, is_sparse=dataset.get_is_sparse())

            fit_time = self.time_fit(m, X_train, y_train, sample_wt_train)
            score = self._compute_metrics(X_test, y_test, y_train,
                                          m, dataset,
                                          sample_weight=sample_wt_test)

            scores.append(score)
            fit_times.append(fit_time)
            models.append(m)
        return scores, fit_times, models

    def _run_cv_mean(self, dataset, pipeline_spec, problem_info,
                     cv_results=None,
                     random_state=False):
        """
        Run the fit to get the mean of scores and fit time, with CV splits of the input dataset.

        :param dataset: The ClientDatasets object used for the run.
        :param pipeline_spec: The PipelineSpec object used for the run.
        :param problem_info: The ProblemInfo object used for the run.
        :param cv_results: The result of a _run_cv method.
        :param random_state: RandomState instance or None, optional, default = None.
        :return: Mean values of the scores and fit times, and the instantiated pipelines.
        """
        if cv_results is None:
            scores, fit_times, fit_models = self._run_cv(
                dataset, pipeline_spec, problem_info,
                random_state=random_state)
        else:
            scores, fit_times, fit_models = cv_results

        mean_scores = mt.compute_mean_cv_scores(scores, self.metrics)
        mean_fit_time = float(np.mean(fit_times))
        return mean_scores, mean_fit_time, fit_models

    def _run(self, dataset, pipeline_spec, problem_info, sets_to_run,
             subsample_percent=None, random_state=None, include_models=False,
             subsample_seed=0):
        """
        Run the fit with different purpose with specific run sets.

        :param dataset: A dataset generated by ClientDatasets.parse_data().
        :param pipeline_spec: A pipeline specification (obtained from the API).
        :param problem_info: A ProblemInfo object.
        :param sets_to_run: Which experiment types to run (e.g. CV,
            train_valid, etc).
        :param subsample_percent: A multiple of 5 between 5 and 100, inclusive.
        :param random_state: int or RandomState object to seed random
            operations.
        :param include_models:
        :return: train, validation, and test scores for the experiments
            specified in sets_to_run.
        """
        results = {TrainingResultsType.MODELS: {}}
        training_percent = subsample_percent or problem_info.training_percent
        if training_percent is not None and training_percent < 100:
            # train on a subset of the training dataset.
            results[TrainingResultsType.TRAIN_PERCENT] = training_percent
            dataset = dataset.get_subsampled_dataset(
                training_percent, random_state=subsample_seed)
        else:
            results[TrainingResultsType.TRAIN_PERCENT] = 100

        if constants.TrainingType.TrainAndValidation in sets_to_run:
            results[TrainingResultsType.TRAIN_VALIDATE_STATUS] = 0
            try:
                score_full, train_time, fit_model = self._run_train_valid(
                    dataset, pipeline_spec, problem_info,
                    random_state=random_state)
                results[TrainingResultsType.VALIDATION_METRICS] = score_full
                results[TrainingResultsType.MODELS][
                    constants.TrainingType.TrainAndValidation] = fit_model
                results[TrainingResultsType.VALIDATION_METRICS][
                    TrainingResultsType.TRAIN_TIME] = train_time
            except ValueError:
                results[TrainingResultsType.TRAIN_VALIDATE_STATUS] = \
                    traceback.format_exc()
                results[TrainingResultsType.VALIDATION_METRICS] = None

        if constants.TrainingType.TrainValidateTest in sets_to_run:
            results[TrainingResultsType.TRAIN_VALIDATE_STATUS] = 0

            X_train, y_train, sample_weight_train = dataset.get_train_set()
            try:
                score_full, train_time, fit_model = self._run_train_valid(
                    dataset, pipeline_spec, problem_info,
                    random_state=random_state)
                results[TrainingResultsType.VALIDATION_METRICS] = score_full
                results[TrainingResultsType.MODELS][
                    constants.TrainingType.TrainValidateTest] = fit_model
                scores = self._compute_metrics(X_train, y_train, None,
                                               fit_model, dataset,
                                               sample_weight=sample_weight_train)
                results[TrainingResultsType.TRAIN_METRICS] = scores
                results[TrainingResultsType.TRAIN_METRICS][
                    TrainingResultsType.TRAIN_TIME] = train_time

                X_test, y_test, sample_weight_test = dataset.get_test_set()
                scores = self._compute_metrics(X_test, y_test, None,
                                               fit_model, dataset,
                                               sample_weight=sample_weight_test)
                results[TrainingResultsType.TEST_METRICS] = scores
            except ValueError as e:
                results[TrainingResultsType.TRAIN_VALIDATE_STATUS] = \
                    traceback.format_exc()
                results[TrainingResultsType.VALIDATION_METRICS] = None
                results[TrainingResultsType.TRAIN_METRICS] = None
                results[TrainingResultsType.TEST_METRICS] = None

        if constants.TrainingType.TrainFull in sets_to_run:
            results[TrainingResultsType.TRAIN_FULL_STATUS] = 0
            try:
                score_full, train_time, fit_model = self._run_train_full(
                    dataset, pipeline_spec, problem_info,
                    random_state=random_state)

                results[TrainingResultsType.MODELS][
                    constants.TrainingType.TrainFull] = fit_model
                results[TrainingResultsType.TRAIN_FROM_FULL_METRICS] = score_full
                results[TrainingResultsType.TRAIN_FROM_FULL_METRICS][
                    TrainingResultsType.TRAIN_TIME] = train_time

                if dataset.has_test_set():
                    X_test, y_test, sample_weight_test = dataset.get_test_set()
                    scores = self._compute_metrics(X_test, y_test, None,
                                                   fit_model, dataset,
                                                   sample_weight=sample_weight_test)
                    results[TrainingResultsType.TEST_FROM_FULL_METRICS] = scores
            except ValueError as e:
                results[TrainingResultsType.TRAIN_FULL_STATUS] = \
                    traceback.format_exc()
                results[TrainingResultsType.TRAIN_FROM_FULL_METRICS] = None
                results[TrainingResultsType.TEST_FROM_FULL_METRICS] = None

        if (constants.TrainingType.CrossValidation in sets_to_run or
                constants.TrainingType.MeanCrossValidation in sets_to_run):
            results[TrainingResultsType.CV_STATUS] = 0
            try:
                scores, fit_times, fit_model = self._run_cv(
                    dataset, pipeline_spec, problem_info,
                    random_state=random_state)
                results[TrainingResultsType.MODELS][
                    constants.TrainingType.CrossValidation] = fit_model
                for i in range(len(scores)):
                    score = scores[i]
                    fit_time = fit_times[i]
                    score[TrainingResultsType.TRAIN_TIME] = fit_time
                results[TrainingResultsType.CV_METRICS] = scores

                mean_scores, mean_time, fit_model = self._run_cv_mean(
                    dataset, pipeline_spec, problem_info,
                    cv_results=(scores, fit_times, fit_model))

                results[TrainingResultsType.CV_MEAN_METRICS] = mean_scores
                results[TrainingResultsType.CV_MEAN_METRICS][
                    TrainingResultsType.TRAIN_TIME] = mean_time
            except ValueError as e:
                results[TrainingResultsType.CV_STATUS] = \
                    traceback.format_exc()
                results[TrainingResultsType.CV_MEAN_METRICS] = None
                results[TrainingResultsType.CV_METRICS] = None

        if not include_models:
            del results[TrainingResultsType.MODELS]

        return results

    def _compute_metrics(self, X_valid, y_valid, y_train,
                         model, dataset, sample_weight=None):
        """Compute the metrics.

        Wrapper for compute_metrics_classification and compute_metrics_regression
        Branches are based on the task and get the appropriate parameters needed
        to compute metrics from the dataset.
        :param X_valid: The inputs to test/compute metrics.
        :param y_valid: The targets to test/compute metrics.
        :param y_train: The targets to train the model.
        :param model: The model to make predictions.
        :param dataset: ClientDataset object that contains information
            about the dataset (see datasets.py).
        :param sample_weight: The weights for each sample to use when computing the
            score for each metric.
        :return: A dictionary of metric name -> score.
        """
        y_pred = self._predict(self.task, model, X_valid)

        if self._log_config is None:
            logger = log_utils.NULL_LOGGER
        else:
            filename, verbosity, namespace = self._log_config.get_params()
            logger = log_utils.get_logger(namespace, filename, verbosity)

        if self.task == Tasks.CLASSIFICATION:
            num_classes = dataset.get_num_classes()
            class_labels = dataset.get_class_labels()
            y_transformer = dataset.get_y_transformer()
            trained_labels = self._get_trained_labels(model, y_train)

            return mt.compute_metrics_classification(
                y_pred, y_valid, metrics=self.metrics,
                class_labels=class_labels,
                trained_class_labels=trained_labels,
                num_classes=num_classes,
                y_transformer=y_transformer,
                sample_weight=sample_weight,
                logger=logger)
        elif self.task == Tasks.REGRESSION:
            y_min, y_max = dataset.get_y_range()
            y_std = dataset.get_y_std()
            bin_info = dataset.get_bin_info()

            return mt.compute_metrics_regression(
                y_pred, y_valid, metrics=self.metrics,
                y_min=y_min, y_max=y_max, y_std=y_std,
                bin_info=bin_info,
                sample_weight=sample_weight,
                logger=logger)
        else:
            raise NotImplementedError

    def _predict(self, task, model, X_valid):
        """
        Return predictions from the given model with a provided task type.

        :param task: The task type (see constants.py).
        :param model: The model used to make predictions.
        :param X_valid: The inputs on which to predict.
        :return: The predictions of the model on X_valid
            The shape of the array returned depends on the task type
            Classification will return probabilities for each class.
        """
        if task == Tasks.CLASSIFICATION:
            return model.predict_proba(X_valid)
        elif task == Tasks.REGRESSION:
            return model.predict(X_valid)
        else:
            raise NotImplementedError

    def _get_trained_labels(self, model, y_train):
        """
        Return the class labels that a model has been trained on.

        Sometimes a model is only trained on a subset of the class labels from
        the dataset. This is especially common with cross validation and
        custom validation sets. This function returns the class labels that
        a model has been trained on.
        If the model is a regression model the function returns np.unique of y_train,
        but this function shouldn't be used for regression
        :param model: The model used to make predictions.
        :param y_train: Targets used during model training.
        :return: The labels used when training the model.
        """
        if hasattr(model, "classes_"):
            return model.classes_
        elif y_train is not None:
            return np.unique(y_train)
        else:
            return None

    def _run_as_subprocess(self, fn, constraints, *args, **kwargs):
        pynobj = safe_enforce_limits(run_as_spawn=self.run_as_spawn, **constraints)
        result = pynobj(fn)(*args, **kwargs)
        return result, pynobj.exit_status

    def _run_in_process(self, fn, constraints, *args, **kwargs):
        return fn(*args, **kwargs), 0

    def _run_prewrap(self, fn, dataset, pipeline_spec, problem_info,
                     enforce_limits=True, **kwargs):
        """Handle clearing the constraints and selecting to run in a subprocess or not."""
        c = problem_info.runtime_constraints
        if pipeline_spec.supports_constrained_fit():
            c = resource_limits.default_resource_limits
            enforce_limits = False

        args = (dataset, pipeline_spec, problem_info)
        wrapper = (self._run_as_subprocess if enforce_limits else
                   self._run_in_process)
        return wrapper(fn, c, *args, **kwargs)

    def run(self, dataset, pipeline_spec, problem_info, sets_to_run=None,
            subsample_percent=None, enforce_limits=True,
            new_constraints=None, is_ensemble_iteration=False,
            random_state=None, include_models=False, subsample_seed=0):
        """
        Run the specific run task.

        :param dataset:
        :param pipeline_spec: A pipeline specification (obtained from the API).
            Not to be confused with a sklearn Pipeline object.
        :param problem_info:
        :param sets_to_run:
        :param subsample_percent:
        :param enforce_limits: If true, run in a subprocess.
        :param new_constraints:
        :param is_ensemble_iteration: bool to indicate whether
            it is an ensemble iteration
        :param random_state: random_state for random operations
        :param include_models:
        :param subsample_seed: a int for seeding subsample operations
        :return: A dict of results, filled in with TrainingResultsType keys.
        """
        if is_ensemble_iteration:
            return self.run_ensembling(
                dataset, pipeline_spec, problem_info,
                sets_to_run[0] if sets_to_run
                else TrainingType.TrainAndValidation)

        if sets_to_run is None:
            sets_to_run = list(constants.TrainingType.FULL_SET)

        kwargs = {'sets_to_run': sets_to_run,
                  'subsample_percent': subsample_percent,
                  'random_state': random_state,
                  'subsample_seed': subsample_seed,
                  'include_models': include_models}
        return self._run_prewrap(
            self._run, dataset, pipeline_spec, problem_info,
            enforce_limits=enforce_limits, **kwargs)

    def run_ensembling(self, dataset, pipeline_spec,
                       problem_info, training_type):
        """
        Run the ensemble selection & generates an Estimator out of the chosen pipelines.

        :param dataset: The input dataset which is used for the ensemble selection.
        :param pipeline: The Ensemble pipeline to fit.
        :param training_type: The type of training used.
        """
        # disable safe_enforce_limits until LightGBM hanging bug is fixed
        # pynobj = safe_enforce_limits(**self.runtime_constraints)
        result = self._run_ensembling_internal(dataset,
                                               pipeline_spec,
                                               problem_info,
                                               training_type)
        return result, 0

    def _run_ensembling_internal(self, dataset, pipeline_spec,
                                 problem_info, training_type):
        pipeline = pipeline_spec.instantiate_pipeline_spec(
            problem_info, is_sparse=dataset.get_is_sparse())

        fit_time, fitted_ensemble_model, cross_validated_ensembles = \
            self.time_fit_ensemble(pipeline, training_type, dataset)
        fitted_pipeline = sklearn.pipeline.make_pipeline(fitted_ensemble_model)
        if training_type == TrainingType.TrainAndValidation:
            _, y_train, _ = dataset.get_train_set()
            X_valid, y_valid, sample_weight_valid = dataset.get_valid_set()
            score_valid = self._compute_metrics(X_valid, y_valid, y_train,
                                                fitted_pipeline, dataset,
                                                sample_weight=sample_weight_valid)
        elif training_type == TrainingType.MeanCrossValidation:
            fold_index = 0
            scores = []
            for _, y_train, _, X_test, y_test, sample_wt_test in dataset.get_CV_splits():
                m = cross_validated_ensembles[fold_index]
                score = self._compute_metrics(X_test, y_test, y_train,
                                              m, dataset,
                                              sample_weight=sample_wt_test)
                scores.append(score)
                fold_index += 1
            score_valid = mt.compute_mean_cv_scores(scores, self.metrics)
        return score_valid, fit_time, fitted_pipeline

    def time_fit_ensemble(self, m, training_type, dataset):
        """
        Run the ensemble fit of the given model.

        :param m: The model to run the fit.
        :param X: Input data.
        :param y: Target values.
        :return: Elapsed time in seconds, the fitted ensemble with all the selected models.
        """
        t = datetime.datetime.utcnow()  # time.process_time()
        fitted_ensemble_model, cv_ensembles = m._final_estimator.fit_ensemble(
            training_type, dataset)
        elapsed_time = datetime.datetime.utcnow() - t
        return elapsed_time.seconds, fitted_ensemble_model, cv_ensembles


if __name__ == '__main__':
    pass
