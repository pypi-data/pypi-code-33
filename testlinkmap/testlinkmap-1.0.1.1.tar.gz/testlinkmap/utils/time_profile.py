#! /usr/local/bin/python3
# encoding: utf-8

import time


# TODO: 带参，用以指明是否开启print日志。 @time_profile_*(open_log)


# 单次调用耗时统计
def time_profile_wrapper(func):
    def wrapper(*args, **kwargs):
        begin_time = time.time()
        x = func(*args, **kwargs) # func 有无返回值都ok
        end_time = time.time()
        print(f'\n---*** cost 【{end_time - begin_time:<.8f}】 seconds in 【{func.__name__}】 ***---\n')
        return x
    return wrapper


# 多次调用累加统计
def time_profile_acc_wrapper(func):
    """
        两种实现方式：
            1. 给本def增加属性dict[func:const]
            2. 使用装饰器给func增加属性cost
        对比：
            方法1可以集中打印数据信息，方法2会改变func的关联属性
            这里采用更中规中矩的方法1
    """

    # 函数指针，方便函数重命名
    outter_func = time_profile_acc_wrapper

    # 为函数添加属性，用以保存信息
    attr_name_cost_dict = 'attr_name_cost_dict'
    if not hasattr(outter_func, attr_name_cost_dict):
        setattr(outter_func, attr_name_cost_dict, {})

    # 调用信息
    class CallInfo(object):
        def __init__(self, funcname):
            self.func_name = funcname
            self.call_count = 0
            self.cost_time = 0

        def add_count(self):
            self.call_count += 1

        def add_cost_time(self, cost_time):
            self.cost_time += cost_time

        def debug_info(self):
            return f'---*** total call 【{self.call_count}】times and cost total【{self.cost_time:<.8f}】' \
                   f'avg 【{self.cost_time/self.call_count if self.call_count > 0 else self.cost_time:<.8f}】 seconds ' \
                   f'in 【{self.func_name}】 ***---'

    # debug logs
    # def print_all_logs():
    #     attr_dict = getattr(outter_func, attr_name_cost_dict)
    #     for key in attr_dict:
    #         print(attr_dict[key].debug_info())

    # wrapper
    def wrapper(*args, **kwargs):
        begin_time = time.time()
        x = func(*args, **kwargs)
        end_time = time.time()

        # cost
        cost = end_time - begin_time

        # get attr
        call_info = getattr(outter_func, attr_name_cost_dict).get(func.__name__, CallInfo(func.__name__))

        # acc
        call_info.call_count += 1
        call_info.cost_time += cost

        # set attr
        getattr(outter_func, attr_name_cost_dict)[func.__name__] = call_info

        # print
        # print(f'\n---*** cost 【{cost:<.8f}】, total 【{acc_cost:<.8f}】 seconds in 【{func.__name__}】 ***---\n')

        return x
    return wrapper


# print all time profile infos
# ！这里只是粗略统计，因为函数间是可能有相互调用的，所以简单加出来的时间会比实际时间更大一些！
def time_profile_print_all_logs():
    print('--- log all time profiles ---')
    x_func = time_profile_acc_wrapper
    x_key = 'attr_name_cost_dict'
    if hasattr(x_func, x_key):
        attr_dict = getattr(x_func, x_key)
        total_cost_time = 0
        for key in attr_dict:
            total_cost_time += attr_dict[key].cost_time
            print(attr_dict[key].debug_info())
        print(f'--- sum cost 【{total_cost_time:<.8f}】 seconds ---')
    else:
        print('--- no time profiles ---')
