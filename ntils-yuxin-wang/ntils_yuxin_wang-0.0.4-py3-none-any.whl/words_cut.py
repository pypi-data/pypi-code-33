#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/2/11 11:23
# @Author  : Young.W
# @File    : word_seg.py
# @Project : workbench

from typing import List

import re
import logging
from multiprocessing import Pool

import jieba
import pkuseg

from ntils.useful_func import is_other


class Cleaner:
    def clean(self, text: str) -> str:
        raise NotImplementedError


class Cutter:
    def cut(self, text: str) -> str:
        raise NotImplementedError


class JiebaCutter(Cutter):
    def __init__(self):
        jieba.setLogLevel(logging.INFO)

    def cut(self, text):
        cut_sent = " ".join([w for w in jieba.cut(text) if w.strip()])
        return cut_sent


class PkuSegCutter(Cutter):
    def __init__(self, model_name="default", user_dict="default"):
        self.model = pkuseg.pkuseg(model_name=model_name, user_dict=user_dict)

    def cut(self, text: str):
        cut_sent = " ".join([w for w in self.model.cut(text) if w.strip()])
        return cut_sent


class PreserveValidCharCleaner(Cleaner):
    def __init__(self, preserve_punc='，。！？“”《》.,"!?:：；; ><()（）-\\/、 '):
        self.preserve_punc = set(preserve_punc)

    def clean(self, text):
        re_sent = re.sub("\s{2,}", "", text)
        re_sent = "".join(
            [w for w in re_sent if not is_other(w) or w in self.preserve_punc]
        )
        return re_sent.strip()


def word_cut(
    texts: List[str], cleaner: Cleaner = None, cutter: Cutter = None, worker=8
) -> List[str]:
    """
    对文本列表进行切词，并返回以空格切开的词汇组成的句子
    :param texts: 文本列表
    :param cleaner: 清洗类
    :param cutter: 分词类
    :param worker: 进程数
    :return: List[str]
    """
    with Pool(processes=worker) as pool:
        cleaned_texts = list(pool.map(cleaner.clean, texts))
        cutted_texts = list(pool.map(cutter.cut, cleaned_texts))

    return cutted_texts


if __name__ == "__main__":
    test_texts = ["领域细分的中文分词工具", "跟现有开源工具相比提高了分词的准确率"]
    a = word_cut(test_texts, PreserveValidCharCleaner(), JiebaCutter())
