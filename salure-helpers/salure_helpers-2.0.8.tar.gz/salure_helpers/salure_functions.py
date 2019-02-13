import sys
import pandas as pd
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
