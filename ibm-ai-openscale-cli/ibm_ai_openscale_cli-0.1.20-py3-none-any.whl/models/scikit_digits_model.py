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

    def __init__(self, target_env, ml_engine_type = 'wml', history_days=7, model_instances=1):
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
        return {'fields': fields, 'values': values }

    def get_payload_history(self, num_day):
        fullRecordsList = []
        for day in range(num_day, num_day+1):
            history_file = os.path.join(self._model_dir, 'payload_history_' + str(day + 1) + '.json')
            with open(history_file) as f:
                payloads = json.load(f)
                hourly_records = int(len(payloads) / 24)
                index = 0
                for hour in range(24):
                    for i in range(hourly_records):
                        score_time = str(datetime.datetime.utcnow() + datetime.timedelta(hours=(-(24 * day + hour + 1))))
                        fullRecordsList.append(PayloadRecord(request=payloads[index]['request'], response=payloads[index]['response'], scoring_timestamp=score_time))
                        index += 1
        return fullRecordsList

    # return an array of tuples with datestamp, response_time, and records
    def get_performance_history(self, num_day):
        fullRecordsList = []
        for day in range(num_day, num_day+1):
            for hour in range(24):
                score_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=(-(24 * day + hour + 1)))).strftime('%Y-%m-%dT%H:%M:%SZ')
                score_count = random.randint(60, 600)
                score_resp = random.uniform(60, 300)
                fullRecordsList.append({'timestamp': score_time, 'value': {'response_time': score_resp, 'records': score_count}})
        return fullRecordsList

    def get_fairness_history(self, num_day):
        fullRecordsList = []
        historyfile = os.path.join(self._model_dir, 'fairness_history.json')
        if historyfile != None and self._history_days > 0:
            with open(historyfile) as f:
                fairnessValues = json.load(f)
            for day in range(num_day, num_day+1):
                for hour in range(24):
                    fairnessTime = (datetime.datetime.utcnow() + datetime.timedelta(hours=(-(24*day + hour + 1)))).strftime('%Y-%m-%dT%H:%M:%SZ')
                    fullRecordsList.append({'timestamp': fairnessTime, 'value': fairnessValues[random.randint(0, len(fairnessValues))-1]})
        return fullRecordsList

    def get_quality_history(self, num_day):
        fullRecordsList = []
        for day in range(self._history_days):
            for hour in range(num_day, num_day+1):
                score_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=(-(24*day + hour + 1)))).strftime('%Y-%m-%dT%H:%M:%SZ')
                quality = random.uniform(0.68, 0.80)
                fullRecordsList.append({
                    'timestamp': score_time,
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
