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
from typing import List, Dict
from k_util import pather
from k_util.logger import Logger

from raid.data.interface.i_dataset import IDataset
from raid.data.interface.i_sample import ISample
from raid.engine.checkpoint import Checkpoint
from raid.engine.limit_type import LimitType
from raid.engine.metric import Metric
from raid.visual.plotter import Plotter

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class Trainer:

    K_MAX_FILE_LIMIT: int = 10  # How many files to store in a history.

    # Default keys for config values.
    C_BATCH_SIZE: str = "batch_size"

    # Default metric keys.
    M_LOSS: str = "loss"
    M_VALIDATION: str = "validation"

    def __init__(self):

        # Config Loading.
        self._tmp_config_data: dict = None  # Tmp storage of config values provided.
        self._tmp_config_hit: dict = None  # TMP storage of config values used.
        self._tmp_config_miss: dict = None  # TMP storage of config values used.

        # Session Runtime Variables.
        self.batch_size: int = 1
        self._tmp_validation_set: IDataset = None

        # Metric Logging.
        self.metrics: Dict[str, Metric] = {}

        # Checkpoints.
        self.output_dir: str = "output"
        self.session_id: str = "default_session"
        self.checkpoint = None

    def reset(self):
        """ Reset the state of the trainer. """
        self.metrics = {}

    # ===================================================================================================
    # Helpers.
    # ===================================================================================================

    @property
    def session_dir(self):
        """ Save loose files for the whole trainer process. """
        path = os.path.join(self.output_dir, self.session_id)
        pather.create(path)
        return path

    @property
    def artifact_dir(self):
        """ Save loose files for the whole trainer process. """
        path = os.path.join(self.session_dir, "artifacts")
        pather.create(path)
        return path

    def get_model_path(self, model_name: str):
        path = os.path.join(self.session_dir, "models", model_name)
        pather.create(path)
        return path

    # ===================================================================================================
    # Abstract Methods.
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
    def save_model(self, path: str):
        with open(path, "w") as f:
            f.write("Hello World")

    @abstractmethod
    def on_load_config(self):
        """ Load the config. It is a dict-mapping of key to value pairs. """
        self.batch_size = self.get(self.C_BATCH_SIZE, self.batch_size)

    @abstractmethod
    def on_checkpoint_hit(self, index: int, duration: float, sample_count: int):
        pass

    # ===================================================================================================
    # Config Loading.
    # ===================================================================================================

    def load_config(self, config: dict):
        # TODO: Maybe we can do this with closure/decorator for cleaner code.
        # Empty Configuration
        if config is None:
            config = {}

        # Initialize the tmp maps.
        self._tmp_config_data = config
        self._tmp_config_hit = {}
        self._tmp_config_miss = {}

        # Subclass call to load the config.
        self.on_load_config()
        self._generate_config_summary()

        # Clear the tmp maps.
        self._tmp_config_data = None
        self._tmp_config_hit = None
        self._tmp_config_miss = None

    def _generate_config_summary(self):
        """ Print the hit/miss results from loading the config. """
        self._show_config_value_list("Config Values Loaded", self._tmp_config_hit)
        self._show_config_value_list("Config Values Missing", self._tmp_config_miss)

        # Also write the results to the artifact folder.
        config_path = os.path.join(self.artifact_dir, "config_summary.json")
        data = {
            "config_loaded": self._tmp_config_hit,
            "config_missing": self._tmp_config_miss
        }
        with open(config_path, "w") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def _show_config_value_list(title: str, config_map: dict):
        Logger.header(title)
        if len(config_map) == 0:
            Logger.indent()
            Logger.log("None")
        else:
            for k, v in config_map.items():
                Logger.field(k, v)

    def get(self, key: str, default=None):
        """ Get some data from the config map. """
        if self._tmp_config_data is None:
            raise Exception("You can only use trainer's get() function inside on_load_config().")

        if key in self._tmp_config_data:
            self._tmp_config_hit[key] = self._tmp_config_data[key]
            return self._tmp_config_data[key]
        else:
            self._tmp_config_miss[key] = default
            return default

    # ===================================================================================================
    # ...
    # ===================================================================================================

    def start_session(
            self,
            title: str,
            config: dict,
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
        checkpoint = self.checkpoint

        self.load_config(config)
        self._tmp_validation_set = validation_set

        # Sort the batches.
        batch_count = training_set.get_batch_count(self.batch_size)
        sample_max = batch_count * self.batch_size

        # Set the epoch to some large number, unless we are training by epoch.
        epochs = int(limit_number + 1) if limit_type == LimitType.EPOCHS else sys.maxsize

        for e in range(1, epochs):
            Logger.header(f"Begin Epoch {e}")
            training_set.shuffle()
            for batch_index in range(batch_count):
                data_batch = training_set.get_batch(batch_index, self.batch_size)

                loss = self.step(data_batch)
                self.add_short_metric(self.M_LOSS, loss)

                # End of Step: Timer based CP Activation.
                checkpoint.step(epoch_gain=0)
                if checkpoint.has_completed(e - 1):  # This line also updates the progress.
                    break

            # End of Epoch: Epoch based CP Activation.
            checkpoint.step(epoch_gain=1)

        Logger.log("Activate Final Checkpoint")
        checkpoint.update_progress(epochs)
        checkpoint.activate()

        Logger.log("Training Complete")

    # ===================================================================================================
    #
    # ===================================================================================================

    def _activate_checkpoint(self, checkpoint: Checkpoint):

        # Validate.
        self._tmp_validation_set.shuffle()
        validation_score = self.validate(self._tmp_validation_set)

        # Arbitrary Functions.
        self.on_checkpoint_hit(checkpoint.index, checkpoint.duration, 0)

        # Save Models.
        loss = self.aggregate_metric(self.M_LOSS)
        is_best_loss = checkpoint.register_loss(loss)
        if is_best_loss:
            self.save_model(self.get_model_path("model_best_loss.pt"))

        self.add_fixed_metric(self.M_VALIDATION, validation_score)
        is_best_validation = checkpoint.register_validation(validation_score)
        if is_best_validation:
            self.save_model(self.get_model_path("model_best_validation.pt"))

        # Save the latest model as well.
        self.save_model(self.get_model_path("model_latest.pt"))

        # Draw Metrics.
        Plotter.render_metrics(self.metrics, self.session_dir)

        # Export Metric Log
        self.export_metrics()

        self.export_checkpoint_log(checkpoint)

    def export_metrics(self):
        metric_path = os.path.join(self.session_dir, "metrics.json")
        data = {k: m.aggregate_history for k, m in self.metrics.items()}
        with open(metric_path, "w") as f:
            json.dump(data, f, indent=2)

    def export_checkpoint_log(self, checkpoint: Checkpoint):
        log_path = os.path.join(self.session_dir, "checkpoint_log.json")
        data = {
            "session": self.session_id,
            "progress": checkpoint.progress,
            "duration": time.time() - checkpoint.start_time,
            "best_loss": checkpoint.best_loss,
            "best_validation": checkpoint.best_validation
        }

        with open(log_path, "w") as f:
            json.dump(data, f, indent=2)
        pass

    # ===================================================================================================
    # Training Support Functions.
    # ===================================================================================================

    def register_metric(self, title: str, capacity: int=100):
        self.metrics[title] = Metric(title, capacity)

    def add_short_metric(self, title: str, value: float):
        """ Log an arbitrary metric"""
        self.get_metric(title).add_short(value)

    def add_fixed_metric(self, title: str, value: float):
        """ Log an arbitrary metric"""
        self.get_metric(title).add_fixed(value)

    def get_metric(self, title: str):
        if title not in self.metrics:
            self.register_metric(title)
        return self.metrics[title]

    def aggregate_metric(self, title: str):
        metric = self.get_metric(title)
        return metric.aggregate()
