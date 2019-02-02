# -*- coding: utf-8 -*-

"""
<ENTER DESCRIPTION HERE>
"""

import json
import os
import sys
from distutils.dir_util import copy_tree
from typing import Union, Type

import yaml
from k_util import pather
from k_util.logger import Logger

from raid.data.interface.i_dataset import IDataset
from raid.logic.config import Config
from raid.logic.grid_search import grid_search
from raid.logic.limit_type import LimitType
from raid.logic.trainer import Trainer

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


C_ENGINE: str = "engine"
C_TRAINER: str = "trainer"
C_SESSION_LIMIT_TYPE: str = "session_limit_type"
C_SESSION_LIMIT: str = "session_limit"
C_INTERVAL_TYPE: str = "interval_type"
C_INTERVAL: str = "interval"


class Engine:

    def __init__(self):
        pass

    @staticmethod
    def execute(
            title: str,
            trainer_class: Type[Trainer],
            config: Union[dict, str],
            training_set: IDataset,
            validation_set: IDataset
    ):
        """ Takes a trainer object, some configs (either path to json, yaml or dict). """

        output_dir = Engine.setup_output_paths(title, trainer_class)

        # Manage the incoming config object.
        engine_config, trainer_config = Engine.load_config(config)

        # Load the session run limits, and pop them from the config.
        session_limit_type = Engine.get_limit_type(C_SESSION_LIMIT_TYPE, engine_config, LimitType.EPOCHS)
        session_limit = Engine.get(C_SESSION_LIMIT, engine_config, 10)
        interval_type = Engine.get_limit_type(C_INTERVAL_TYPE, engine_config, LimitType.EPOCHS)
        interval = Engine.get(C_INTERVAL, engine_config, 1)

        Logger.header("Preparing to Run Engine")
        Logger.field("Session Limit", f"{session_limit} {session_limit_type.value}")
        Logger.field("Interval", f"{interval} {interval_type.value}")

        # Grid search the config.
        grid_collection = grid_search(trainer_config)

        # Engine Summary
        engine_summary: dict = {f"session_{i}": None for i in range(len(grid_collection))}

        # For each sub-config, run the trainer.
        for i in range(len(grid_collection)):

            session_id = f"{title}_session_{i}"
            session_output_dir = os.path.join(output_dir, "sessions", str(i))

            i_config_data = grid_collection[i]
            i_config = Config(i_config_data)
            trainer: Trainer = trainer_class(i_config)
            trainer.set_session_data(session_id, session_output_dir)
            i_config.generate_config_summary(session_output_dir)

            trainer.start_session(
                training_set=training_set,
                validation_set=validation_set,
                limit_number=session_limit,
                limit_type=session_limit_type,
                cp_interval_number=interval,
                cp_interval_type=interval_type
            )

            Engine.create_session_summary(i, engine_summary, output_dir, trainer)

    @staticmethod
    def load_config(config):
        if type(config) is str:
            if not os.path.exists(config):
                raise Exception(f"No config file found at {config}.")

            if ".yml" in config.lower() or ".yaml" in config.lower():
                with open(config, "r") as f:
                    data = yaml.load(f)

            elif ".json" in config.lower():
                with open(config, "r") as f:
                    data = json.load(f)
            else:
                raise Exception(f"Config format unrecognized. Must be JSON or YAML: {config}")
        elif type(config) is dict:
            data = config
        else:
            raise Exception(f"Config item must be either a path (string) or a dict object. "
                            f"Detected type: {type(config)}")

        print(data)
        engine_config = data[C_ENGINE] if C_ENGINE in data else {}
        trainer_config = data[C_TRAINER] if C_TRAINER in data else {}
        return engine_config, trainer_config

    @staticmethod
    def setup_output_paths(title, trainer_class):
        output_dir = os.path.join("output", title)
        pather.create(output_dir)
        Engine.create_src_copy(trainer_class, output_dir)
        return output_dir

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
