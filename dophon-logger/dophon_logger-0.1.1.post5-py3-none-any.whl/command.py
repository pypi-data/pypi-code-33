import logging
from logging import Logger


# 日志过滤非框架打印
class DefFilter(logging.Filter):
    def filter(self, record):
        return record.name.startswith('dophon')


def inject_logger(g: dict, var_name: str = 'logger'):
    logger = Logger(g['__name__'])
    logger.addFilter(DefFilter())
    g[var_name] = logger
