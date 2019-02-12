import os
import sys
from logging import Logger
import base64
import pandas as pd
import mandrill
import codecs
import requests
import datetime
from salure_helpers.mysql import MySQL


class SalureFunctions:

    @staticmethod
    def applymap(column: pd.Series, mapping: dict):
        """
        This function maps a given column of a dataframe to new values, according to specified mapping.
        Column types float and int are converted to object because those types can't be compared and changed
        ----------
        :param column: input df on which you want to apply the rename. You should include in the mapping, all
        :return: df with renamed columns
        """
        if column.dtype == 'float64' or column.dtype == 'int64':
            column = column.astype('object')
        if len(mapping) == 0:
            return 'Geen mapping gespecificeerd'
        else:
            column.replace(to_replace=mapping, inplace=True)

            return column

    @staticmethod
    def catch_error(e):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        error = str(e)[:400].replace('\'', '').replace('\"', '') + ' | Line: {}'.format(exc_tb.tb_lineno)
        raise Exception(error)

    @staticmethod
    def scheduler_error_handling(e: Exception, task_id, run_id, mysql_con: MySQL, breaking=True, started_at=None):
        """
        This function handles errors that occur in the scheduler. Logs the traceback, updates run statuses and notifies users
        :param e: the Exception that is to be handled
        :param task_id: The scheduler task id
        :param mysql_con: The connection which is used to update the scheduler task status
        :param logger: The logger that is used to write the logging status to
        :param breaking: Determines if the error is breaking or code will continue
        :param started_at: Give the time the task is started
        :return: nothing
        """
        # Format error to a somewhat readable format
        exc_type, exc_obj, exc_tb = sys.exc_info()
        error = str(e)[:400].replace('\'', '').replace('\"', '') + ' | Line: {}'.format(exc_tb.tb_lineno)
        # Get scheduler task details for logging
        task_details = mysql_con.select('task_scheduler', 'queue_name, runfile_path', 'WHERE id = {}'.format(task_id))[0]
        taskname = task_details[0]
        customer = task_details[1].split('/')[-1].split('.')[0]

        if breaking:
            # Set scheduler status to failed
            mysql_con.update('task_scheduler', ['status', 'last_error_message'], ['IDLE', 'Failed'], 'WHERE `id` = {}'.format(task_id))
            # Log to database
            mysql_con.raw_query("INSERT INTO `task_execution_log` VALUES ({}, {}, 'CRITICAL', '{}', {}, '{}')".format(run_id, task_id, datetime.datetime.now(), exc_tb.tb_lineno, error), insert=True)
            mysql_con.raw_query("INSERT INTO `task_scheduler_log` VALUES ({}, {}, 'Failed', '{}', '{}')".format(run_id, task_id, started_at, datetime.datetime.now()),
                insert=True)
            # Notify users on Slack
            SalureFunctions.send_error_to_slack(customer, taskname, 'failed')
            raise Exception(error)
        else:
            mysql_con.raw_query("INSERT INTO `task_execution_log` VALUES ({}, {}, 'CRITICAL', '{}', {}, '{}')".format(run_id, task_id, datetime.datetime.now(), exc_tb.tb_lineno, error), insert=True)
            SalureFunctions.send_error_to_slack(customer, taskname, 'contains an error')

    @staticmethod
    def convert_empty_columns_type(df: pd.DataFrame):
        """
        Converts the type of columns which are complete empty (not even one value filled) to object. This columns are
        sometimes int or float but that's difficult to work with. Therefore, change always to object
        :param df: input dataframe which must be converted
        :return: dataframe with new column types
        """
        for column in df:
            if df[column].isnull().all():
                df[column] = None

        return df

    @staticmethod
    def dfdate_to_datetime(df: pd.DataFrame, dateformat=None):
        """
        This function processes input dataset and tries to convert all columns to datetime. If this throws an error, it skips the column
        ----------
        :param df: input dataframe for which you want to convert datetime columns
        :param dateformat: optionally specify output format for datetimes. If empty, defaults to %y-%m-%d %h:%m:%s
        :return: returns input df but all date columns formatted according to datetime format specified
        """
        df = df.apply(lambda col: pd.to_datetime(col, errors='ignore') if col.dtypes == object else col, axis=0)
        if format is not None:
            # optional if you want custom date format. Note that this changes column type from date to string
            df = df.apply(lambda col: col.dt.strftime(dateformat) if col.dtypes == 'datetime64[ns]' else col, axis=0)
            df.replace('NaT', '', inplace=True)

        return df

    @staticmethod
    def send_mail(email_to: list, config, subject: str, language='NL', content=None, attachment=None):
        """
        Send a mail with the salureconnect layout and using mandrill
        :param email_to: a list with name and mailadress to who the mail must be send
        :param config: the config file of the project. A mandrill section with at least an api_token, email_from, from_name and email_to with name and mail
        :param subject: The subject of the email
        :param language: Determines the salutation and greeting text. For example Beste or Dear
        :param content: The message of the email
        :param attachment: The attachment of an email loaded as binary file (NOT the location of the file)
        :return: If the sending of the mail is successful or not
        """
        try:
            mandrill_client = mandrill.Mandrill(config.mandrill['api_token'])
            # Load the html template for e-mails
            html_file_location = '{}/templates/mail_salureconnect.html'.format(os.path.dirname(os.path.abspath(__file__)))
            html_file = codecs.open(html_file_location, 'r')
            html = html_file.read()
            opened_attachment = attachment.read()

            if language == 'NL':
                salutation = 'Beste '
                greeting_text = 'Met vriendelijke groet,'
            else:
                salutation = 'Dear '
                greeting_text = 'Kind regards,'

            # Pick the configurations from the config file and create the mail
            for i in email_to:
                new_html = html.replace('{', '{{'). \
                    replace('}', '}}'). \
                    replace('{{subject}}', '{subject}'). \
                    replace('{{title}}', '{title}'). \
                    replace('{{salutation}}', '{salutation}'). \
                    replace('{{name}}', '{name}'). \
                    replace('{{content}}', '{content}'). \
                    replace('{{greeting}}', '{greeting}').format(subject=subject, title=subject, salutation=salutation, name=i['name'], content=content, greeting=greeting_text)
                if attachment == None:
                    mail = {
                        'from_email': config.mandrill['email_from'],
                        'from_name': config.mandrill['name_from'],
                        'subject': subject,
                        'html': new_html,
                        'to': [{'email': i['mail'],
                                'name': i['name'],
                                'type': 'to'}]
                    }
                else:
                    encoded_attachment = base64.b64encode(opened_attachment).decode('utf-8')
                    mail = {
                        'from_email': config.mandrill['email_from'],
                        'from_name': config.mandrill['name_from'],
                        'attachments': [{'content': encoded_attachment,
                                         'name': attachment.name.split('/')[-1]
                                         }],
                        'subject': subject,
                        'html': new_html,
                        'to': [{'email': i['mail'],
                                'name': i['name'],
                                'type': 'to'}]
                    }
                # Send the mail
                mandrill_client.messages.send(message=mail, async=False, ip_pool='Main Pool')
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error = str(e)[:400].replace('\'', '').replace('\"', '') + ' | Line: {}'.format(exc_tb.tb_lineno)
            return Exception(error)

    @staticmethod
    def send_error_to_slack(customer, taskname, message):
        """
        This function is meant to send scheduler errors to slack
        :param customer: Customername where error occured
        :param taskname: Taskname where error occured
        :return: nothing
        """
        message = requests.get('https://slack.com/api/chat.postMessage',
                               params={'channel': 'C04KBG1T2',
                                       'text': 'The reload task of {taskname} from {customer} {message}. Check the {taskname} log for details'.format(customer=customer,
                                                                                                                                                      taskname=taskname,
                                                                                                                                                      message=message),
                                       'username': 'Task Scheduler',
                                       'token': 'xoxp-4502361743-4844095730-47265352212-271109ebd7'}).content
