"""
Tools which allow bots to interact with Slack APIs.
"""

import logging
import re
import time

from slackclient import SlackClient

def default_logger(name='slack_invoker', handler=None, level=logging.INFO):
    """
    Returns a logging.Logger for use with slack_invoker clients.

    Args:
    1. name - Optional name for the logger; defaults to "slack_invoker"
    2. handler - logging Handler which determines where log messages go; if passed as None (the
       default value), then a StreamHandler is used
    3. level - Log level (can be passed as logging.INFO, logging.DEBUG, etc. or as strings 'INFO',
       'DEBUG', etc.)

    Returns: Instance of logging.Logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if handler is None:
        formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(name)s: %(message)s')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger

def rtm_bot_user(bot, bot_user_access_token, rtm_poll_interval=2, logger=None):
    """
    Sets up a slack client to connect to the Slack Real-time Messaging API as a bot user, listen on
    mentions, and handle the corresponding payloads using a given slack_invoker bot. Runs in calling
    process.

    Note: Heavily inspired by (copy-pasted from) the following blog -
    https://www.fullstackpython.com/blog/build-first-slack-bot-python.html

    Args:
    1. bot - slack_invoker bot as produced by parse.wrap_runner; the naked interface is that the bot
       should accept a list of strings representing tokens sent with a bot mention, and return a
       string to be displayed in response to the mention
    2. bot_user_access_token - Access token for bot user; these are available on
       https://api.slack.com once you create a bot user
    3. rtm_poll_interval - Number of seconds between each poll of the Slack RTM API
    4. logger - logging.Logger instance to be used for logging purposes; if None, the
       default_logger method is called to generate a logger

    Returns: None
    """
    if logger is None:
        logger = default_logger()

    MENTION_REGEX = re.compile('^<@(|[WU].+?)>(.*)')

    slack_client = SlackClient(bot_user_access_token)
    bot_id = None
    if slack_client.rtm_connect(with_team_state=False):
        # Read bot's user ID by calling Web API method `auth.test`
        bot_id = slack_client.api_call('auth.test')['user_id']
        logger.info('Initializing bot user')
        while True:
            logger.debug('Polling slack RTM API')
            slack_events = slack_client.rtm_read()
            for event in slack_events:
                if event['type'] == 'message' and not 'subtype' in event:
                    matches = MENTION_REGEX.search(event['text'])
                    user_id = None
                    message = ''
                    if matches:
                        user_id, message = (matches.group(1), matches.group(2).strip())

                    if user_id == bot_id:
                        logger.info('Processing message: {}'.format(message))
                        response = None
                        logger.info(message)
                        try:
                            response = bot(message)
                        except Exception as e:
                            response = str(e)
                        logger.info('Response: {}'.format(response))

                        slack_client.api_call(
                            'chat.postMessage',
                            channel=event['channel'],
                            text=response or 'wtf'
                        )

            time.sleep(rtm_poll_interval)
