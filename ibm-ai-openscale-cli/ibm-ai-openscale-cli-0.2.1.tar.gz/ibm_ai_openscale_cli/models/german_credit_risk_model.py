# coding=utf-8
import os
import logging
import random
import json
import tempfile
import copy
from pathlib import Path
from ibm_ai_openscale_cli.utility_classes.utils import choices
from ibm_ai_openscale_cli.database_classes.cos import CloudObjectStorage
from ibm_ai_openscale.supporting_classes import PayloadRecord, BluemixCloudObjectStorageReference
from ibm_ai_openscale_cli.models.model import Model
from ibm_ai_openscale_cli.utility_classes.utils import jsonFileToDict

logger = logging.getLogger(__name__)

class GermanCreditRiskModel(Model):

    def __init__(self, target_env, ml_engine_type = 'wml', history_days=7, model_instances=1, training_data_dict=None):
        super().__init__('GermanCreditRiskModel', target_env, ml_engine_type, history_days, model_instances, training_data_dict)
        self._temp_meta_file = None

    # generate a valid value based roughly on the training data distribution
    def _get_weighted_score_input_value(self):
        checkingstatus = choices(['no_checking', '0_to_200', 'greater_200', 'less_0'], weights=[20, 13, 3, 14])
        loanduration = choices([0, 1, 2, 3, 4], weights=[5, 18, 5, 18, 1])
        if loanduration == 0:
            loanduration = random.randint(4,6)
        elif loanduration == 1:
            loanduration = random.randint(7,23)
        elif loanduration == 2:
            loanduration = 24
        elif loanduration == 3:
            loanduration = random.randint(25,35)
        else:
            loanduration = random.randint(36,50)
        credithistory = choices(['no_credits', 'prior_payments_delayed', 'credits_paid_to_date', 'all_credits_paid_back', 'outstanding_credit'], weights=[1, 17, 15, 8, 10])
        loanpurpose = choices(['appliances', 'business', 'car_new', 'car_used', 'education', 'furniture', 'other', 'radio_tv', 'repairs', 'retraining', 'vacation'], weights=[6, 1, 9, 8, 2, 9, 1, 8, 3, 2, 2])
        loanamount = choices([0, 1, 2], weights=[10, 35, 5])
        if loanamount == 0:
            loanamount = 250
        elif loanamount == 1:
            loanamount = 10*random.randint(26, 700)
        else:
            loanamount = 10*random.randint(701, 1000)
        existingsavings = choices(['unknown', 'less_100', '100_to_500', '500_to_1000', 'greater_1000'], weights=[4, 19, 11, 11, 6])
        employmentduration = choices(['unemployed', 'less_1', '1_to_4', '4_to_7', 'greater_7'], weights=[3, 9, 15, 14, 9])
        installmentpercent = choices([1, 2, 3, 4, 5], weights=[5, 12, 16, 12, 4])
        sex = choices(['female', 'male'], weights=[17, 33])
        othersonloan = choices(['none', 'co-applicant', 'guarantor'], weights=[42, 7, 1])
        currentresidenceduration = choices([1, 2, 3, 4, 5], weights=[6, 12, 17, 11, 4])
        ownsproperty = choices(['unknown', 'savings_insurance', 'real_estate', 'car_other'], weights=[7, 17, 11, 15])
        age = choices([0, 1, 2, 3, 4], weights=[30, 6, 27, 6, 3])
        if age == 0:
            age = random.randint(19, 21)
        elif age == 1:
            age = random.randint(22, 27)
        elif age == 2:
            age = random.randint(28, 45)
        elif age == 3:
            age = random.randint(46, 52)
        else:
            age = random.randint(53, 74)
        installmentplans = choices(['none', 'stores', 'bank'], weights=[35, 10, 5])
        housing = choices(['own', 'free', 'rent'], weights=[32, 7, 11])
        existingcreditscount = choices([1, 2, 3], weights=[28, 20, 2])
        job = choices(['skilled', 'management_self-employed', 'unskilled', 'unemployed'], weights=[34, 6, 7, 3])
        dependents = choices([1, 2], weights=[42, 8])
        telephone = choices(['yes', 'none'], weights=[21, 29])
        foreignworker = random.choice(['yes', 'no'])
        return [checkingstatus, loanduration, credithistory, loanpurpose, loanamount, existingsavings, employmentduration, installmentpercent, sex, othersonloan, currentresidenceduration, ownsproperty, age, installmentplans, housing, existingcreditscount, job, dependents, telephone, foreignworker]

    def get_score_input(self, num_values=1):
        fields = ["CheckingStatus","LoanDuration","CreditHistory","LoanPurpose","LoanAmount","ExistingSavings","EmploymentDuration","InstallmentPercent","Sex","OthersOnLoan","CurrentResidenceDuration","OwnsProperty","Age","InstallmentPlans","Housing","ExistingCreditsCount","Job","Dependents","Telephone","ForeignWorker"]
        values = []
        for _ in range(num_values):
            values.append(self._get_weighted_score_input_value())
        return (fields, values)

    def get_payload_history(self, num_day):
        """ Retrieves payload history from a json file"""
        fullRecordsList = []
        for day in range(num_day, num_day+1):
            history_file = os.path.join(self._model_dir, 'history_payloads_' + str(day + 1) + '.json')
            with open(history_file) as f:
                payloads = json.load(f)
                hourly_records = int(len(payloads) / 24)
                index = 0
                for hour in range(24):
                    for i in range(hourly_records):
                        req = payloads[index]['request']
                        resp = payloads[index]['response']
                        score_time = str(self._get_score_time(day, hour))
                        fullRecordsList.append(PayloadRecord(request=req, response=resp, scoring_timestamp=score_time))
                        index += 1
        return fullRecordsList

    def generate_payload_history(self, num_day):
        """ Generates random payload history"""
        fullRecordsList = []
        for day in range(num_day, num_day+1):
            hourly_records = random.randint(2,20)
            for hour in range(24):
                for i in range(hourly_records):
                    fields, values = self.get_score_input()
                    req = {'fields': fields, 'values': values }
                    resp = copy.deepcopy(req)
                    if self._ml_engine_type == 'azureml':
                        resp['fields'].append('Scored Labels')
                        resp['fields'].append('Scored Probabilities')
                        resp['values'][0].append(random.choice(['Risk', 'No Risk']))
                        resp['values'][0].append([random.uniform(0.01, 0.09)])
                    elif self._ml_engine_type == 'spss':
                        resp['fields'].append('$N-Risk')
                        resp['fields'].append('$NC-Risk')
                        resp['values'][0].append(random.choice(['Risk', 'No Risk']))
                        resp['values'][0].append(random.uniform(0.1, 0.9))
                    score_time = str(self._get_score_time(day, hour))
                    fullRecordsList.append(PayloadRecord(request=req, response=resp, scoring_timestamp=score_time))
        return fullRecordsList

    def get_quality_history(self, num_day):
        return super().get_quality_history(num_day, 0.68, 0.80)