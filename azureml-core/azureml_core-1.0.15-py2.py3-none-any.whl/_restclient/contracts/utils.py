# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# ---------------------------------------------------------

"""contracts utilities"""

import uuid
import datetime
import pytz
from azureml._restclient.constants import RUN_ID_EXPRESSION


DATE_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


def get_new_id():
    """create an uuid string"""
    return str(uuid.uuid4())


def get_timestamp(return_as_string=True):
    """create a time stamp"""
    # Setting microsecond to 0, this removes the millisecond the resulting
    # string is formatted as YYYY-MM-DDTHH:MM:SS+HH:MM
    # https://stackoverflow.com/questions/2150739/
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    if return_as_string:
        now = now.strftime(DATE_TIME_FORMAT)
    return now


def get_run_ids_filter_expression(run_ids):
    """get run ids filter expression"""
    sep = " or "
    run_filter = [(RUN_ID_EXPRESSION + run_id) for run_id in run_ids]
    return sep.join(run_filter)
