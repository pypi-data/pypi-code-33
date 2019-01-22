__version__ = '0.1.0'

LOGGER_ROOT = 'dophon_logger.'

COMMAND = {
    'name': 'command'
}

DOPHON = {
    'name': 'dophon',
}

# 日志部件缓存(单例)
logger_cache = {}


def get_logger(logger_type: dict):
    if logger_type['name'] in logger_cache:
        # 初始化过日志组件则直接返回
        return logger_cache[logger_type['name']]
    if logger_type != COMMAND:
        try:
            logger = __import__(LOGGER_ROOT + logger_type['name'], fromlist=True)
            cache_type = logger_type['name']
        except Exception as e:
            print('无法获取的日志配置:', e)
            # 获取日志配置失败则返回默认配置
            logger = __import__(LOGGER_ROOT + COMMAND['name'], fromlist=True)
            cache_type = logger_type['name']
    else:
        logger = __import__(LOGGER_ROOT + logger_type['name'], fromlist=True)
        cache_type = logger_type['name']
    # 缓存日志组件
    logger_cache[cache_type] = logger
    return logger
