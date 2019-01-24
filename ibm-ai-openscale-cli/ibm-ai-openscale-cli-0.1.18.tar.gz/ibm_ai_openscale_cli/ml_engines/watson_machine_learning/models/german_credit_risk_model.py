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
from ibm_ai_openscale_cli.ml_engines.watson_machine_learning.models.model import Model

logger = logging.getLogger(__name__)

class GermanCreditRiskModel(Model):

    def __init__(self, target_env, history_days=7, model_instances=1):
        super().__init__(target_env, 'GermanCreditRiskModel', history_days, model_instances)
        self._training_data_filename = 'credit_risk_training.csv'
        self._training_data_file = os.path.join(self._model_dir, self._training_data_filename)
        self._temp_meta_file = None

    def update_training_metadata(self, cos_credentials):
        if self._temp_meta_file is None:
            # cos operations
            cos_instance = CloudObjectStorage(cos_credentials)
            bucket = cos_instance.get_bucket()
            if bucket is None:
                cos_instance.create_bucket()
                bucket = cos_instance.get_bucket()
            cos_instance.delete_item(bucket.name, self._training_data_filename)
            logger.info('Uploading training data to bucket: {}'.format(bucket.name))
            cos_instance.multi_part_upload(bucket.name, self._training_data_filename, self._training_data_file)
            # update training metadata
            with open(self.metadata['model_metadata_file']) as f:
                s = f.read()
                s = s.replace('__api_key__', cos_credentials['apikey'])
                s = s.replace('__bucket_name__', bucket.name)
            temp_meta_file = tempfile.NamedTemporaryFile(suffix='-{}-metadata-tmp.json'.format(self.model_name), delete=False)
            with temp_meta_file as temp:
                with open(temp.name, 'w') as fd:
                    fd.write(s)
            self._temp_meta_file = temp_meta_file.name
        logger.info('Using model metadata file: {}'.format(self._temp_meta_file))
        self.metadata['model_metadata_file'] = self._temp_meta_file

    def get_score_input(self, num_values=1):
        fields = ["CheckingStatus","LoanDuration","CreditHistory","LoanPurpose","LoanAmount","ExistingSavings","EmploymentDuration","InstallmentPercent","Sex","OthersOnLoan","CurrentResidenceDuration","OwnsProperty","Age","InstallmentPlans","Housing","ExistingCreditsCount","Job","Dependents","Telephone","ForeignWorker"]
        values = []
        for _ in range(num_values):
            values.append([
                random.choice(['no_checking', '0_to_200']),
                random.randint(12, 35),
                random.choice(['no_credits', 'prior_payments_delayed', 'credits_paid_to_date', 'all_credits_paid_back', 'outstanding_credit']),
                random.choice(['car_new', 'furniture', 'appliances', 'retraining']),
                random.randint(800, 6000),
                random.choice(['unknown', 'less_100', '100_to_500', '500_to_1000']),
                random.choice(['less_1', '1_to_4', '4_to_7', 'greater_7']),
                random.randint(2, 4),
                random.choice(['female', 'male']),
                random.choice(['none', 'co-applicant']),
                random.randint(2, 4),
                random.choice(['unknown', 'savings_insurance', 'real_estate']),
                random.randint(23, 54),
                'none',
                random.choice(['own', 'free', 'rent']),
                random.randint(1, 2),
                random.choice(['skilled', 'management_self-employed']),
                1,
                random.choice(['yes', 'none']),
                random.choice(['yes', 'no'])
            ])
        return {'fields': fields, 'values': values }

    def get_payload_history(self):
        fullRecordsList = []
        for day in range(self._history_days):
            logger.info(' - Loading day {}'.format(day + 1))
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
        historyfile = os.path.join(self._model_dir, 'fairness_history.json')
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

    def __del__(self):
        temp_file = self._temp_meta_file
        if temp_file and Path(temp_file).is_file():
            try:
                logger.debug('Deleting file: {}'.format(temp_file))
                os.remove(temp_file)
            except Exception as e:
                logger.debug('Warning: Unable to cleanup temporary file {}: {}'.format(temp_file, e))
