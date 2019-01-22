import argparse
from dophon_manager.actions import *

parser = argparse.ArgumentParser(description='dophon project manager')
parser.add_argument('action', type=str, default='-h')
parser.add_argument('--name', type=str, default='dophon_project')
FLAGS = parser.parse_args()

ARG_DICT = {
    'new': ActionObj().new_action,
    'init': ActionObj().init_action,
    'dev': ActionObj().dev_action,
    'run': ActionObj().run_action
}

__version__ = '0.1.0'


def main():
    # 执行项目管理初始化
    action = FLAGS.action
    if action in ARG_DICT:
        ARG_DICT[action](FLAGS.name)
