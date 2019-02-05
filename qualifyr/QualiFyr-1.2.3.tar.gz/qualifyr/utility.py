import logging
import io
import os
import colorlog
import base64

def get_logger(filepath, level=logging.DEBUG):
    # create logger
    logger = logging.getLogger(os.path.basename(filepath))
    logger.setLevel(level)
    # create console handler and set level to debug
    console = logging.StreamHandler()
    console.setLevel(level)
    # create formatter
    format_str = '%(asctime)s - %(levelname)-8s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    if os.isatty(2):
        cformat = '%(log_color)s' + format_str
        colors = {'DEBUG': 'reset',
                  'INFO': 'reset',
                  'WARNING': 'bold_yellow',
                  'ERROR': 'bold_red',
                  'CRITICAL': 'bold_red'}
        formatter = colorlog.ColoredFormatter(cformat, date_format,
                                              log_colors=colors)
    else:
        formatter = logging.Formatter(format_str, date_format)
    # add formatter to ch
    console.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(console)

    return logger

def string_to_num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

def include_file(name, fdir=None, b64=False):
    logger = logging.getLogger(__name__)
    try:
        if fdir is None:
            fdir = ''
        if b64:
            with io.open (os.path.join(fdir, name), "rb") as f:
                return base64.b64encode(f.read()).decode('utf-8')
        else:
            with io.open (os.path.join(fdir, name), "r", encoding='utf-8') as f:
                return f.read()
    except (OSError, IOError) as e:
        logger.error("Could not include file '{}': {}".format(name, e))