# -*- coding: utf-8 -*-
"""
.. Created on Mon Nov 12 21:17:02 2018

.. module:: haidatacfg
   :platform: Windows, Linux
   :synopsis: A class that controls data processing of pandas dataframes

.. moduleauthor:: Hans Roggeman <hans@invalid.com>

"""

import os
import sys
import jsonpickle
import json
import traceback
import logging
import copy
import pandas as pd
import math
from pkgutil import iter_modules


from datetime import datetime
from operator import itemgetter

from fix_encode import fix_encode
from fix_colnames import fix_colnames
from fix_empty_cols import fix_empty_cols
from fix_empty_rows import fix_empty_rows
from to_datetime import to_datetime
from drop_cols import drop_cols
from fix_excess_stdev import fix_excess_stdev
from haidatautils import dicts_get

logging.disable(sys.maxsize)
logger = logging.getLogger(__name__)

myPath = os.path.dirname(os.path.abspath(__file__))


def module_exists(module_name):
    return module_name in (name for loader, name, is_pkg in iter_modules())

class HaiDataCfg(object):
    """We use this as a public class example class.

    .. note::
       An example of intersphinx is this: you **cannot** use :mod:`pickle` on this class.

    """

    _HAI_PATH = None
    _constructed_time = None
    _settings = None
    _settings_file_name = 'haidata_settings.json'
    _built_in_functions = ['fix_encode', "fix_colnames", "fix_empty_cols", "fix_empty_rows", "to_datetime", "drop_cols",
                           "fix_excess_stdev", "turn_to_int", "turn_to_factor", "fix_syntax"]
    _user_functions = {}

    def __init__(self):
        pass

    def __call__(self, df, inplace=True):
        if hasattr(self, 'ACTIONS'):
            if isinstance(df, pd.DataFrame):
                if len(self.ACTIONS) > 0:
                    try:
                        if all(map(lambda x: x > 0, df.shape)):
                            df_result = copy.deepcopy(df) if not inplace else df # from now on df_result will be altered inplace
                            for action in sorted([action for action in self.ACTIONS], key=itemgetter('SEQUENCE')):
                                # this is where we execute the actions
                                # replace the if statements with chained commands when all are implemented and
                                # we allow for the injection of custom functions
                                action_name = action['ACTION'].lower()
                                if action_name == 'fix_encode':
                                    df_result = fix_encode(df_result, action['ARGS'])
                                elif action_name == 'fix_colnames':
                                    df_result = fix_colnames(df_result, action['ARGS'])
                                elif action_name == 'fix_empty_cols':
                                    df_result = fix_empty_cols(df_result, action['ARGS'])
                                elif action_name == 'fix_empty_rows':
                                    df_result = fix_empty_rows(df_result, action['ARGS'])
                                elif action_name == 'to_datetime':
                                    df_result = to_datetime(df_result, action['ARGS'])
                                elif action_name == 'drop_cols':
                                    df_result = drop_cols(df_result, action['ARGS'])
                                elif action_name == 'fix_excess_stdev':
                                    df_result = fix_excess_stdev(df_result, action['ARGS'])
                                elif action_name in self._built_in_functions:
                                    pass  # not implemented yet
                                else:
                                    # user defined
                                    df_result = self._user_functions[action_name](df_result, action['ARGS'])
                            return df_result
                        else:
                            logger.warning("DataFrame with shape {0}, No actions performed.".format(str(df.shape)))
                    except Exception as e:
                        self._try_log_error(e)
            else:
                logger.warning("Object supplied was of type {0}, expected type {1}. No actions performed.". \
                               format(str(type(df)), str(pd.DataFrame)))
        else:
            logger.warning("No actions set in HaiDataCfg, No actions performed.")

        if isinstance(df, pd.DataFrame):
            return df

        return None

    def _register_user_functions_from_actions(self, _locals):
        if hasattr(self, 'ACTIONS'):
            if len(self.ACTIONS) > 0:
                for action in sorted([action for action in self.ACTIONS], key=itemgetter('SEQUENCE')):
                    action_name = action['ACTION'].lower()
                    if action_name not in self._built_in_functions:
                        try:
                            HaiDataCfg._register_action(action_name, _locals)
                        except Exception as e:
                            self._try_log_error(e)

    def _get_max_sequence(self):
        max_seq = -math.inf
        if hasattr(self, 'ACTIONS'):
            if len(self.ACTIONS) > 0:
                max_seq = max([action['SEQUENCE'] for action in self.ACTIONS])
        return max_seq

    def add_action(self, action_name, args_dict=None, seq_count=None, _locals=None):
        if args_dict is None:
            args_dict = dict({})
        if action_name not in self._built_in_functions:
            HaiDataCfg._register_action(action_name, _locals)
        if not hasattr(self, 'ACTIONS'):
            self.ACTIONS = []
        if seq_count is None:
            x = self._get_max_sequence()
            seq_count = x + 1 if math.isfinite(x) else 0
        action = dict({"ACTION": action_name, "SEQUENCE": int(seq_count), "ARGS": args_dict})
        self.ACTIONS.append(action)
        pass

    def to_json(self, json_file_name):
        actions_list = []
        if hasattr(self, 'ACTIONS'):
            actions_list = self.ACTIONS
        # will return a new instance as read by the file..
        return HaiDataCfg._dict_to_valid_instance(dict({"ACTIONS": actions_list}), json_file_name)

    @classmethod
    def construct_hai_data_cfg(cls, json_file_name=None, _locals=None):
        """We do not implement this in a __new__ method to block recursive calls from jsonpickle

        :param json_file_name: a JSON file Name
        :type json_file_name: str
        :param _locals: a dictionary of the variables in a scope, defaults to None of access is not required
        :type _locals: dicts
        :returns:  an instance of HaiDataCfg
        :raises: ValueError, IndexError, AttributeError, KeyError, AssertionError, Exception

        """
        try:
            if cls._HAI_PATH is None:
                cls._initialize()

            use_default_config = False
            json_file_name_to_use = json_file_name
            if json_file_name_to_use is None:
                json_file_name_to_use = os.path.join(HaiDataCfg.get_path(), 'config', 'default_cfg.json')
                if not os.path.isfile(json_file_name_to_use):
                    json_file_name_to_use = os.path.join(myPath, 'config', 'default_cfg.json')
                use_default_config = True

            dict_string_to_use = None
            direct_dict_input = False

            instance = None
            if type(json_file_name_to_use) is dict:
                instance = cls._dict_to_valid_instance(json_file_name_to_use, None)
                direct_dict_input = True
            else:
                if json_file_name_to_use.strip()[-4:].lower() == 'json' or os.path.isfile(json_file_name_to_use):
                    with open(json_file_name_to_use, 'r') as json_file:
                        instance = jsonpickle.decode(str(json_file.read()))
                else:
                    # data was entered as a json string
                    dict_string_to_use = json_file_name.strip()
                    instance = jsonpickle.decode(dict_string_to_use)

            if instance.__class__.__name__ is cls.__name__:
                instance.file_name = json_file_name_to_use if not direct_dict_input else None
            else:
                # JSON in the file was not specified according to jsonpickle, that is OK, it is a dict
                # though we read it from a file, there is no need to overwrite it
                instance = cls._dict_to_valid_instance(instance,
                                                       json_file_name_to_use if not use_default_config and
                                                                                not dict_string_to_use else None)
                if use_default_config:
                    instance.file_name = json_file_name_to_use

            assert (instance.__class__.__name__ is cls.__name__)
            instance._register_user_functions_from_actions(_locals)
            return instance

        except Exception as e:
            cls._try_log_error(e)

    @classmethod
    def _register_action(cls, func_name, _locals):
        try:
            if func_name in cls._built_in_functions:
                raise ValueError(
                    "{0} is built-in and cannot be overwritten. Please rename the action.".format(func_name))
            cls._user_functions[func_name] = dicts_get(func_name, _locals, locals(), globals())
        except Exception as e:
            cls._try_log_error(e)
        pass

    @classmethod
    def _dict_to_valid_instance(cls, instance, file_name=None):
        instance_string = cls._create_json_string_from_dict(instance, file_name)
        instance = jsonpickle.decode(instance_string)
        if cls._HAI_PATH is None:
            cls._initialize()
        return instance

    @classmethod
    def _set_valid_dict(cls, input_dict, file_name=None):
        input_dict["py/object"] = "haidata.haidatacfg." + cls.__name__ if module_exists(
            "haidata") else "haidatacfg." + cls.__name__
        input_dict["file_name"] = file_name
        if cls._HAI_PATH is None:
            cls._initialize()
        return input_dict

    @classmethod
    def _create_json_string_from_dict(cls, input_dict, file_name=None):
        cls._set_valid_dict(input_dict, file_name)
        json_string = json.dumps(input_dict, indent=4)
        if file_name is not None:
            with open(file_name, 'w') as f:
                print(json_string, file=f)
        return json_string

    @classmethod
    def get_path(cls):
        if cls._HAI_PATH is None:
            cls._initialize()
        return str(cls._HAI_PATH)

    @classmethod
    def _initialize(cls):

        cls._HAI_PATH = os.environ['HAI_PATH'] if not None else os.getcwd()
        cls._constructed_time = cls._now_time_string()

        settings_file = os.path.join(cls._HAI_PATH, 'config', cls._settings_file_name)

        json_dict = None
        logging_format = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

        if os.path.isfile(settings_file):
            with open(settings_file, 'r') as json_file:
                json_dict = json.loads(json_file.read())
                if type(json_dict) is list:
                    json_dict = json_dict[0]
        else:
            json_dict = dict({"CONSOLE_HANDLER": {"LOG_LEVEL": "ERROR"}})

        cls._settings = json_dict

        console_log_dict = cls._settings.get("CONSOLE_HANDLER", None)
        if console_log_dict is not None:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(logging_format)
            console_log_level = eval("logging." + console_log_dict.get('LOG_LEVEL', "WARNING").upper().strip())
            stream_handler.setLevel(console_log_level)
            try:
                logger.addHandler(stream_handler)
            except:
                pass

        file_log_dict = cls._settings.get("FILE_HANDLER", None)
        if file_log_dict is not None:
            log_dir = file_log_dict.get('LOG_DIR', os.path.join(cls._HAI_PATH, "logs"))
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            if log_dir is None:
                log_dir = os.getcwd()
            log_file_name = os.path.join(log_dir, cls._constructed_time)
            file_handler = logging.FileHandler(log_file_name)
            file_handler.setFormatter(logging_format)
            file_log_level = eval("logging." + file_log_dict.get('LOG_LEVEL', "WARNING").upper().strip())
            file_handler.setLevel(file_log_level)
            try:
                logger.addHandler(file_handler)
            except:
                pass

    @staticmethod
    def from_json(json_file_name, _locals=None):
        return HaiDataCfg.construct_hai_data_cfg(json_file_name, _locals)
        pass

    @staticmethod
    def _now_time_string():
        return datetime.now().strftime("%Y%m%d%H%M%S")

    @staticmethod
    def _construct_log_filename():
        return "HaiData_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".log"

    @staticmethod
    def _try_log_error(e):
        logger.error(traceback.format_exc())
        raise e
