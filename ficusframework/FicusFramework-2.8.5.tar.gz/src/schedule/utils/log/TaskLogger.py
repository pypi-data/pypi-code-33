# 用来在程序中写入日志
import datetime
import logging

import traceback

# 本地log
from schedule.utils.log import TaskLogFileAppender

local_log = logging.getLogger('Ficus')

def log(append_log: str):
    """
    记录日志信息
    :param append_log: 需要记录的内容
    :return:
    """
    call_info = _get_filename_function_line(limit=2)
    print(call_info)
    _log_detail(call_info,append_log)

def error(e:Exception):
    """
    记录异常信息
    :param e:  抛出的异常
    :return:
    """
    call_info = _get_filename_function_line(limit=2)
    _log_detail(call_info, str(e))


def _stack_tuple_to_function_line_filename(stackTuple):
    ''''' stackTuple: （文件名，行号，函数名，这一行的代码）
    '''
    filename = stackTuple[0]
    linenumber = stackTuple[1]
    funcname = stackTuple[2]

    import threading
    return f"[{filename}#{funcname}]-[{linenumber}]-[{threading.current_thread().name}]"

def _get_filename_function_line(limit=1):  # limit = 1 表示抽取该函数调用者的位置，注意输入到extract_stack中的limit=limit+1
    stackTuple = traceback.extract_stack(limit=limit + 1)[0]
    return _stack_tuple_to_function_line_filename(stackTuple)

def _log_detail(call_info,append_log):
    """
    把东西写入文件中
    :param call_info:
    :param append_log:
    :return:
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    format_append_log = f"{now} {call_info} {append_log if append_log is not None else ''}"

    log_file_name = TaskLogFileAppender.get_log_file_name()

    if log_file_name is not None and log_file_name.strip()!="":
        TaskLogFileAppender.append_log(log_file_name,format_append_log)
    else:
        local_log.info(format_append_log)
