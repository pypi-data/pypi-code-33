# coding=utf-8
import os
import logging
import random
import json
import datetime
import tempfile
from pathlib import Path
from ibm_ai_openscale_cli.database_classes.cos import CloudObjectStorage
from ibm_ai_openscale.supporting_classes import PayloadRecord
from ibm_ai_openscale_cli.models.model import Model

logger = logging.getLogger(__name__)

class ScikitDigitsModel(Model):

    def __init__(self, target_env, ml_engine_type = 'wml', history_days=7, model_instances=1, training_data_dict=None):
        super().__init__('ScikitDigitsModel', target_env, ml_engine_type, history_days, model_instances)
        self._scoring_data_filename = 'scikit_digits_scoring.json'
        self._scoring_data_file = os.path.join(self._model_dir, self._scoring_data_filename)
        with open(self._scoring_data_file) as f:
            self._scoring_data = json.load(f)

    def get_score_input(self, num_values=1):
        fields = [ 'f0', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f20', 'f21', 'f22', 'f23', 'f24', 'f25', 'f26', 'f27', 'f28', 'f29', 'f30', 'f31', 'f32', 'f33', 'f34', 'f35', 'f36', 'f37', 'f38', 'f39', 'f40', 'f41', 'f42', 'f43', 'f44', 'f45', 'f46', 'f47', 'f48', 'f49', 'f50', 'f51', 'f52', 'f53', 'f54', 'f55', 'f56', 'f57', 'f58', 'f59', 'f60', 'f61', 'f62', 'f63' ]
        values = []
        for _ in range(num_values):
            values.append(random.choice(self._scoring_data)['data'])
        return (fields, values)
