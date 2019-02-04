# -*- coding: utf-8 -*-

"""
<ENTER DESCRIPTION HERE>
"""

import json
import os
import random
import sys
import time
from abc import abstractmethod
from typing import List, Dict, Union
from k_util import pather
from k_util.logger import Logger

from raid.data.interface.i_dataset import IDataset
from raid.data.interface.i_sample import ISample
from raid.logic.checkpoint import Checkpoint
from raid.logic.config import Config
from raid.logic.limit_type import LimitType
from raid.logic.metric import Metric
from raid.visual.plotter import Plotter

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class Trainer:

    # Default keys for config values.
    C_BATCH_SIZE: str = "batch_size"
    C_BALANCED_SHUFFLE: str = "balanced_shuffle"
    C_RANDOM_SEED: str = "random_seed"

    # Default metric keys.
    M_LOSS: str = "loss"
    M_VALIDATION: str = "validation"

    def __init__(self, config: Config):

        if config is None:
            config = Config({})

        # Session Runtime Variables.
        self.batch_size: int = config(self.C_BATCH_SIZE, default=1)
        self.balanced_shuffle: bool = config(self.C_BALANCED_SHUFFLE, default=True)
        self.random_seed: Union[int, None] = config(self.C_RANDOM_SEED, default=None)

        self.validation_set: IDataset = None

        # Metric Logging.
        self.metrics: Dict[str, Metric] = {}

        # Checkpoints.
        self._output_dir: str = "output"
        self.session_id: str = "default_session"
        self.checkpoint = None

    def set_session_data(self, session_id: str, output_dir: str):
        self._output_dir: str = output_dir
        self.session_id: str = session_id

    def reset(self):
        """ Reset the state of the trainer. """
        self.metrics = {}

    # ===================================================================================================
    # Helpers.
    # ===================================================================================================

    @property
    def output_dir(self):
        """ Save loose files for the whole trainer process. """
        pather.create(self._output_dir)
        return self._output_dir

    @property
    def artifact_dir(self):
        """ Save loose files for the whole trainer process. """
        path = os.path.join(self.output_dir, "artifacts")
        pather.create(path)
        return path

    def get_model_path(self, model_name: str):
        path = os.path.join(self.output_dir, "models", model_name)
        pather.create(path)
        return path

    # ===================================================================================================
    # Abstract Methods. Must implement.
    # ===================================================================================================

    @abstractmethod
    def step(self, data_batch: List[ISample]) -> float:
        """ Implement this step function. Forward, calculate loss, step the optimizer
        and return the loss. """
        return random.random()

    @abstractmethod
    def validate(self, validation_set: IDataset) -> float:
        return random.random()

    @abstractmethod
    def save(self, path: str):
        with open(path, "w") as f:
            f.write("Hello World")

    # ===================================================================================================
    # Don't need to implement these, but could be helpful.
    # ===================================================================================================

    def preprocess(self, training_set: IDataset) -> IDataset:
        return training_set

    def on_checkpoint_activate(
            self,
            index: int,
            duration: float,
            sample_count: int,
            validation_set: IDataset):
        pass

    # ===================================================================================================
    # ...
    # ===================================================================================================

    def start_session(
            self,
            training_set: IDataset,
            validation_set: IDataset,
            limit_number: float = 10,
            limit_type: LimitType = LimitType.EPOCHS,
            cp_interval_number: float = 1,
            cp_interval_type: LimitType = LimitType.EPOCHS
    ):
        # Create the Checkpoint Manager.
        self.checkpoint: Checkpoint = Checkpoint(
            self._activate_checkpoint,
            cp_interval_number,
            cp_interval_type,
            limit_number,
            limit_type
        )

        # Create checkpoint object.
        checkpoint = self.checkpoint

        # Ref. the validation set for later use.
        self.validation_set = validation_set

        # Preprocess the training set.
        training_set = self.preprocess(training_set)
        if training_set is None or type(training_set) != IDataset:
            raise Exception(f"Preprocess method must return a training set (IDataset)!")

        # Prepare to batch.
        batch_count = training_set.get_batch_count(self.batch_size)

        # Set the epoch to some large number, unless we are training by epoch.
        epochs = int(limit_number + 1) if limit_type == LimitType.EPOCHS else sys.maxsize

        for e in range(1, epochs):
            Logger.header(f"Begin Epoch {e}")
            training_set.shuffle(seed=self.random_seed, balanced=self.balanced_shuffle)
            for batch_index in range(batch_count):
                data_batch = training_set.get_batch(batch_index, self.batch_size)

                # Count each sample that we train.
                for sample in data_batch:
                    checkpoint.register_samples_trained(sample.semantic_labels)

                loss = self.step(data_batch)
                self.add_rolling_metric(self.M_LOSS, loss)

                # End of Step: Timer based CP Activation.
                checkpoint.step(epoch_gain=0)
                if checkpoint.has_completed(e - 1):  # This line also updates the progress.
                    break

            # End of Epoch: Epoch based CP Activation.
            checkpoint.step(epoch_gain=1)
            if checkpoint.has_completed(e - 1):  # This line also updates the progress.
                break

        Logger.log("Activate Final Checkpoint")
        checkpoint.update_progress(epochs)
        checkpoint.activate()
        Logger.log(f"Session: {self.session_id} Complete")

    # ===================================================================================================
    #
    # ===================================================================================================

    def _activate_checkpoint(self, checkpoint: Checkpoint):

        # End the training timer.
        checkpoint.training_end_time = time.time()

        # Validate.
        self.validation_set.shuffle()
        val_start_time = time.time()
        validation_score = self.validate(self.validation_set)
        checkpoint.validation_time = time.time() - val_start_time
        checkpoint.validation_time_per_sample = checkpoint.validation_time / len(self.validation_set)

        # Arbitrary Functions.
        self.on_checkpoint_activate(checkpoint.index, checkpoint.duration, 0, self.validation_set)

        # Auto-save all the best models.
        self._auto_save(checkpoint, validation_score)

        # Write the metrics to disk.
        self._update_metrics(checkpoint)

    def _update_metrics(self, checkpoint):
        # Draw Metrics.
        Plotter.render_metrics(self.metrics, self.output_dir)
        # Export Metric Log
        self.export_metrics()
        self.export_checkpoint_log(checkpoint)

    def _auto_save(self, checkpoint, validation_score):
        # Save Models.
        loss = self.aggregate_metric(self.M_LOSS)
        is_best_loss = checkpoint.register_loss(loss)
        if is_best_loss:
            self.save(self.get_model_path("model_best_loss.pt"))
        self.add_metric(self.M_VALIDATION, validation_score)
        is_best_validation = checkpoint.register_validation(validation_score)
        if is_best_validation:
            self.save(self.get_model_path("model_best_validation.pt"))
        # Save the latest model as well.
        self.save(self.get_model_path("model_latest.pt"))

    def export_metrics(self):
        metric_path = os.path.join(self.output_dir, "metrics.json")
        data = {k: m.aggregate_history for k, m in self.metrics.items()}
        with open(metric_path, "w") as f:
            json.dump(data, f, indent=2)

    def export_checkpoint_log(self, checkpoint: Checkpoint):
        log_path = os.path.join(self.output_dir, "checkpoint_log.json")
        data = {
            "session": self.session_id,
            "progress": checkpoint.progress,
            "total_duration": checkpoint.duration,
            "best_loss": checkpoint.best_loss,
            "best_validation": checkpoint.best_validation,
            "training_duration": checkpoint.training_duration,
            "training_time_per_sample": checkpoint.training_duration / max(1, checkpoint.n_samples_trained),
            "validation_duration": checkpoint.validation_time,
            "validation_time_per_sample": checkpoint.validation_time_per_sample,
        }

        with open(log_path, "w") as f:
            json.dump(data, f, indent=2)

        log_path = os.path.join(self.output_dir, "samples_trained_log.json")
        with open(log_path, "w") as f:
            json.dump(checkpoint.samples_trained_map, f, indent=2)

    # ===================================================================================================
    # Training Support Functions.
    # ===================================================================================================

    def declare_metric(self, title: str, capacity: int=100):
        self.metrics[title] = Metric(title, capacity)

    def add_rolling_metric(self, title: str, value: float):
        """ Log an arbitrary metric"""
        self.get_metric(title).add_short(value)

    def add_metric(self, title: str, value: float):
        """ Log an arbitrary metric"""
        self.get_metric(title).add_fixed(value)

    def get_metric(self, title: str):
        if title not in self.metrics:
            self.declare_metric(title)
        return self.metrics[title]

    def aggregate_metric(self, title: str):
        metric = self.get_metric(title)
        return metric.aggregate()
