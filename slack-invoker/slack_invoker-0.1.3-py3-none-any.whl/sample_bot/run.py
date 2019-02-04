import argparse
import os
import re
import time

from slack_invoker import invoke, parse

RTM_READ_DELAY = 1
SLACK_BOT_USER_ACCESS_TOKEN = os.environ.get('SLACK_BOT_USER_ACCESS_TOKEN')
if SLACK_BOT_USER_ACCESS_TOKEN is None:
    raise ValueError('ERROR: SLACK_BOT_USER_ACCESS_TOKEN environment variable not set')

def greeter(greeting, name):
    return '{}, {}'.format(greeting, name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('@chuck')
    parser.add_argument('--greeting', required=True)
    parser.add_argument('--name', required=True)

    bot = parse.wrap_runner(parser, greeter)
    invoke.rtm_bot_user(bot, SLACK_BOT_USER_ACCESS_TOKEN, RTM_READ_DELAY)
