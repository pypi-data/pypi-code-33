from datetime import timedelta, datetime

import pendulum


def get_last_hour_epoch():
    return int((datetime.now() - timedelta(hours=1)).timestamp() * 1000)


def get_current_epoch():
    return int(datetime.now().timestamp() * 1000)


def get_last_hour():
    return pendulum.now().add(hours=-1).to_iso8601_string()


def get_current_datetime():
    return pendulum.now().to_iso8601_string()


def get_date_today():
    return pendulum.today().to_iso8601_string()


def daterange(start_date, end_date):
    for day in range(int((end_date - start_date).days)):
        yield start_date + timedelta(day)


def get_date_from_string(date_string):
    return pendulum.parse(date_string)
