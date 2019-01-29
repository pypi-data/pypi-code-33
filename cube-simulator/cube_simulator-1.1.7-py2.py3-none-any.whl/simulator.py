__author__ = 'SHASHANK'

from datetime import datetime as dt
from .date_utils import DateUtils
from .flows import *
import json


"""
Assumptions :
    1. PG Transfer Money From midnight to midnight
    2. Timezone is IST
    3. BSE ATIN And BD share same holidays
"""


def setup(transaction_datetime):
    transaction_date = dt.strptime(transaction_datetime, "%Y-%m-%d %H:%M:%S")
    dateutil = DateUtils(transaction_date)
    return dateutil


def setup_for_date(transaction_date):
    dateutil = DateUtils(transaction_date)
    return dateutil


def main(transaction_datetime, basket_items):
    result = []
    dateutil = setup(transaction_datetime)
    rnd = basket_items
    next_date = dateutil.get_next_bank_working_day()
    if int(rnd[0]):
        result.append(execute_cube_iccl_flow(next_date, dateutil))
    if int(rnd[1]):
        result.append(execute_cube_nodal_account_flow(next_date, dateutil))
    if int(rnd[2]):
        result.append(execute_cube_current_account_flow(next_date, dateutil))
    if int(rnd[3]):
        result.append(execute_mf_redemption_flow(next_date, dateutil))
    if int(rnd[4]):
        result.append(execute_faircent_flow(next_date, dateutil))

    return result


def show_result(event_list):
    for key, val in (event_list.__get__().items()):
        print(key.strftime("%Y-%m-%d %H:%M:%S"), val)

    if len(event_list.__get_mf__()) > 0:
        print("\n-----MF----TATS-----\n")
        print(json.dumps(event_list.__get_mf__()))


def getdate(mode, transaction_date, scheme_id, gateway=0):

    #    Nach Transation

    if gateway == 2:

        datee = (transaction_date + timedelta(hours=5, minutes=30))
        dateutils = setup(datee.strftime("%Y-%m-%d %H:%M:%S"))
        debit_date = dateutils.get_next_date_for_nach_file()
        date_str = debit_date.strftime("%Y-%m-%d %H:%M:%S")
        print(date_str)
        if mode == 1:
            event_list, order_dates = main(date_str, "1000")[0]
            try:
                return order_dates[scheme_id]['update_in_app_date'] - timedelta(hours=5, minutes=30, seconds=0)
            except Exception as e:
                return order_dates['Default']['update_in_app_date'] - timedelta(hours=5, minutes=30, seconds=0)

        if mode == 2:
            event_list, order_dates = main(date_str, "0010")[0]
            return order_dates['neft']['update_in_app_date'] - timedelta(hours=5, minutes=30)

        if mode == 3:
            event_list, order_dates = main(date_str, "0100")[0]
            return order_dates['bill']['update_in_app_date'] - timedelta(hours=5, minutes=30)

        if mode == 4:
            date_str = (transaction_date + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
            event_list, order_dates = main(date_str, "0001")[0]
            return order_dates['mfr']['update_in_app_date'] - timedelta(hours=5, minutes=30)

        if mode == 5:
            event_list, order_dates = main(date_str, "00001")[0]
            return order_dates['faircent']['update_in_app_date'] - timedelta(hours=5, minutes=30)

        if mode == 6:
            return transaction_date - timedelta(hours=5, minutes=30)

    #   BD Pg Transation
    elif gateway == 0:

        ### MFP ###
        if mode == 1:
            date_str = (transaction_date + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
            event_list, order_dates = main(date_str, "1000")[0]
            try:
                return order_dates[scheme_id]['update_in_app_date'] - timedelta(hours=5, minutes=30, seconds=0)
            except Exception as e:
                return order_dates['Default']['update_in_app_date'] - timedelta(hours=5, minutes=30, seconds=0)

        ### NODAL ###
        if mode == 2:
            date_str = (transaction_date + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
            event_list, order_dates = main(date_str, "0010")[0]
            return order_dates['neft']['update_in_app_date'] - timedelta(hours=5, minutes=30)

        ### NEFT ###
        if mode == 3:
            date_str = (transaction_date + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
            event_list, order_dates = main(date_str, "0100")[0]
            return order_dates['bill']['update_in_app_date'] - timedelta(hours=5, minutes=30)

        ### MF REDEMPTION ###
        if mode == 4:
            date_str = (transaction_date + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
            event_list, order_dates = main(date_str, "0001")[0]
            return order_dates['mfr']['update_in_app_date'] - timedelta(hours=5, minutes=30)

        ### FAIRCENT ###
        if mode == 5:
            date_str = (transaction_date + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
            event_list, order_dates = main(date_str, "00001")[0]
            return order_dates['faircent']['update_in_app_date'] - timedelta(hours=5, minutes=30)

        if mode == 6:
            return transaction_date - timedelta(hours=5, minutes=30)

    #   WA Transation
    elif gateway == 4:
        if mode == 1:
            date_str = (transaction_date + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
            event_list, order_dates = main(date_str, "1000")[0]
            try:
                return order_dates[scheme_id]['update_in_app_date'] - timedelta(hours=5, minutes=30, seconds=0)
            except Exception as e:
                return order_dates['Default']['update_in_app_date'] - timedelta(hours=5, minutes=30, seconds=0)

        if mode == 2:
            date_str = (transaction_date + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
            event_list, order_dates = main(date_str, "0010")[0]
            return order_dates['neft']['update_in_app_date'] - timedelta(hours=5, minutes=30)

        if mode == 3:
            date_str = (transaction_date + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
            event_list, order_dates = main(date_str, "0100")[0]
            return order_dates['bill']['update_in_app_date'] - timedelta(hours=5, minutes=30)

        if mode == 4:
            date_str = (transaction_date + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
            event_list, order_dates = main(date_str, "0001")[0]
            return order_dates['mfr']['update_in_app_date'] - timedelta(hours=5, minutes=30)

        if mode == 5:
            date_str = (transaction_date + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
            event_list, order_dates = main(date_str, "00001")[0]
            return order_dates['faircent']['update_in_app_date'] - timedelta(hours=5, minutes=30)

        if mode == 6:
            return transaction_date - timedelta(hours=5, minutes=30)

    #   Withdrawls
    else:
        if mode == 1:
            date_str = (transaction_date + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
            event_list, order_dates = main(date_str, "1000")[0]
            try:
                return order_dates[scheme_id]['update_in_app_date'] - timedelta(hours=5, minutes=30, seconds=0)
            except Exception as e:
                return order_dates['Default']['update_in_app_date'] - timedelta(hours=5, minutes=30, seconds=0)

        if mode == 2:
            date_str = (transaction_date + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
            event_list, order_dates = main(date_str, "0010")[0]
            return order_dates['neft']['update_in_app_date'] - timedelta(hours=5, minutes=30)

        if mode == 3:
            date_str = (transaction_date + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
            event_list, order_dates = main(date_str, "0100")[0]
            return order_dates['bill']['update_in_app_date'] - timedelta(hours=5, minutes=30)

        if mode == 4:
            date_str = (transaction_date + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
            event_list, order_dates = main(date_str, "0001")[0]
            return order_dates['mfr']['update_in_app_date'] - timedelta(hours=5, minutes=30)

        if mode == 5:
            return transaction_date

        if mode == 6:
            return transaction_date - timedelta(hours=5, minutes=30)


if __name__ == "__main__":
    # main(sys.argv[1] + " " + sys.argv[2], sys.argv[3])

    from dateutil.parser import parse
    date = parse("2018-08-21 11:30:29")
    getdate(1, date, 8, 2)