# -*- coding: utf-8 -*-

"""
A Checkpoint system to support the trainer: when to save the models, draw metric graphs, etc.
"""

import time
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

    def convert_duration(self, n: float, limit_type: LimitType):
        if limit_type == LimitType.SECONDS:
            return n
        elif limit_type == LimitType.MINUTES:
            return 60 * self.interval_count
        elif limit_type == LimitType.HOURS:
            return 3600 * self.interval_count

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

    def activate(self):
        if self.on_hit is not None:
            self.on_hit(self)

        self.index += 1
        self.passed_epochs = 0
        self.index_start_time = time.time()

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
