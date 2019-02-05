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

class GermanCreditRiskModel(Model):

    def __init__(self, target_env, ml_engine_type = 'wml', history_days=7, model_instances=1):
        super().__init__('GermanCreditRiskModel', target_env, ml_engine_type, history_days, model_instances)
        self.training_data_filename = 'credit_risk_training.csv'
        self._training_data_file = os.path.join(self._model_dir, self.training_data_filename)
        self._temp_meta_file = None
        self.cos_credentials = None

    def get_training_bucket(self):
        if self.cos_credentials is None:
            logger.error('ERROR: Cloud Object Storage credentials not set ...')
            exit(1)
        if self._temp_meta_file is None:
            # cos operations
            cos_instance = CloudObjectStorage(self.cos_credentials)
            bucket = cos_instance.get_bucket()
            if bucket is None:
                cos_instance.create_bucket()
                bucket = cos_instance.get_bucket()
            cos_instance.delete_item(bucket.name, self.training_data_filename)
            logger.info('Uploading training data to bucket: {}'.format(bucket.name))
            cos_instance.multi_part_upload(bucket.name, self.training_data_filename, self._training_data_file)
            return bucket

    def update_training_metadata(self):
        if self._temp_meta_file is None:
            bucket = self.get_training_bucket()
            # update training metadata
            with open(self.metadata['model_metadata_file']) as f:
                s = f.read()
                s = s.replace('__api_key__', self.cos_credentials['apikey'])
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
            checkingstatus = random.choice(['no_checking', '0_to_200'])
            loanduration = random.randint(12, 35)
            credithistory = random.choice(['no_credits', 'prior_payments_delayed', 'credits_paid_to_date', 'all_credits_paid_back', 'outstanding_credit'])
            loanpurpose = random.choice(['car_new', 'furniture', 'appliances', 'retraining'])
            loanamount = random.randint(800, 6000)
            existingsavings = random.choice(['unknown', 'less_100', '100_to_500', '500_to_1000'])
            employmentduration = random.choice(['less_1', '1_to_4', '4_to_7', 'greater_7'])
            installmentpercent = random.randint(2, 4)
            sex = random.choice(['female', 'male'])
            othersonloan = random.choice(['none', 'co-applicant'])
            currentresidenceduration = random.randint(2, 4)
            ownsproperty = random.choice(['unknown', 'savings_insurance', 'real_estate'])
            age = random.randint(23, 54)
            installmentplans = 'none'
            housing = random.choice(['own', 'free', 'rent'])
            existingcreditscount = random.randint(1, 2)
            job = random.choice(['skilled', 'management_self-employed'])
            dependents = 1
            telephone = random.choice(['yes', 'none'])
            foreignworker = random.choice(['yes', 'no'])
            if self._ml_engine_type == 'wml':
                values.append([checkingstatus, loanduration, credithistory, loanpurpose, loanamount, existingsavings, employmentduration, installmentpercent, sex, othersonloan, currentresidenceduration, ownsproperty, age, installmentplans, housing, existingcreditscount, job, dependents, telephone, foreignworker])
            elif self._ml_engine_type == 'azureml':
                values.append([str(checkingstatus), str(loanduration), str(credithistory), str(loanpurpose), str(loanamount), str(existingsavings), str(employmentduration), str(installmentpercent), str(sex), str(othersonloan), str(currentresidenceduration), str(ownsproperty), str(age), str(installmentplans), str(housing), str(existingcreditscount), str(job), str(dependents), str(telephone), str(foreignworker)])
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
                        req = payloads[index]['request']
                        resp = payloads[index]['response']
                        if self._ml_engine_type == 'azureml':
                            for counter, value in enumerate(req['values'][0]):
                                req['values'][0][counter] = str(req['values'][0][counter])
                            for counter, value in enumerate(resp['values'][0]):
                                try:
                                    tempval = resp['values'][0][counter] + 1
                                    if not '.' in resp['values'][0][counter]:
                                        resp['values'][0][counter] = str(resp['values'][0][counter])
                                except:
                                    pass
                        score_time = str(datetime.datetime.utcnow() + datetime.timedelta(hours=(-(24 * day + hour + 1))))
                        fullRecordsList.append(PayloadRecord(request=req, response=resp, scoring_timestamp=score_time))
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
        historyfile = os.path.join(self._model_dir, 'fairness_history.json')
        fullRecordsList = []
        if historyfile != None:
            with open(historyfile) as f:
                fairnessValues = json.load(f)
            for day in range(num_day, num_day+1):
                for hour in range(24):
                    fairnessTime = (datetime.datetime.utcnow() + datetime.timedelta(hours=(-(24*day + hour + 1)))).strftime('%Y-%m-%dT%H:%M:%SZ')
                    fullRecordsList.append({'timestamp': fairnessTime, 'value': fairnessValues[random.randint(0, len(fairnessValues))-1]})
        return fullRecordsList

    def get_quality_history(self, num_day):
        fullRecordsList = []
        for day in range(num_day, num_day+1):
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