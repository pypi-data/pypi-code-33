# -*- coding: utf-8 -*-

"""
<ENTER DESCRIPTION HERE>
"""

import json
import os
import sys
from distutils.dir_util import copy_tree
from typing import Union, Type

from k_util import pather
from k_util.logger import Logger

from raid.data.interface.i_dataset import IDataset
from raid.logic.grid_search import grid_search
from raid.logic.limit_type import LimitType
from raid.logic.trainer import Trainer

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class Engine:

    C_SESSION_LIMIT_TYPE: str = "session_limit_type"
    C_SESSION_LIMIT: str = "session_limit"
    C_INTERVAL_TYPE: str = "interval_type"
    C_INTERVAL: str = "interval"

    def __init__(self):
        self.session_limit_type: LimitType = LimitType.EPOCHS
        self.session_limit: float = 10
        self.interval_type: LimitType = LimitType.EPOCHS
        self.interval: float = 1

    def execute(
            self,
            title: str,
            trainer_class: Type[Trainer],
            config: Union[dict, str],
            training_set: IDataset,
            validation_set: IDataset
    ):
        """ Takes a trainer object, some configs (either path to json, yaml or dict). """

        output_dir = os.path.join("output", title)
        pather.create(output_dir)
        self.create_src_copy(trainer_class, output_dir)

        # Load the session run limits, and pop them from the config.
        self.session_limit_type = self.get_limit_type(self.C_SESSION_LIMIT_TYPE, config, self.session_limit_type)
        self.session_limit = self.get(self.C_SESSION_LIMIT, config, self.session_limit)
        self.interval_type = self.get_limit_type(self.C_INTERVAL_TYPE, config, self.interval_type)
        self.interval = self.get(self.C_INTERVAL, config, self.interval)

        Logger.header("Preparing to Run Engine")
        Logger.field("Session Limit", f"{self.session_limit} {self.session_limit_type.value}")
        Logger.field("Interval", f"{self.interval} {self.interval_type.value}")

        # Grid search the config.
        grid_collection = grid_search(config)

        # Engine Summary
        engine_summary: dict = {f"session_{i}": None for i in range(len(grid_collection))}

        # For each sub-config, run the trainer.
        for i in range(len(grid_collection)):
            session_title = f"{title}/{title}_session_{i}"
            i_config = grid_collection[i]
            trainer: Trainer = trainer_class()
            trainer.output_dir = "output"
            trainer.session_id = session_title
            trainer.start_session(
                session_title,
                i_config,
                training_set=training_set,
                validation_set=validation_set,
                limit_number=self.session_limit,
                limit_type=self.session_limit_type,
                cp_interval_number=self.interval,
                cp_interval_type=self.interval_type
            )

            self.create_session_summary(i, engine_summary, output_dir, trainer)

    @staticmethod
    def create_session_summary(i, engine_summary, output_dir, trainer):
        session_summary = {
            "best_validation": trainer.checkpoint.best_validation,
            "best_loss": trainer.checkpoint.best_loss
        }
        engine_summary[f"session_{i}"] = session_summary
        engine_summary_list = list(engine_summary.items())
        engine_summary_list.sort(key=lambda x: (x[1]["best_validation"] if x[1] is not None else -1), reverse=True)
        engine_summary_path = os.path.join(output_dir, "engine_summary.json")
        with open(engine_summary_path, "w") as f:
            json.dump(engine_summary_list, f, indent=2)

    @staticmethod
    def get(key: str, config: dict, default=None):
        if key in config:
            return config[key]
        else:
            return default

    @staticmethod
    def get_limit_type(key: str, config: dict, default=None):
        if key in config:
            limit_type_string = config[key]
            for limit_type in LimitType:
                if limit_type.value == limit_type_string:
                    return limit_type
            raise Exception(f"Unrecognized limit Type: {limit_type_string}")
        else:
            return default

    @staticmethod
    def create_src_copy(trainer_class: Type[Trainer], output_dir: str):
        """ Make a copy of the trainer source directory for future reference. """
        trainer_dir = os.path.dirname(sys.modules[trainer_class.__module__].__file__)
        copy_dir = os.path.join(output_dir, "src")
        pather.create(copy_dir)
        copy_tree(trainer_dir, copy_dir)

