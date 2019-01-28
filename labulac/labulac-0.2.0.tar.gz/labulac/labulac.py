"""labulac
Usage:
  labulac ls
  labulac use <name>
  labulac show
  labulac add <name> <url>
  labulac re <name>
  labulac (-h | --help)
  labulac (-v | --version)
"""


import os
import re
import sys
import pickle
import platform
from docopt import docopt
try:
    import configparser
except:
    import ConfigParser as configparser

FILE_NAME = "~\\pip\\pip.ini" if ("Windows" in platform.system()) else "~/.pip/pip.conf"
FILE_PATH = os.path.expanduser(FILE_NAME)
dir_path = os.path.dirname(FILE_PATH)
if not os.path.exists(dir_path):
    os.mkdir(dir_path)
SOURCES_NAME = os.path.join(dir_path, "sources.dict")
SOURCES = dict()

if not os.path.exists(SOURCES_NAME):
    with open(SOURCES_NAME, "wb") as fp:
        pickle.dump({
            "pypi": "https://pypi.python.org/simple/",
            "tuna": "https://pypi.tuna.tsinghua.edu.cn/simple",
            "douban": "http://pypi.douban.com/simple/",
            "aliyun": "https://mirrors.aliyun.com/pypi/simple/",
            "ustc": "https://mirrors.ustc.edu.cn/pypi/web/simple"
        }, fp)
with open(SOURCES_NAME, "rb") as fp:
    SOURCES = pickle.load(fp)

huanyin = """
         Welcome labulac!
"""

def ls():
    print('\n')
    for key in SOURCES.keys():
        print(key, '\t', SOURCES[key])
    print('\n')

def wr(name):
    with open(FILE_PATH, 'w') as fp:
        str_ = "[global]\nindex-url = {0}\n[install]\ntrusted-host = {1}".format(
            SOURCES[name], SOURCES[name].split('/')[2])
        fp.write(str_)

def select(name):
    if name not in SOURCES.keys():
        print("\n{} is not in the Source list.\n".format(name))
    else:
        wr(name)
        print("\nSource is changed to {}({}).\n".format(name, SOURCES[name]))

def show():
    if not os.path.exists(FILE_PATH):
        print("\nCurrent source is pypi.\n")
        return
    config = configparser.ConfigParser()
    config.read(FILE_PATH)
    index_url = config.get("global", "index-url")
    for key in SOURCES.keys():
        if index_url == SOURCES[key]:
            print("\nCurrent source is {}({}).\n".format(key, index_url))
            break
    else:
         print("\nCurrent source is {}.\n".format(index_url))

def check(url):
    p = re.compile("^https?://.+?/simple/?$")
    if p.match(url) == None:
        return False    
    return True

def add(name, source_url):
    if not check(source_url):
        print("\nURL({}) does not conform to the rules.\n".format(source_url))
        return
    SOURCES[name] = source_url
    with open(SOURCES_NAME, "wb") as fp:
        pickle.dump(SOURCES, fp)
    print("\n{}({}) is add to Source list.\n".format(name, source_url))

def remove(name):
    if name not in SOURCES.keys():
        print("\n{} is not in the Source list.\n".format(name))
    else:
        source_url = SOURCES.pop(name)
        with open(SOURCES_NAME, "wb") as fp:
            pickle.dump(SOURCES, fp)
        print("\n{}({}) is remove to Source list.\n".format(name, source_url))

def main():
    arguments = docopt(__doc__, version="2.0.6")
    if arguments["ls"]:
        ls()
    elif arguments["use"]:
        select(arguments["<name>"])
    elif arguments["show"]:
        show()
    elif arguments["add"]:
        add(arguments["<name>"], arguments["<url>"])
    elif arguments["re"]:
        remove(arguments["<name>"])
    else:
        print("看准了输入！！!")

if __name__ == "__main__":
    print(huanyin)
    main()
