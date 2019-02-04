# -*- coding: utf-8 -*-

"""
A Checkpoint system to support the trainer: when to save the models, draw metric graphs, etc.
"""

import time
from typing import Dict, List

from k_util.logger import Logger

from raid.logic.limit_type import LimitType

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class Checkpoint:
    def __init__(self,
                 on_hit=None,
                 interval_count: float=1,
                 interval_type: LimitType=LimitType.EPOCHS,
                 limit_number: float=10,
                 limit_type: LimitType=LimitType.EPOCHS):

        Logger.header("Initializing Checkpoint")

        self.interval_count: float = interval_count
        self.interval_type: LimitType = interval_type
        self.interval_gap_seconds: int = 0

        # Training limits.
        self.limit_number: float = limit_number
        self.limit_type: LimitType = limit_type

        # Runtime variables to manage the checkpoint.
        self.start_time: int = time.time()
        self.index_start_time: int = time.time()
        self.passed_epochs: int = 0
        self.index: int = 0

        self.best_loss: float = None
        self.best_validation: float = None
        self.on_hit = on_hit
        self.progress: float = 0

        # Work out the interval gap in seconds.
        self.interval_gap_seconds = self.convert_duration(self.interval_count, self.interval_type)
        self.limit_gap_seconds = self.convert_duration(self.limit_number, self.limit_type)

        # Timings.
        self.n_samples_trained: int = 0
        self.training_end_time: float = 0
        self.validation_time: float = 0
        self.validation_time_per_sample: float = 0
        self.samples_trained_map: Dict[str, int] = {}  # Mapping label ID to times trained.

        Logger.field("Interval Limit", self.interval_count)
        Logger.field("Interval Type", self.interval_type.value)

        Logger.field("Session Limit", self.limit_number)
        Logger.field("Session Type", self.limit_type.value)

    def register_samples_trained(self, labels: List[str]):
        for i in labels:
            if i not in self.samples_trained_map:
                self.samples_trained_map[i] = 0

            self.samples_trained_map[i] += 1
        self.n_samples_trained += 1

    @staticmethod
    def convert_duration(n: float, limit_type: LimitType):
        if limit_type == LimitType.SECONDS:
            return n
        elif limit_type == LimitType.MINUTES:
            return 60 * n
        elif limit_type == LimitType.HOURS:
            return 3600 * n

    def step(self, epoch_gain: int = 0) -> bool:
        self.passed_epochs += epoch_gain
        if self.interval_type == LimitType.EPOCHS:
            if self.passed_epochs >= self.interval_count:
                self.activate()
                return True
        else:
            if self.duration >= self.interval_gap_seconds:
                self.activate()
                return True

        return False

    @property
    def duration(self):
        return time.time() - self.index_start_time

    @property
    def training_duration(self):
        return self.training_end_time - self.index_start_time

    def activate(self):
        if self.on_hit is not None:
            self.on_hit(self)

        self.index += 1
        self.passed_epochs = 0
        self.n_samples_trained = 0
        self.validation_time = 0
        self.validation_time_per_sample = 0
        self.index_start_time = time.time()
        self.training_end_time = 0
        self.samples_trained_map.clear()

    def register_loss(self, value: float):
        if self.best_loss is None or value < self.best_loss:
            self.best_loss = value
            return True

    def register_validation(self, value: float):
        if self.best_validation is None or value > self.best_validation:
            self.best_validation = value
            return True

    def update_progress(self, epoch: int):
        if self.limit_type == LimitType.EPOCHS:
            self.progress = min(1.0, epoch / self.limit_number)
        else:
            self.progress = min(1.0, (time.time() - self.start_time) / self.limit_gap_seconds)
        return self.progress

    def has_completed(self, epoch: int):
        return self.update_progress(epoch) >= 1.0
