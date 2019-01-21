# coding: utf-8
__version__ = '1.0.0'

"""
    Eikon Data API for Python allows your Python applications to access Refinitiv data directly from Eikon.
    It's usage requires:
        - An App Key (you can create it wit App Key Generator in Eikon Desktop)
        - Eikon Desktop application running on your local machine

"""

from .Profile import set_app_key, get_app_key,\
    set_timeout, get_timeout, \
    set_port_number, get_port_number,\
    set_log_level, set_log_path,\
    set_app_id, get_app_id
from .symbology import get_symbology
from .json_requests import send_json_request
from .news_request import get_news_headlines, get_news_story
from .time_series import get_timeseries
from .data_grid import get_data, TR_Field
from .eikonError import EikonError




