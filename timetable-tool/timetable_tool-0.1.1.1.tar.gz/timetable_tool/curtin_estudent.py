#!/usr/bin/env python

import datetime
import logging
import sys

import requests
from bs4 import BeautifulSoup

from timetable_tool import constants
from timetable_tool import utilities as utils

logger = logging.getLogger(__name__)


class Session():
    """Form a requests session for Curtin eStudent."""

    def __init__(self):
        self.sess = requests.Session()
        self.current_page = None
        self.current_page_date = None
        self.current_data = self.update_data_tup()

    def update_data_tup(self):
        # Update tuple
        self.current_data = (self.current_page, self.current_page_date)

    # Login
    def login(self, studentid, password):
        r = self.sess.get(constants.LOGIN_URL)
        data = dict(UserName=studentid, Password=password)
        r = self.sess.post(constants.LOGIN_URL, data=data,
                           allow_redirects=False)
        if r.status_code != requests.codes.found:
            logger.info('Login error')
            sys.exit("Exiting...")
        else:
            logger.info('Login successful!')

    # Get today's timetable page by navigating to the monday of
    # this week.
    def navigate_tt_page(self):
        # Navigate to the 'My Studies' tab
        r = self.sess.post(constants.MY_STUDIES_URL)
        # Navigate to the 'eStudent'
        r = self.sess.get(constants.ESTUDENT_URL)
        # Navigate to the 'My Classes' tab
        r = self.sess.get(constants.TIMETABLE_URL)
        # Update current page
        self.current_page = r.text
        # Navigate to today's timetable page
        self.navigate_tt_page_dated(self.get_this_monday())

    def navigate_tt_page_dated(self, date):
        # Convert to compatible date string
        compatible_date = utils.datetime_to_estudent(date)
        # Get page data for navigating
        data = self.make_estudent_happy()
        # Add data to navigate to requested date
        data.update({
            'ctl00$Content$ctlFilter$TxtStartDt': compatible_date,
            'ctl00$Content$ctlFilter$BtnSearch': 'Refresh',
        })
        r = self.sess.post(constants.TIMETABLE_URL,
                           data=data, allow_redirects=False)
        r.raise_for_status()
        # Update current_page
        self.current_page = r.text
        # Update current_page_date
        self.current_page_date = date
        # Update data tuple
        self.update_data_tup()

    def advance_tt_page_one_week(self):
        date = self.current_page_date + datetime.timedelta(days=7)
        self.navigate_tt_page_dated(date)

    def get_this_monday(self):
        monday = datetime.datetime.today(
        ) - datetime.timedelta(days=datetime.datetime.today().weekday())
        return monday

    def make_estudent_happy(self):
        """Extract required form values for POST requests."""
        values = {}
        soup = BeautifulSoup(self.current_page, "lxml")

        for name in '__VIEWSTATE', '__VIEWSTATEGENERATOR', '__EVENTVALIDATION':
            values[name] = soup.find(id=name)['value']
        return values
