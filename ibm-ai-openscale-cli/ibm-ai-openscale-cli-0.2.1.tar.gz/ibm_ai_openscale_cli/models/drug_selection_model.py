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

    def __init__(self, target_env, ml_engine_type = 'wml', history_days=7, model_instances=1, training_data_dict=None):
        super().__init__('DrugSelectionModel', target_env, ml_engine_type, history_days, model_instances, training_data_dict)

    def get_score_input(self, num_values=1):
        fields = ['AGE', 'SEX', 'BP', 'CHOLESTEROL', 'NA', 'K']
        values = []
        for _ in range(num_values):
            values.append([random.randint(15, 80),
                           random.choice(['F', 'M']),
                           random.choice(['HIGH', 'LOW', 'NORMAL']),
                           random.choice(['HIGH', 'NORMAL']),
                           random.uniform(0.5, 0.9),
                           random.uniform(0.02, 0.08)])
        return (fields, values)

    def get_payload_history(self, num_day):
        historyfile = os.path.join(self._model_dir, 'history_payloads.json')
        fullRecordsList = []
        if historyfile != None:
            with open(historyfile) as f:
                payloads = json.load(f)
            for day in range(num_day, num_day+1):
                for hour in range(24):
                    for payload in payloads:
                        req = payload['request']
                        resp = payload['response']
                        score_time = str(self._get_score_time(day, hour))
                        fullRecordsList.append(PayloadRecord(request=req, response=resp, scoring_timestamp=score_time))
        return fullRecordsList

    def get_quality_history(self, num_day):
        return super().get_quality_history(num_day, 0.75, 0.95)