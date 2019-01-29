__author__ = 'SHASHANK'

from datetime import datetime, timedelta
from .constants import BANK_HOLIDAYS, BSE_HOLIDAYS
from dateutil import rrule


class DateUtils:

    def __init__(self, transation_date):

        self.init_date = transation_date

        # setting up bank calender#
        r = rrule.rrule(rrule.YEARLY,
                        byweekday=[rrule.MO, rrule.TU, rrule.WE, rrule.TH, rrule.FR, rrule.SA],
                        dtstart=datetime.strptime("2019-01-01", "%Y-%m-%d"))
        rs = rrule.rruleset()
        [rs.exdate(datetime.strptime(HOLIDAY, "%Y-%m-%d")) for HOLIDAY in BANK_HOLIDAYS]
        rs.rrule(r)
        self.daterules_bank = rs
        self.init_date_index_bank = -1
        counter = 0

        if transation_date < datetime.strptime("2019-01-01", "%Y-%m-%d") < datetime.strptime("2020-01-01", "%Y-%m-%d"):
            raise ValueError("Transaction Date is out of 1 year window")

        while True:
            for i in self.daterules_bank._iter():
                if counter == 366:
                    break
                if i == transation_date.replace(hour=0, minute=0, second=0):
                    self.init_date_index_bank = counter
                    break
                counter += 1
            if counter == 366:
                transation_date = transation_date + timedelta(days=-1)
                counter = 0
            else:
                break

        # setting up bse calender #
        transation_date = self.init_date
        rb = rrule.rrule(rrule.YEARLY,
                         byweekday=[rrule.MO, rrule.TU, rrule.WE, rrule.TH, rrule.FR],
                         dtstart=datetime.strptime("2019-01-01", "%Y-%m-%d"))
        rsb = rrule.rruleset()
        [rsb.exdate(datetime.strptime(HOLIDAY, "%Y-%m-%d")) for HOLIDAY in BSE_HOLIDAYS]
        rsb.rrule(rb)
        self.daterules_bse = rsb
        self.init_date_index_bse = -1
        counter = 0

        if transation_date < datetime.strptime("2019-01-01", "%Y-%m-%d") < datetime.strptime("2020-01-01", "%Y-%m-%d"):
            raise ValueError("Transaction Date is out of 1 year window")

        while True:
            for i in self.daterules_bse._iter():
                if counter == 366:
                    break
                if i == transation_date.replace(hour=0, minute=0, second=0):
                    self.init_date_index_bse = counter
                    break
                counter += 1
            if counter == 366:
                transation_date = transation_date + timedelta(days=-1)
                counter = 0
            else:
                break

    def get_next_bank_working_day(self, days=1):
        (hour, min, sec) = self.init_date.strftime("%H:%m:%S").split(':')
        return self.daterules_bank[self.init_date_index_bank + days].replace(hour=int(hour), minute=int(min), second=int(sec))

    def get_current_day(self):
        return self.init_date

    def get_next_bse_working_day(self, days=1):
        (hour, min, sec) = self.init_date.strftime("%H:%m:%S").split(':')
        return self.daterules_bse[self.init_date_index_bse + days].replace(hour=int(hour), minute=int(min), second=int(sec))

    def get_next_date_for_nach_file(self):
        (hour, min, sec) = self.init_date.strftime("%H:%m:%S").split(':')
        if self.init_date.date() == self.get_next_bse_working_day(0).date():
            if self.init_date < self.init_date.replace(hour=int(15), minute=int(30), second=int(0)):
                return self.get_next_bse_working_day(3)
            else:
                return self.get_next_bse_working_day(4)
        else:
            return self.get_next_bse_working_day(4)
