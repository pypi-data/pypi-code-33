# coding=utf-8
import os
import logging
import random
import json
import datetime
from ibm_ai_openscale.supporting_classes import PayloadRecord
from ibm_ai_openscale_cli.models.model import Model

logger = logging.getLogger(__name__)

class DrugSelectionModel(Model):

    def __init__(self, target_env, ml_engine_type = 'wml', history_days=7, model_instances=1):
        super().__init__('DrugSelectionModel', target_env, ml_engine_type, history_days, model_instances)

    def get_score_input(self, num_values=1):
        values = []
        for _ in range(num_values):
            values.append([random.randint(15, 80),
                           random.choice(['F', 'M']),
                           random.choice(['HIGH', 'LOW', 'NORMAL']),
                           random.choice(['HIGH', 'NORMAL']),
                           random.uniform(0.5, 0.9),
                           random.uniform(0.02, 0.08)])
        return {
            'fields': ['AGE', 'SEX', 'BP', 'CHOLESTEROL', 'NA', 'K'],
            'values': values
        }

    def get_payload_history(self):
        historyfile = os.path.join(self._model_dir, 'historypayloads.json')
        fullRecordsList = []
        if historyfile != None:
            with open(historyfile) as f:
                payloads = json.load(f)
            for day in range(self._history_days):
                logger.info(' - Loading day {}'.format(day + 1))
                for hour in range(24):
                    for payload in payloads:
                        score_time = str(datetime.datetime.utcnow() + datetime.timedelta(hours=(-(24 * day + hour + 1))))
                        fullRecordsList.append(PayloadRecord(request=payload['request'], response=payload['response'], scoring_timestamp=score_time))
        return fullRecordsList

    # return an array of tuples with datestamp, response_time, and records
    def get_performance_history(self):
        fullRecordsList = []
        for day in range(self._history_days):
            logger.info(' - Loading day {}'.format(day + 1))
            for hour in range(24):
                score_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=(-(24 * day + hour + 1)))).strftime('%Y-%m-%dT%H:%M:%SZ')
                score_count = random.randint(60, 600)
                score_resp = random.uniform(60, 300)
                fullRecordsList.append({'timestamp': score_time, 'value': {'response_time': score_resp, 'records': score_count}})
        return fullRecordsList

    def get_fairness_history(self):
        historyfile = os.path.join(self._model_dir, 'historyfairness.json')
        fullRecordsList = []
        if historyfile != None:
            with open(historyfile) as f:
                fairnessValues = json.load(f)
            for day in range(self._history_days):
                logger.info(' - Loading day {}'.format(day + 1))
                for hour in range(24):
                    fairnessTime = (datetime.datetime.utcnow() + datetime.timedelta(hours=(-(24*day + hour + 1)))).strftime('%Y-%m-%dT%H:%M:%SZ')
                    fullRecordsList.append({'timestamp': fairnessTime, 'value': fairnessValues[random.randint(0, len(fairnessValues))-1]})
        return fullRecordsList

    def get_quality_history(self):
        fullRecordsList = []
        for day in range(self._history_days):
            logger.info(' - Loading day {}'.format(day + 1))
            for hour in range(24):
                qualityTime = (datetime.datetime.utcnow() + datetime.timedelta(hours=(-(24*day + hour + 1)))).strftime('%Y-%m-%dT%H:%M:%SZ')
                quality = random.uniform(0.75, 0.95)
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