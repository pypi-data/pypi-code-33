import os
import sys
basedir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(basedir)
from salure_helpers.salure_functions import SalureFunctions
from salure_helpers.mysql import MySQL
import datetime
import traceback
import pandas as pd
from dotenv import load_dotenv
load_dotenv(basedir + '\.env')

# TODO: voeg elke connector toe aan 1 bestand om vandaar uit te starten
# TODO: elke connector op een eigen te kiezen tijdstip met een eigen te kiezen frequentie kunnen starten
# TODO: errors identiek afvangen en naar Slack sturen
# TODO: logging generiek opbouwen dat deze voor elke connector te gebruiken is
# TODO: als een task niet heeft gerund, dan een message naar Slack sturen dat task niet heeft gerund


class TaskScheduler:

    def __init__(self, customer, task_name, start_time, frequency):
        self.customer = customer
        self.task_name = task_name
        self.start_time = start_time
        self.frequency = frequency
        self.mysql = MySQL(os.environ.get('MYSQL_HOST'),
                           os.environ.get('MYSQL_USER'),
                           os.environ.get('MYSQL_PASSWORD'),
                           os.environ.get('MYSQL_DATABASE'))
        self.slack = SalureFunctions.send_error_to_slack(os.environ.get('SLACK_TOKEN'),
                           os.environ.get('SLACK_CHANNEL'),
                           os.environ.get('SLACK_USER'))

    def run_all(self):
        epoch_start = int(datetime.datetime.now().timestamp()) * 1000
        try:
            self.run_connector()
            self.logging(epoch_start)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error = str(e)[:400].replace('\'', '').replace('\"', '') + ' | Line: {}'.format(exc_tb.tb_lineno)
            stacktrace = traceback.format_exc()
            epoch_end = int(datetime.datetime.now().timestamp()) * 1000
            log_message = [{'customer': self.customer,
                            'task': self.task_name,
                            'start_time': epoch_start,
                            'end_time': epoch_end,
                            'success': False,
                            'message': '{}'.format(error)}]
            df = pd.DataFrame(log_message)

            # Store error in database en send to Slack
            self.mysql.insert('connectors_log', df)
            self.slack.send_errors('customer: {} - task: {}'.format(self.customer, self.task_name), stacktrace)


    def run_connector(self):
        pass


    def logging(self, epoch_start):
        epoch_end = int(datetime.datetime.now().timestamp()) * 1000

        log_message = [{'customer': self.customer,
                        'task': self.task_name,
                        'start_time': epoch_start,
                        'end_time': epoch_end,
                        'success': True,
                        'message': 'NA'}]
        df = pd.DataFrame(log_message)
        self.mysql.insert('connectors_log', df)

        epoch_filter_success = int(datetime.datetime.now().timestamp()) * 1000 - (3600 * 1000 * 24 * 62)
        epoch_filter_failed = int(datetime.datetime.now().timestamp()) * 1000 - (3600 * 1000 * 24 * 128)
        # Delete all loglines older as 1 hour if status is success or older as 3 days if status is failed
        self.mysql.delete('connectors_log', 'WHERE task = \'{}\' AND ((end_time <= {} AND success = True) OR (end_time <= {} AND success = False))'.format(
            self.task_name, epoch_filter_success, epoch_filter_failed))