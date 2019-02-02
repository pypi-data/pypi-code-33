#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime


def get_home_budget_data(username, startdate, db):
    data = {}

    with db:
        cur = db.cursor()

        #Find expenditures grouped by date
        cur.execute("SELECT SUM(AMOUNT) as AMOUNT, strftime(\"%d.%m.%Y\", DATE) as DATE FROM HOME_BUDGET_DATA WHERE AMOUNT <= 0 AND DATE >= :date GROUP BY DATE ORDER BY DATE ASC",
                    {'date': startdate})
        costs = []

        last_date = None

        for item in cur.fetchall():
            this_date = datetime.datetime.strptime(item['DATE'], "%d.%m.%Y")
            if(last_date is not None):
                difference = (this_date - last_date).days

                for i in range(1, difference):
                    date = last_date + datetime.timedelta(days=i)
                    costs.append({'date': date.strftime("%d.%m.%Y"), 'amount': round(0, 2)})

            last_date = this_date

            costs.append({'date': item['DATE'], 'amount': round(item['AMOUNT']*-1, 2)})
        data['costs'] = costs

        #Find amount money left
        cur.execute("SELECT SUM(AMOUNT) as AMOUNT FROM HOME_BUDGET_DATA")
        item = cur.fetchone()
        overall_amount = round(item['AMOUNT'], 2)
        data['overall_amount'] = overall_amount

        #Compute date where money reaches 0
        cur.execute("SELECT AVG(AMOUNT) as AMOUNT FROM (SELECT SUM(AMOUNT) as AMOUNT FROM HOME_BUDGET_DATA WHERE AMOUNT < 0 GROUP BY DATE);")
        item = cur.fetchone()
        average_spending_per_day = item['AMOUNT']*-1

        #compute timeperiod
        cur.execute("SELECT MIN(DATE) as mindate, MAX(DATE) as maxdate, COUNT(*) as numdays FROM (SELECT DISTINCT DATE FROM HOME_BUDGET_DATA);")
        min_max_date = cur.fetchone()
        real_numdays = (datetime.datetime.today()-datetime.datetime.strptime(min_max_date['mindate'], "%Y-%m-%d")).days
        average_spending_per_day = average_spending_per_day * min_max_date['numdays'] / real_numdays
        days_left = overall_amount/average_spending_per_day
        date = datetime.datetime.today() + datetime.timedelta(days=days_left)
        date = datetime.datetime.strftime(date, "%d.%m.%Y")
        data['sufficient_until'] = date

    return {'data': data}

def get_home_budget_data_graph(username, startdate, enddate, db):
    with db:
        cur = db.cursor()

        cur.execute("SELECT SUM(AMOUNT) as AMOUNT FROM HOME_BUDGET_DATA WHERE DATE < :startdate;",
            {'startdate': startdate})

        startvalue = cur.fetchone()['AMOUNT']

        if startvalue is None:
            startvalue = 0

        #Get values
        cur.execute("SELECT SUM(AMOUNT) as AMOUNT, strftime(\"%d.%m.%Y\", DATE) as DATE FROM HOME_BUDGET_DATA WHERE DATE >= :startdate AND DATE <= :enddate GROUP BY DATE ORDER BY DATE ASC",
            {'startdate': startdate, 'enddate': enddate})

        values = []

        last_date = None

        for item in cur.fetchall():
            this_date = datetime.datetime.strptime(item['DATE'], "%d.%m.%Y")
            if (last_date is not None):
                difference = (this_date - last_date).days

                for i in range(1, difference):
                    date = last_date + datetime.timedelta(days=i)
                    values.append({'date': date.strftime("%d.%m.%Y"), 'amount': round(0, 2)})

            last_date = this_date

            values.append({'date': item['DATE'], 'amount': round(item['AMOUNT'], 2)})

    return {'startvalue': startvalue, 'values': values}


def get_home_budget_data_day_items(username, date, db):
    data = []

    with db:
        cur = db.cursor()

        cur.execute("SELECT *, strftime(\"%d.%m.%Y\", DATE) as DATE FROM HOME_BUDGET_DATA WHERE DATE = :date ORDER BY DATE ASC",
                    {'date': date})

        for item in cur.fetchall():
            data.append({'id': item['ID'], 'date': item['DATE'], 'amount': round(item['AMOUNT'], 2), 'info': item['INFO']})

    return {'data': data}

def add_edit_home_budget_data(username, id, date, info, amount, db):
    add_new = (id == None or id == "" or id == "-1")

    with db:
        cur = db.cursor()

        if (add_new):
            cur.execute("INSERT INTO HOME_BUDGET_DATA (INFO, AMOUNT, DATE) VALUES (:info, :amount, :date)",
                        {'info': info, 'amount': float(amount), 'date': date})

            return {'result': 'ok'}

        else:
            cur.execute("UPDATE HOME_BUDGET_DATA SET INFO = :info, AMOUNT = :amount, DATE = :date WHERE ID = :id",
                        {'info': info, 'amount': float(amount), 'date': date, 'id': id})

            return {'result': 'ok'}

def delete_home_budget_data(username, id, db):
    with db:
        cur = db.cursor()

        cur.execute("DELETE FROM HOME_BUDGET_DATA WHERE ID = :id", {'id': id})

        return {'result': 'ok'}