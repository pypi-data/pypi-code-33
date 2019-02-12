#!/usr/bin/python3
import datetime
from datetime import date

import pandas as pd


class MasterCalendar():

    def masterCalendar(self, amountOfYearsBack, amountOfYearsForward):
        #set startdate and enddate of the range as variable. Calculate also the start of current year and the startdate of last year
        vStartDate = date(datetime.datetime.now().year-amountOfYearsBack, 1, 1)
        vEndDate = date(datetime.datetime.now().year+amountOfYearsForward, 12, 31)
        vStartDateCurrentYear = pd.to_datetime(date(datetime.datetime.now().year, 1, 1))
        vToday = pd.to_datetime(datetime.datetime.now())
        vStartDateLastYear = pd.to_datetime(date(datetime.datetime.now().year-1, 1, 1))
        vTodayLastYear = pd.to_datetime(date(date.today().year-1, date.today().month, date.today().day))

        #create a column with all the dates between startdate and enddate and name it kalenderdatum
        masterCalendar = pd.date_range(vStartDate, vEndDate, freq='D')
        masterCalendar = pd.DataFrame(data=masterCalendar, columns=['Kalenderdatum'])

        # set all columns like jaar, maand, week, etc. They're all depending on the kalenderdatum.
        masterCalendar['Jaar'] = masterCalendar['Kalenderdatum'].apply(lambda x: int(x.strftime('%Y')))
        masterCalendar['Schooljaar'] = masterCalendar['Kalenderdatum'].apply(lambda x: str(int(x.strftime('%Y'))-1) + '-' + x.strftime('%Y') if x <= datetime.datetime(year=int(x.strftime('%Y')), month=7, day=31) else x.strftime('%Y') + '-' + str(int(x.strftime('%Y'))+1))
        masterCalendar['Maand'] = masterCalendar['Kalenderdatum'].apply(lambda x: x.strftime('%m'))
        masterCalendar['Kwartaal'] = masterCalendar['Maand'].apply(lambda x: (int(x)-1) //3 + 1)
        masterCalendar['Week'] = masterCalendar['Kalenderdatum'].apply(lambda x: x.strftime('%W'))
        masterCalendar['Maand-Jaar'] = masterCalendar['Kalenderdatum'].apply(lambda x: x.strftime('%b-%Y'))
        masterCalendar['Week-Jaar'] = masterCalendar['Kalenderdatum'].apply(lambda x: x.strftime('%W-%Y'))
        masterCalendar['Dag'] = masterCalendar['Kalenderdatum'].apply(lambda x: x.strftime('%A'))
        masterCalendar['CYTDFlag'] = masterCalendar['Kalenderdatum'].apply(lambda x: 1 if x > vStartDateCurrentYear and x <= vToday else 0)
        masterCalendar['LYTDFlag'] = masterCalendar['Kalenderdatum'].apply(lambda x: 1 if x > vStartDateLastYear and x <= vTodayLastYear else 0)

        return masterCalendar
