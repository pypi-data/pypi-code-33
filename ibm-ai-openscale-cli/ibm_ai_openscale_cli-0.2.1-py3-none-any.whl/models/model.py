# coding=utf-8
import logging
import os
import re
import datetime
import random
import math
import json
from ibm_ai_openscale_cli.utility_classes.utils import jsonFileToDict
from pathlib import Path

logger = logging.getLogger(__name__)

CONFIGURATION_FILENAME = 'configuration.json'
MODEL_META_FILENAME = 'model_meta.json'
MODEL_CONTENT_FILENAME = 'model_content.gzip'
PIPELINE_META_FILENAME = 'pipeline_meta.json'
PIPELINE_CONTENT_FILENAME = 'pipeline_content.gzip'
TRAINING_DATA_STATISTICS_FILENAME = 'training_data_statistics.json'
FAIRNESS_HISTORY_FILENAME = 'history_fairness.json'
PAYLOAD_HISTORY_FILENAME = 'history_payloads.json'

class Model():

    def __init__(self, name, target_env, ml_engine_type = 'wml', history_days=7, model_instances=1, training_data_dict=None):
        self.name = name
        if model_instances > 1:
            self.name += str(model_instances)
        self._ml_engine_type = ml_engine_type
        self._target_env = target_env
        self._history_days = history_days
        self._model_dir = os.path.join(os.path.dirname(__file__), name)
        env_name = '' if target_env['name'] == 'YPPROD' else target_env['name']

        # model create and deploy
        self.metadata = {}
        self.metadata['model_name'] = self.name + env_name
        self.metadata['model_metadata_file'] = os.path.join(self._model_dir, MODEL_META_FILENAME)
        self.metadata['model_file'] = os.path.join(self._model_dir, MODEL_CONTENT_FILENAME)
        self.metadata['pipeline_metadata_file'] = os.path.join(self._model_dir, PIPELINE_META_FILENAME)
        self.metadata['pipeline_file'] = os.path.join(self._model_dir, PIPELINE_CONTENT_FILENAME)
        self.metadata['deployment_name'] = self.name + env_name
        self.metadata['deployment_description'] = 'Created by Watson OpenScale Fast Path.'

        # configuration
        configuration_file = os.path.join(self._model_dir, CONFIGURATION_FILENAME)
        if not Path(configuration_file).is_file():
            configuration_file = configuration_file.replace('.json', '_{}.json'.format(ml_engine_type))
        self.configuration_data = jsonFileToDict(configuration_file)

        # training data
        self.training_data_source = None
        self.training_data_statistics = None
        if training_data_dict:
            self._cos_credentials = training_data_dict['connection']
            self._training_data_filename = training_data_dict['source']['file_name']
            self._bucket_name = training_data_dict['source']['bucket']
            first_line_header = True if training_data_dict['source']['firstlineheader'] == 'true' else False
            self.training_data_source = BluemixCloudObjectStorageReference( self._cos_credentials,
                                        '{}/{}'.format( self._bucket_name,
                                                        self._training_data_filename ),
                                        first_line_header=first_line_header )
        if not self.training_data_source:
            statistics_file_path = os.path.join(self._model_dir, TRAINING_DATA_STATISTICS_FILENAME)
            if Path(statistics_file_path).is_file():
                self.training_data_statistics = jsonFileToDict(statistics_file_path)

    def _get_score_time(self, day, hour):
        return datetime.datetime.utcnow() + datetime.timedelta(hours=(-(24 * day + hour + 1)))

    # return an array of tuples with datestamp, response_time, and records
    def get_performance_history(self, num_day):
        fullRecordsList = []
        now = datetime.datetime.utcnow()
        for day in range(num_day, num_day+1):
            # model "typical" day (min at midnight, max at noon)
            # but with some days more busy overall than others, plus some random "noise"
            day_base = random.randint(1,4)
            for hour in range(24):
                score_time = (now + datetime.timedelta(hours=(-(24 * day + hour + 1)))).strftime('%Y-%m-%dT%H:%M:%SZ')
                score_count = day_base*60 + math.fabs(hour - 12)*30*random.randint(1,2) + 2*random.randint(-30, 90) + 1
                score_resp = random.uniform(60, 300)
                fullRecordsList.append({'timestamp': score_time, 'value': {'response_time': score_resp, 'records': score_count}})
        return fullRecordsList

    def get_fairness_history(self, num_day):
        historyfile = os.path.join(self._model_dir, FAIRNESS_HISTORY_FILENAME)
        fullRecordsList = []
        if historyfile != None:
            with open(historyfile) as f:
                fairnessValues = json.load(f)
            for day in range(num_day, num_day+1):
                for hour in range(24):
                    score_time = self._get_score_time(day, hour).strftime('%Y-%m-%dT%H:%M:%SZ')
                    fullRecordsList.append({'timestamp': score_time, 'value': fairnessValues[random.randint(0, len(fairnessValues))-1]})
        return fullRecordsList

    def get_quality_history(self, num_day, quality_min, quality_max):
        fullRecordsList = []
        for day in range(num_day, num_day+1):
            for hour in range(24):
                qualityTime = self._get_score_time(day, hour).strftime('%Y-%m-%dT%H:%M:%SZ')
                quality = random.uniform(quality_min, quality_max)
                fullRecordsList.append(
                    {'timestamp': qualityTime,
                    'value': {
                        'quality': quality,
                        'threshold': 0.8,
                        'metrics': [
                            {
                                'name': 'auroc',
                                'value': quality,
                                'threshold': 0.8
                            }
                        ]
                    }
                })
        return fullRecordsList
