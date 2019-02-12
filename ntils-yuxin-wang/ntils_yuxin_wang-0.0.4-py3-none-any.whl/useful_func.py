#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/2/11 11:14
# @Author  : Young.W
# @File    : useful_func.py
# @Project : workbench

from functools import wraps
import editdistance
import time
import pickle


def calculate_edit_distance(pred_text_list, truth_text_list, mode="global_avg"):

    if mode == "global_avg":
        edit_distance = 0
        char_count = 0
        for p, t in zip(pred_text_list, truth_text_list):
            if p:
                char_count += len(t)
                edit_distance += editdistance.eval(p, t)
        return edit_distance / char_count

    elif mode == "text_avg":
        total_cer = 0
        for p, t in zip(pred_text_list, truth_text_list):
            if p:
                total_cer += editdistance.eval(p, t) / len(t)
        return total_cer / len(truth_text_list)

    else:
        raise Exception("Unknown mode")


def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if (uchar >= u"\u4e00") and (uchar <= u"\u9fa5"):
        return True
    else:
        return False


def is_number(uchar):
    """判断一个unicode是否是数字"""
    if (uchar >= u"\u0030") and (uchar <= u"\u0039"):
        return True
    else:
        return False


def is_alphabet(uchar):
    """判断一个unicode是否是英文字母"""
    if ((uchar >= u"\u0041") and (uchar <= u"\u005a")) or (
        (uchar >= u"\u0061") and (uchar <= u"\u007a")
    ):
        return True
    else:
        return False


def is_other(uchar):
    """判断是否非汉字，数字和英文字符"""
    if not (is_chinese(uchar) or is_number(uchar) or is_alphabet(uchar)):
        return True
    else:
        return False


def human_time(num_of_seconds):
    interval = 60
    human_mask = ["s", "min", "hours"]
    for i in range(len(human_mask)):
        if num_of_seconds < interval ** (i + 1):
            return "{:.2f}({})".format(num_of_seconds / interval ** i, human_mask[i])


def human_size(num_of_bytes):
    interval = 1024
    human_mask = ["B", "KB", "MB", "GB"]
    for i in range(len(human_mask)):
        if num_of_bytes < interval ** (i + 1):
            return "{:.2f}({})".format(num_of_bytes / interval ** i, human_mask[i])


def execute_time(func):
    @wraps(func)
    def cal_time_func(*args, **kwargs):
        print("{} function Start".format(func.__name__))
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(
            "{} function Completed, Execute Time: {}".format(
                func.__name__, human_time(end - start)
            )
        )
        return result

    return cal_time_func


def merge_file(input_file_list, output=None):
    """merge 多个文件数据，若指定输出则输出到文件，否则直接返回数据"""
    files_data = [read_file(i, mode="str") for i in input_file_list]
    merge_data = "\n".join(files_data)
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(merge_data)
            print("write data to {}".format(output))
    else:
        return merge_data


def read_file(fp, mode="lines"):
    """读取文件内容，mode[lines|str]"""
    with open(fp, "r", encoding="utf-8") as f:
        if mode == "lines":
            return f.readlines()
        if mode == "str":
            return f.read()


def save_text(text, fp):
    print("save file {}".format(fp))
    with open(fp, "w", encoding="utf-8") as f:
        f.write(text)


def pickle_dump(obj, fp):
    print("Serialize Start {}".format(fp))
    with open(fp, "wb") as f:
        pickle.dump(obj, f)


def pickle_load(fp):
    print("Deserialize Start".format(fp))
    with open(fp, "rb") as f:
        return pickle.load(f)
