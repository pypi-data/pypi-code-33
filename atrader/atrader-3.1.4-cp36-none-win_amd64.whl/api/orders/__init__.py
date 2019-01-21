# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 15:10:02 2018

@author: kunlin.l
"""

import numpy as np
import atrader.enums as enums
from atrader.tframe import sysclsbase as cnt
from atrader.tframe.udefs import NONETYPE, INTEGERSTYPE
from atrader.tframe.sysclsbase import smm
from atrader.tframe.sysclsbase import gv
from atrader.tframe.utils.argchecker import apply_rule, verify_that

__all__ = [
    'order_volume',
    'order_value',
    'order_percent',
    'order_target_volume',
    'order_target_value',
    'order_close_all',
    'order_cancel_all',
    'order_cancel',
    'order_target_percent',
    'stop_trailing_by_order',
    'stop_cancel',
    'stop_profit_by_order',
    'stop_loss_by_order',
    'get_stop_info',
    'get_daily_orders',
    'get_last_execution',
    'get_unfinished_orders',
    'get_daily_executions',
    'get_order_info',
    'get_last_order',
]


#################################
# 交易函数: 普通下单指令
@smm.force_mode(gv.RUNMODE_BACKTEST, gv.RUNMODE_REALTRADE)
@smm.force_phase(gv.RUMMODE_PHASE_ONDATA)
@apply_rule(verify_that('account_idx').is_instance_of(*INTEGERSTYPE),
            verify_that('target_idx').is_instance_of(*INTEGERSTYPE),
            verify_that('volume').is_instance_of(*INTEGERSTYPE),
            verify_that('side').is_in((enums.ORDERSIDE_BUY, enums.ORDERSIDE_SELL)),
            verify_that('position_effect').is_in((enums.ORDERPOSITIONEFFECT_OPEN,
                                                  enums.ORDERPOSITIONEFFECT_CLOSE,
                                                  enums.ORDERPOSITIONEFFECT_CLOSETODAY)),
            verify_that('order_type').is_in((enums.ORDERTYPE_LIMIT,
                                             enums.ORDERTYPE_MARKET)),
            verify_that('price').is_greater_or_equal_than(0))
def order_volume(account_idx: 'int',
                 target_idx: 'int',
                 volume: 'int',
                 side: 'int',
                 position_effect: 'int',
                 order_type: 'int',
                 price=0.0):
    account_idx, target_idx = cnt.env.check_idx('order_volume', account_idx, target_idx, toarray=False)
    return cnt.env.diff_api.order_volume(account_idx, target_idx, volume, side, position_effect, order_type, price)


@smm.force_mode(gv.RUNMODE_BACKTEST, gv.RUNMODE_REALTRADE)
@smm.force_phase(gv.RUMMODE_PHASE_ONDATA)
@apply_rule(verify_that('account_idx').is_instance_of(*INTEGERSTYPE),
            verify_that('target_idx').is_instance_of(*INTEGERSTYPE),
            verify_that('value').is_greater_than(0),
            verify_that('side').is_in((enums.ORDERSIDE_BUY, enums.ORDERSIDE_SELL)),
            verify_that('position_effect').is_in((enums.ORDERPOSITIONEFFECT_OPEN,
                                                  enums.ORDERPOSITIONEFFECT_CLOSE,
                                                  enums.ORDERPOSITIONEFFECT_CLOSETODAY)),
            verify_that('order_type').is_in((enums.ORDERTYPE_LIMIT,
                                             enums.ORDERTYPE_MARKET,
                                             enums.ORDERTYPE_FAK,
                                             enums.ORDERTYPE_FOK,
                                             enums.ORDERTYPE_BOC,
                                             enums.ORDERTYPE_BOP,
                                             enums.ORDERTYPE_B5TC,
                                             enums.ORDERTYPE_B5TL)),
            verify_that('price').is_greater_or_equal_than(0))
def order_value(account_idx: 'int',
                target_idx: 'int',
                value: 'float',
                side: 'int',
                position_effect: 'int',
                order_type: 'int',
                price=0.0):
    account_idx, target_idx = cnt.env.check_idx('order_value', account_idx, target_idx, toarray=False)
    return cnt.env.diff_api.order_value(account_idx, target_idx, value, side, position_effect, order_type, price)


@smm.force_mode(gv.RUNMODE_BACKTEST, gv.RUNMODE_REALTRADE)
@smm.force_phase(gv.RUMMODE_PHASE_ONDATA)
@apply_rule(verify_that('account_idx').is_instance_of(*INTEGERSTYPE),
            verify_that('target_idx').is_instance_of(*INTEGERSTYPE),
            verify_that('percent').is_greater_than(0).is_less_or_equal_than(1),
            verify_that('side').is_in((enums.ORDERSIDE_BUY,
                                       enums.ORDERSIDE_SELL)),
            verify_that('position_effect').is_in((enums.ORDERPOSITIONEFFECT_OPEN,
                                                  enums.ORDERPOSITIONEFFECT_CLOSE,
                                                  enums.ORDERPOSITIONEFFECT_CLOSETODAY)),
            verify_that('order_type').is_in((enums.ORDERTYPE_LIMIT,
                                             enums.ORDERTYPE_MARKET,
                                             enums.ORDERTYPE_FAK,
                                             enums.ORDERTYPE_FOK,
                                             enums.ORDERTYPE_BOC,
                                             enums.ORDERTYPE_BOP,
                                             enums.ORDERTYPE_B5TC,
                                             enums.ORDERTYPE_B5TL)),
            verify_that('price').is_greater_or_equal_than(0))
def order_percent(account_idx: 'int',
                  target_idx: 'int',
                  percent: 'float',
                  side: 'int',
                  position_effect: 'int',
                  order_type: 'int',
                  price=0.0):
    account_idx, target_idx = cnt.env.check_idx('order_percent', account_idx, target_idx, toarray=False)
    return cnt.env.diff_api.order_percent(account_idx, target_idx, percent, side, position_effect, order_type, price)


#################################

# 交易函数: 目标下单指令

@smm.force_mode(gv.RUNMODE_BACKTEST, gv.RUNMODE_REALTRADE)
@smm.force_phase(gv.RUMMODE_PHASE_ONDATA)
@apply_rule(verify_that('account_idx').is_instance_of(*INTEGERSTYPE),
            verify_that('target_idx').is_instance_of(*INTEGERSTYPE),
            verify_that('target_volume').is_instance_of(*INTEGERSTYPE).is_greater_or_equal_than(0),
            verify_that('side').is_in((enums.POSITIONSIDE_LONG, enums.POSITIONSIDE_SHORT)),
            verify_that('order_type').is_in((enums.ORDERTYPE_LIMIT,
                                             enums.ORDERTYPE_MARKET,
                                             enums.ORDERTYPE_FAK,
                                             enums.ORDERTYPE_FOK,
                                             enums.ORDERTYPE_BOC,
                                             enums.ORDERTYPE_BOP,
                                             enums.ORDERTYPE_B5TC,
                                             enums.ORDERTYPE_B5TL)),
            verify_that('price').is_greater_or_equal_than(0))
def order_target_volume(account_idx: 'int',
                        target_idx: 'int',
                        target_volume: 'int',
                        side: 'int',
                        order_type: 'int',
                        price=0.0):
    handle_idx, target_idx = cnt.env.check_idx('order_target_volume', account_idx, target_idx, toarray=False)
    return cnt.env.diff_api.order_target_volume(account_idx, target_idx, target_volume, side, order_type, price)


@smm.force_mode(gv.RUNMODE_BACKTEST, gv.RUNMODE_REALTRADE)
@smm.force_phase(gv.RUMMODE_PHASE_ONDATA)
@apply_rule(verify_that('account_idx').is_instance_of(*INTEGERSTYPE),
            verify_that('target_idx').is_instance_of(*INTEGERSTYPE),
            verify_that('target_value').is_greater_or_equal_than(0),
            verify_that('side').is_in((enums.POSITIONSIDE_SHORT, enums.POSITIONSIDE_LONG)),
            verify_that('order_type').is_in((enums.ORDERTYPE_LIMIT,
                                             enums.ORDERTYPE_MARKET,
                                             enums.ORDERTYPE_FAK,
                                             enums.ORDERTYPE_FOK,
                                             enums.ORDERTYPE_BOC,
                                             enums.ORDERTYPE_BOP,
                                             enums.ORDERTYPE_B5TC,
                                             enums.ORDERTYPE_B5TL)),
            verify_that('price').is_greater_or_equal_than(0))
def order_target_value(account_idx: 'int',
                       target_idx: 'int',
                       target_value: 'float',
                       side: 'int',
                       order_type: 'int',
                       price=0.0):
    handle_idx, target_idx = cnt.env.check_idx('order_target_value', account_idx, target_idx, toarray=False)
    return cnt.env.diff_api.order_target_value(account_idx, target_idx, target_value, side, order_type, price)


@smm.force_mode(gv.RUNMODE_BACKTEST, gv.RUNMODE_REALTRADE)
@smm.force_phase(gv.RUMMODE_PHASE_ONDATA)
@apply_rule(verify_that('account_idx').is_instance_of(*INTEGERSTYPE),
            verify_that('target_idx').is_instance_of(*INTEGERSTYPE),
            verify_that('target_percent').is_greater_or_equal_than(0),
            verify_that('side').is_in((enums.ORDERSIDE_BUY, enums.ORDERSIDE_SELL)),
            verify_that('order_type').is_in((enums.ORDERTYPE_LIMIT,
                                             enums.ORDERTYPE_MARKET,
                                             enums.ORDERTYPE_FAK,
                                             enums.ORDERTYPE_FOK,
                                             enums.ORDERTYPE_BOC,
                                             enums.ORDERTYPE_BOP,
                                             enums.ORDERTYPE_B5TC,
                                             enums.ORDERTYPE_B5TL)),
            verify_that('price').is_greater_or_equal_than(0))
def order_target_percent(account_idx: 'int',
                         target_idx: 'int',
                         target_percent: 'float',
                         side: 'int',
                         order_type: 'int',
                         price=0.0):
    handle_idx, target_idx = cnt.env.check_idx('order_target_percent', account_idx, target_idx, toarray=False)
    return cnt.env.diff_api.order_target_percent(account_idx, target_idx, target_percent, side, order_type, price)


#################################

# 交易函数: 撤销委托指令

@smm.force_phase(gv.RUMMODE_PHASE_ONDATA)
@apply_rule(verify_that('order_list').is_instance_of(list))
def order_cancel(order_list: 'list'):
    return cnt.env.diff_api.order_cancel(order_list)


@smm.force_mode(gv.RUNMODE_BACKTEST, gv.RUNMODE_REALTRADE)
@smm.force_phase(gv.RUMMODE_PHASE_ONDATA)
@apply_rule(verify_that('account_indice').is_instance_of(*INTEGERSTYPE, list, tuple))
def order_cancel_all(account_indice=(0,)):
    if isinstance(account_indice, INTEGERSTYPE):
        account_indice = [account_indice]
    account_indice, _ = cnt.env.check_idx('account_indice', account_indice, None, toarray=False)
    return cnt.env.diff_api.order_cancel_all(account_indice)


#################################

# 交易函数: 一键平仓指令
@smm.force_mode(gv.RUNMODE_BACKTEST, gv.RUNMODE_REALTRADE)
@smm.force_phase(gv.RUMMODE_PHASE_ONDATA)
@apply_rule(verify_that('account_indice').is_instance_of(*INTEGERSTYPE, list, tuple))
def order_close_all(account_indice=(0,)):
    if isinstance(account_indice, INTEGERSTYPE):
        account_indice = [account_indice]
    account_indice, _ = cnt.env.check_idx('account_indice', account_indice, None, toarray=False)
    return cnt.env.diff_api.order_close_all(account_indice)


#################################

# 交易函数: 委托单查询函数
@smm.force_mode(gv.RUNMODE_BACKTEST, gv.RUNMODE_REALTRADE)
@smm.force_phase(gv.RUMMODE_PHASE_ONDATA)
@apply_rule(verify_that('order_list').is_instance_of(*INTEGERSTYPE, list, tuple),
            verify_that('account_indice').is_instance_of(*INTEGERSTYPE, list, tuple))
def get_order_info(order_list=(), account_indice=(0,)):
    if isinstance(order_list, INTEGERSTYPE):
        order_list = [order_list]
    if isinstance(account_indice, INTEGERSTYPE):
        account_indice = [account_indice]
    account_indice, _ = cnt.env.check_idx('account_indice', account_indice, None, toarray=False)
    strategy_input = cnt.env.get_strategy_input()
    ls = cnt.env.diff_api.order_info(order_list, account_indice)
    return cnt.env.diff_cvt.convert_order_to_df(ls,
                                                strategy_input['AccountNameList'],
                                                strategy_input['TargetList'])


@smm.force_mode(gv.RUNMODE_BACKTEST, gv.RUNMODE_REALTRADE)
@smm.force_phase(gv.RUMMODE_PHASE_ONDATA)
@apply_rule(verify_that('account_indice').is_instance_of(*INTEGERSTYPE, list, tuple))
def get_unfinished_orders(account_indice=(0,)):
    if isinstance(account_indice, INTEGERSTYPE):
        account_indice = [account_indice]
    account_indice, _ = cnt.env.check_idx('account_indice', account_indice, None, toarray=False)
    bar_date_s = {int(cnt.env.fresh_bar_time)}
    ls = cnt.env.diff_api.unfinished_orders(bar_date_s, account_indice)
    strategy_input = cnt.env.get_strategy_input()
    return cnt.env.diff_cvt.convert_unfinished_orders_to_df(ls,
                                                            strategy_input['AccountNameList'],
                                                            strategy_input['TargetList'])


@smm.force_mode(gv.RUNMODE_BACKTEST, gv.RUNMODE_REALTRADE)
@smm.force_phase(gv.RUMMODE_PHASE_ONDATA)
@apply_rule(verify_that('account_indice').is_instance_of(*INTEGERSTYPE, list, tuple))
def get_daily_orders(account_indice=(0,)):
    if isinstance(account_indice, INTEGERSTYPE):
        account_indice = [account_indice]
    bar_date_s = {int(cnt.env.fresh_bar_time)}
    ls = cnt.env.diff_api.get_orders_by_date(bar_date_s, account_indice)
    strategy_input = cnt.env.get_strategy_input()
    return cnt.env.diff_cvt.convert_daily_orders_to_df(ls,
                                                       strategy_input['AccountNameList'],
                                                       strategy_input['TargetList'])


@smm.force_mode(gv.RUNMODE_BACKTEST, gv.RUNMODE_REALTRADE)
@smm.force_phase(gv.RUMMODE_PHASE_ONDATA)
@apply_rule(verify_that('account_idx').is_instance_of(*INTEGERSTYPE),
            verify_that('target_idx').is_instance_of(*INTEGERSTYPE),
            verify_that('side').is_in((enums.ORDERSIDE_UNKNOWN,
                                       enums.ORDERSIDE_BUY,
                                       enums.ORDERSIDE_SELL)),
            verify_that('position_effect').is_in((enums.ORDERPOSITIONEFFECT_UNKNOWN,
                                                  enums.ORDERPOSITIONEFFECT_OPEN,
                                                  enums.ORDERPOSITIONEFFECT_CLOSE,
                                                  enums.ORDERPOSITIONEFFECT_CLOSETODAY)))
def get_last_order(account_idx=0,
                   target_idx=0,
                   side=enums.ORDERSIDE_UNKNOWN,
                   position_effect=enums.ORDERPOSITIONEFFECT_UNKNOWN):
    handle_idx, target_idx = cnt.env.check_idx('get_last_order', account_idx, target_idx, toarray=False)
    side_set = {side}
    position_effect_set = {position_effect}

    if side == enums.ORDERSIDE_UNKNOWN:
        side_set = {enums.ORDERSIDE_BUY,
                    enums.ORDERSIDE_SELL}

    if position_effect == enums.ORDERPOSITIONEFFECT_UNKNOWN:
        position_effect_set = {enums.ORDERPOSITIONEFFECT_OPEN,
                               enums.ORDERPOSITIONEFFECT_CLOSE,
                               enums.ORDERPOSITIONEFFECT_CLOSETODAY}

    ls = cnt.env.diff_api.last_order(handle_idx, target_idx, side_set, position_effect_set)
    if len(ls) < 1:
        return None
    strategy_input = cnt.env.get_strategy_input()
    return cnt.env.diff_cvt.convert_last_order_to_df(ls,
                                                     strategy_input['AccountNameList'],
                                                     strategy_input['TargetList'])


#################################

# 成交查询

@smm.force_mode(gv.RUNMODE_BACKTEST, gv.RUNMODE_REALTRADE)
@smm.force_phase(gv.RUMMODE_PHASE_ONDATA)
@apply_rule(verify_that('account_indice').is_instance_of(*INTEGERSTYPE, list, tuple))
def get_daily_executions(account_indice=(0,)):
    if isinstance(account_indice, INTEGERSTYPE):
        account_indice = [account_indice]
    bar_date_s = {int(cnt.env.fresh_bar_time)}
    ls = cnt.env.diff_api.get_executions(bar_date_s, account_indice)
    if len(ls) < 1:
        return None
    strategy_input = cnt.env.get_strategy_input()
    return cnt.env.diff_cvt.convert_daily_executions_to_df(ls,
                                                           strategy_input['AccountNameList'],
                                                           strategy_input['TargetList'])


@smm.force_mode(gv.RUNMODE_BACKTEST, gv.RUNMODE_REALTRADE)
@smm.force_phase(gv.RUMMODE_PHASE_ONDATA)
@apply_rule(verify_that('account_idx').is_instance_of(*INTEGERSTYPE),
            verify_that('target_idx').is_instance_of(*INTEGERSTYPE),
            verify_that('side').is_in((enums.ORDERSIDE_UNKNOWN,
                                       enums.ORDERSIDE_BUY,
                                       enums.ORDERSIDE_SELL)),
            verify_that('position_effect').is_in((enums.ORDERPOSITIONEFFECT_UNKNOWN,
                                                  enums.ORDERPOSITIONEFFECT_OPEN,
                                                  enums.ORDERPOSITIONEFFECT_CLOSE,
                                                  enums.ORDERPOSITIONEFFECT_CLOSETODAY)))
def get_last_execution(account_idx=0,
                       target_idx=0,
                       side=enums.ORDERSIDE_UNKNOWN,
                       position_effect=enums.ORDERPOSITIONEFFECT_UNKNOWN):
    handle_idx, target_idx = cnt.env.check_idx('get_last_execution', account_idx, target_idx, toarray=False)
    side_set = {side}
    position_effect_set = {position_effect}

    if side == enums.ORDERSIDE_UNKNOWN:
        side_set = {enums.ORDERSIDE_BUY,
                    enums.ORDERSIDE_SELL}

    if position_effect == enums.ORDERPOSITIONEFFECT_UNKNOWN:
        position_effect_set = {enums.ORDERPOSITIONEFFECT_OPEN,
                               enums.ORDERPOSITIONEFFECT_CLOSE,
                               enums.ORDERPOSITIONEFFECT_CLOSETODAY}

    ls = cnt.env.diff_api.last_execution(handle_idx, target_idx, side_set, position_effect_set)
    if len(ls) < 1:
        return None
    strategy_input = cnt.env.get_strategy_input()
    return cnt.env.diff_cvt.convert_last_execution_to_df(ls,
                                                         strategy_input['AccountNameList'],
                                                         strategy_input['TargetList'])


#################################

# 止盈止损函数: byorder 的止盈止损

@smm.force_mode(gv.RUNMODE_BACKTEST, gv.RUNMODE_REALTRADE)
@smm.force_phase(gv.RUMMODE_PHASE_ONDATA)
@apply_rule(verify_that('target_order_id').is_instance_of(*INTEGERSTYPE, NONETYPE),
            verify_that('stop_type').is_in((enums.ORDERSTOP_STOP_TYPE_PERCENT,
                                            enums.ORDERSTOP_STOP_TYPE_POINT)),
            verify_that('stop_gap').is_instance_of(*INTEGERSTYPE).is_greater_than(0),
            verify_that('order_type').is_in((enums.ORDERTYPE_LIMIT,
                                             enums.ORDERTYPE_MARKET)))
def stop_loss_by_order(target_order_id: 'int',
                       stop_type: 'int',
                       stop_gap: 'int',
                       order_type: 'int'):
    if target_order_id is None:
        return None

    return cnt.env.diff_api.stop_loss_by_order(target_order_id,
                                               stop_type,
                                               stop_gap,
                                               order_type)


@smm.force_mode(gv.RUNMODE_BACKTEST, gv.RUNMODE_REALTRADE)
@smm.force_phase(gv.RUMMODE_PHASE_ONDATA)
@apply_rule(verify_that('target_order_id').is_instance_of(*INTEGERSTYPE, NONETYPE),
            verify_that('stop_type').is_in((enums.ORDERSTOP_STOP_TYPE_PERCENT,
                                            enums.ORDERSTOP_STOP_TYPE_POINT)),
            verify_that('stop_gap').is_greater_than(0).is_instance_of(*INTEGERSTYPE),
            verify_that('order_type').is_in((enums.ORDERTYPE_LIMIT,
                                             enums.ORDERTYPE_MARKET)))
def stop_profit_by_order(target_order_id: 'int',
                         stop_type: 'int',
                         stop_gap: 'int',
                         order_type: 'int'):
    if target_order_id is None:
        return None

    return cnt.env.diff_api.stop_profit_by_order(target_order_id,
                                                 stop_type,
                                                 stop_gap,
                                                 order_type)


@smm.force_mode(gv.RUNMODE_BACKTEST, gv.RUNMODE_REALTRADE)
@smm.force_phase(gv.RUMMODE_PHASE_ONDATA)
@apply_rule(verify_that('target_order_id').is_instance_of(*INTEGERSTYPE, NONETYPE),
            verify_that('stop_type').is_in((enums.ORDERSTOP_STOP_TYPE_POINT,
                                            enums.ORDERSTOP_STOP_TYPE_PERCENT)),
            verify_that('stop_gap').is_greater_than(0).is_instance_of(*INTEGERSTYPE),
            verify_that('trailing_gap').is_greater_than(0).is_instance_of(*INTEGERSTYPE),
            verify_that('trailing_type').is_in((enums.ORDERSTOP_TRAILING_POINT,
                                                enums.ORDERSTOP_TRAILING_PERCENT)),
            verify_that('order_type').is_in((enums.ORDERTYPE_LIMIT,
                                             enums.ORDERTYPE_MARKET)))
def stop_trailing_by_order(target_order_id: 'int',
                           stop_type: 'int',
                           stop_gap: 'int',
                           trailing_gap: 'int',
                           trailing_type: 'int',
                           order_type: 'int'):
    if target_order_id is None:
        return None

    return cnt.env.diff_api.stop_trailing_by_order(target_order_id,
                                                   stop_type,
                                                   stop_gap,
                                                   trailing_gap,
                                                   trailing_type,
                                                   order_type)


#################################

# 止盈止损单查询函数

@smm.force_mode(gv.RUNMODE_BACKTEST, gv.RUNMODE_REALTRADE)
@smm.force_phase(gv.RUMMODE_PHASE_ONDATA)
@apply_rule(verify_that('stop_list').is_instance_of(*INTEGERSTYPE, list, tuple, ))
def get_stop_info(stop_list: 'list'):
    if isinstance(stop_list, INTEGERSTYPE):
        stop_list = [stop_list]

    ls = cnt.env.diff_api.stop_info(stop_list)
    if len(ls) < 1:
        return None

    return cnt.env.diff_cvt.convert_stop_info_to_df(ls)


#################################

# 止盈止损单查询
@smm.force_mode(gv.RUNMODE_BACKTEST, gv.RUNMODE_REALTRADE)
@smm.force_phase(gv.RUMMODE_PHASE_ONDATA)
@apply_rule(verify_that('stop_list').is_instance_of(*INTEGERSTYPE, list, tuple))
def stop_cancel(stop_list: 'list'):
    if isinstance(stop_list, INTEGERSTYPE):
        stop_list = [stop_list]

    return cnt.env.diff_api.stop_cancel(stop_list)
