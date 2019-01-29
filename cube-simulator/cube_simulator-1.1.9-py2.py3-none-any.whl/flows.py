__author__ = 'SHASHANK'
from datetime import timedelta
from .constants import MF_ALLOTMENT_TAT
from collections import OrderedDict


def execute_cube_current_account_flow(date, dateutils):
    trans_date = dateutils.get_current_day()
    money_received = date
    event_list = {
        'money_debit_ts': trans_date,
        'neft_file_ts': trans_date.replace(hour=int(10), minute=int(00), second=int(0)) + timedelta(days=1),
        'cube_current_money_credit_ts': dateutils.get_next_bank_working_day().replace(hour=int(17), minute=int(00), second=int(0)),
        'bd_claim_ts': money_received + timedelta(hours=2)
    }

    order_dates_list = {
        'neft': {
            'update_in_app_date': dateutils.get_next_bank_working_day().replace(hour=int(19), minute=int(00), second=int(0))
        }
    }

    return event_list, order_dates_list


def execute_cube_nodal_account_flow(date, dateutils):

    trans_date = dateutils.get_current_day()
    order_dates_list = {
        'bill': {
            'update_in_app_date': trans_date
        }
    }
    money_received = dateutils.get_next_bse_working_day()
    event_list = {
        'money_debit_ts': trans_date,
        'recon_file_ts': trans_date.replace(hour=int(6), minute=int(30), second=int(0)) + timedelta(days=1),
        'cube_nodal_money_credit_ts': dateutils.get_next_bank_working_day().replace(hour=int(13), minute=int(30), second=int(0)),
        'bd_claim_ts': money_received.replace(hour=int(14), minute=int(30), second=int(0))
    }

    return event_list, order_dates_list


def execute_cube_iccl_flow(date, dateutils):
    money_received = date
    trans_date = dateutils.get_current_day()
    money_received_time = money_received.replace(hour=int(13), minute=int(30), second=int(0))
    settlement_file_generation = (trans_date + timedelta(1)).replace(hour=int(15), minute=int(15), second=int(0))

    event_list = {
        'money_debit_ts': trans_date,
        'iccl_money_credit_ts': money_received_time,
        'settlement_file_generation_ts': settlement_file_generation
    }

    order_dates_list = OrderedDict()
    for key, value in MF_ALLOTMENT_TAT.items():
        additional_delta_days = value[0]
        allotment_tat = value[1]
        ex_date = dateutils.get_next_bse_working_day(1+additional_delta_days)
        ex_date_1 = dateutils.get_next_bse_working_day(1+additional_delta_days+allotment_tat)

        result_set = {
            'order_placed_date': dateutils.get_next_bse_working_day(),
            'order_date': ex_date,
            'nav_date': ex_date.replace(hour=00, minute=00),
            'allotment_date': ex_date_1.replace(hour=17, minute=00),
            'update_in_app_date': ex_date_1.replace(hour=17, minute=30)
        }

        order_dates_list[key] = result_set

    return event_list, order_dates_list


def execute_cube_iccl_flow(date, dateutils):
    money_received = date
    trans_date = dateutils.get_current_day()
    money_received_time = money_received.replace(hour=int(13), minute=int(30), second=int(0))
    settlement_file_generation = (trans_date + timedelta(1)).replace(hour=int(15), minute=int(15), second=int(0))

    event_list = {
        'money_debit_ts': trans_date,
        'iccl_money_credit_ts': money_received_time,
        'settlement_file_generation_ts': settlement_file_generation
    }

    order_dates_list = OrderedDict()
    for key, value in MF_ALLOTMENT_TAT.items():
        additional_delta_days = value[0]
        allotment_tat = value[1]
        ex_date = dateutils.get_next_bse_working_day(1+additional_delta_days)
        ex_date_1 = dateutils.get_next_bse_working_day(1+additional_delta_days+allotment_tat)

        result_set = {
            'order_placed_date': dateutils.get_next_bse_working_day(),
            'order_date': ex_date,
            'nav_date': ex_date.replace(hour=00, minute=00),
            'allotment_date': ex_date_1.replace(hour=17, minute=00),
            'update_in_app_date': ex_date_1.replace(hour=17, minute=30)
        }

        order_dates_list[key] = result_set

    return event_list, order_dates_list


def execute_mf_redemption_flow(date, dateutils):
    trans_date = dateutils.get_current_day()
    order_placed_date = trans_date
    if order_placed_date <= trans_date.replace(hour=9, minute=30, second=0):
        order_dates_list = {
            'mfr': {
                'order_placed_date': trans_date,
                'order_date': trans_date,
                'nav_date': dateutils.get_next_bse_working_day(),
                'allotment_date': dateutils.get_next_bse_working_day(),
                'update_in_app_date': dateutils.get_next_bse_working_day()
            }
        }
    else:
        order_dates_list = {
            'mfr': {
                'order_placed_date': trans_date,
                'order_date': dateutils.get_next_bse_working_day(),
                'nav_date': dateutils.get_next_bse_working_day(),
                'allotment_date': dateutils.get_next_bse_working_day(2),
                'update_in_app_date': dateutils.get_next_bse_working_day(),
            }
        }

    return {}, order_dates_list


def execute_faircent_flow(date, dateutils):
    trans_date = dateutils.get_current_day()
    order_dates_list = {
        'faircent': {
            'order_placed_date': trans_date,
            'order_date': trans_date,
            'nav_date': dateutils.get_next_bse_working_day(),
            'allotment_date': dateutils.get_next_bse_working_day(),
            'update_in_app_date': dateutils.get_next_bse_working_day()
        }
    }

    return {}, order_dates_list