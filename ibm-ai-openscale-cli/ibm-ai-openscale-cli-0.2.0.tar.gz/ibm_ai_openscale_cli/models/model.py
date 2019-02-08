# coding=utf-8
import logging
import os
import re
import datetime
from ibm_ai_openscale_cli.utility_classes.utils import jsonFileToDict
from pathlib import Path

logger = logging.getLogger(__name__)

class Model():

    def __init__(self, name, target_env, ml_engine_type = 'wml', history_days=7, model_instances=1):
        self.name = name
        if model_instances > 1:
            self.name += str(model_instances)
        self._ml_engine_type = ml_engine_type
        self._target_env = target_env
        self._history_days = history_days
        self._model_dir = os.path.join(os.path.dirname(__file__), name)
        configuration_data_file_name = re.sub('(.)([A-Z])', r'\1_\2', name).lower() + '.json'
        configuration_data_file = os.path.join(self._model_dir, configuration_data_file_name)
        self.training_data_stats_fairness = None
        self.training_data_stats_explainability = None
        if not Path(configuration_data_file).is_file():
            configuration_data_file = configuration_data_file.replace('.json', '_{}.json'.format(ml_engine_type))
        self.configuration_data = jsonFileToDict(configuration_data_file)
        env_name = '' if self._target_env['name'] == 'YPPROD' else self._target_env['name']
        self.metadata = {}
        self.metadata['model_name'] = self.name + env_name
        self.metadata['model_metadata_file'] = os.path.join(self._model_dir, 'model-meta.json')
        self.metadata['model_file'] = os.path.join(self._model_dir, 'model-content.gzip')
        self.metadata['pipeline_metadata_file'] = os.path.join(self._model_dir, 'pipeline-meta.json')
        self.metadata['pipeline_file'] = os.path.join(self._model_dir, 'pipeline-content.tgz')
        self.metadata['deployment_name'] = self.name + env_name
        self.metadata['deployment_description'] = 'Created by aios fast path.'

    def _get_score_time(self, day, hour):
        return datetime.datetime.utcnow() + datetime.timedelta(hours=(-(24 * day + hour + 1)))