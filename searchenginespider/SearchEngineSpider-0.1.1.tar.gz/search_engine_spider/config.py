import os
import logging

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("chardet").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s: %(message)s')
LOGGER = logging.getLogger('search_engine')
SEARCH_ENGINE_SPIDER_DIR = os.path.realpath(os.path.dirname(__file__))
DATA_DIR = os.path.join(SEARCH_ENGINE_SPIDER_DIR, "data")


def assert_exists(file_name):
    if os.path.exists(file_name):
        return True
    print("not exists: " + file_name)

def file2list(file_name):
    assert_exists(file_name)
    with open(file_name) as f:
        lines = [line.strip() for line in f]
    return lines
