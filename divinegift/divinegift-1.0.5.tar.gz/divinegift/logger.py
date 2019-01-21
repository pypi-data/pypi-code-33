import os
import logging
from logging.handlers import TimedRotatingFileHandler
from divinegift.monitoring import send_telegram, send_slack
from divinegift.monitoring import send_email, send_email_with_attachments
import traceback

telegram_chat = {'private': 161680036, 'chat': -277453709, 'channel': -1001343660695}
to_email_chat = {'private': ['r.rasputin@s7.ru'], 'chat': ['aims.control@s7.ru']}
cc_email_chat = {'private': [], 'chat': []}
logger = None


def log_debug(msg):
    """
    Logging a debug message
    :param msg: Message which would be logged
    :return: None
    """
    if logger:
        logger.debug(msg)
    else:
        logging.debug(msg)
    #print(msg)


def log_info(msg):
    """
    Logging a info
    :param msg: Message which would be logged
    :return: None
    """
    if logger:
        logger.info(msg)
    else:
        logging.info(msg)
    #print(msg)


def log_warning(msg):
    """
    Logging a warning
    :param msg: Message which would be logged
    :type msg: string
    :return: None
    """
    if logger:
        logger.warning(msg)
    else:
        logging.warning(msg)
    #print(msg)


def log_err(msg, src=None, mode=[], channel={}):
    """
    Logging an error with monitoring if parameters were filled
    :param msg: Error message which will logged
    :param src: Source which raised error
    :type src: string
    :param mode: List of monitoring's mode (telegram, email, email_attach, slack)
    :type mode: list
    :param channel: Dict with parameters of monitoring (e.g. {'telegram': -1001343660695}
    :type channel: dict
    :return: None
    """
    if logger:
        logger.exception(msg)
    else:
        logging.exception(msg)
    #print(msg)
    error_txt = 'An error has occurred in {}\nError text: {}\n{}'.format(src, msg, traceback.format_exc())

    if mode:
        #if 'vk' in mode:
        #   send_vk(error_txt, vk_chat[channel.get('vk')], channel.get('vk', 'private'))
        if 'telegram' in mode:
            send_telegram(error_txt, chat_id=channel.get('telegram', -1001343660695))
        if 'slack' in mode:
            send_slack()
        if 'email' in mode:
            send_email(error_txt, src + ' ERROR',
                       channel.get('email_to', ['r.rasputin@s7.ru']),
                       channel.get('email_cc', []))
        if 'email_attach' in mode:
            send_email_with_attachments(src + ' ERROR', error_txt,
                                       channel.get('email_to', ['r.rasputin@s7.ru']),
                                       channel.get('email_cc', []),
                                       log, os.getcwd() + os.sep)


def log_crit(msg):
    logging.critical(msg)
    #print(msg)


def set_loglevel(log_level, log_file, log_dir='./logs/', when='midnight', interval=1, backupCount=7):
    """
    This set up log_level and name of logfile
    :param log_level: String with log_level (e.g. 'INFO')
    :param log_file: Name of file with logs
    :param log_dir: Directory which should keep logs
    :param when: When rotate log
    :param interval: How often
    :param backupCount: How many version need to keep
    :return: None
    """
    global logger
    logger = logging.getLogger('Rotating log')
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % log_level)
    logger.setLevel(numeric_level)
    formatter = logging.Formatter('%(levelname)-8s [%(asctime)s] %(message)s')
    if log_file:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        handler = TimedRotatingFileHandler(os.path.join(log_dir, log_file), when=when, interval=interval, backupCount=backupCount)
    else:
        handler = logging.StreamHandler()

    handler.setFormatter(formatter)
    logger.addHandler(handler)
