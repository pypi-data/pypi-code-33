# coding: utf-8
import tma
from fuzzywuzzy import fuzz
from textrank4zh import TextRank4Sentence
from tma.collector.ts import pro as ts_pro


def get_top_news(news, top=10):
    """返回最重要的 top 个新闻

    :param news: list of news
    :param top: int
    :return: top news
    """
    ranker = tma.TfidfDocRank(news, N=10)
    top_news = [x[1] for x in ranker.rank(top=top+30)]

    for i, new in enumerate(top_news):
        for j in range(i + 1, len(top_news)):
            distance = fuzz.ratio(new, top_news[j])
            if distance > 80:
                top_news[j] = 'drop'
    top_news = [new for new in top_news if new != "drop"]

    return top_news[:top]


def cctv_abstract(date):
    """从CCTV新闻联播当天的内容中抽取10个句子作为摘要

    :param date: str
        日期，如：20181222
    :return: str
    """
    news = ts_pro.cctv_news(date=date)
    contents = "".join(list(news['content']))

    tr4s = TextRank4Sentence()
    tr4s.analyze(text=contents, lower=True, source='all_filters')

    abstract = []
    for i, item in enumerate(tr4s.get_key_sentences(num=10), 1):
        abstract.append("(%i) %s。\n" % (i, item.sentence))

    return "".join(abstract)



