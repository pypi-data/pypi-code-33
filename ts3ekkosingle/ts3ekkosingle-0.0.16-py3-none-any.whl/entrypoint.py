#!/usr/bin/python3.6
import subprocess
import time
import os
import urllib.parse
import logging
import pathlib

import ts3ekkoutil.parser
import ts3ekkosingle
from ts3ekkoutil.envconsts import EkkoPropertyNames as epn

try:
    from ts3ekkosingle.ts3identity import replace_identity, startup
    from ts3ekkosingle.bot import EkkoBot
except ImportError:
    from .ts3identity import replace_identity, startup
    from .bot import EkkoBot

logger = logging.getLogger('ekkoclient-entrypoint')


def prepare_platform(prep_env):
    """
    Start services required for teamspeak. Uses sleeps to wait for required services to start (15 sec).

    :param prep_env: Set of environment variables, including DISPLAY=:1.
    """
    logger.info('starting xvfb')
    subprocess.Popen(['Xvfb', ':1', '-screen', '0', '1025x768x16'], env=prep_env) # Xvfb :1 -screen 0 1025x768x16
    time.sleep(5)
    logger.info('starting dbus')
    subprocess.run(['dbus-daemon', '--system', '--fork'], env=prep_env) # dbus-daemon --system --fork
    time.sleep(5)
    logger.info('starting pulseaudio')
    subprocess.run(['pulseaudio', '--start', '--daemonize=true'], env=prep_env)
    time.sleep(5)


def prepare_teamspeak(path, record_key, old_identity_str, new_identity_str):
    """
    Provision the ts3 client. Modifies the ts3 settings.db to put in the desired identity.

    :param path: path of the settings.db to be modified
    :param record_key: key-id of the record to be modified inside of the settings.db ProtobufItems table
    :param old_identity_str: string to be removed from the value of the targeted record (default id)
    :param new_identity_str: string to be inserted into the value of the targeted record (new id)
    """
    sess = startup(path)
    logger.debug(f'path: {path}, record key: {record_key}, '
                 f'old_iden: {old_identity_str}, new_iden: {new_identity_str}')
    replace_identity(sess, record_key, old_identity_str, new_identity_str)
    logger.info('ts3 identity prepared')


def start_teamspeak(prep_env, ts3_workdir, ts3_runscript, ts3url):
    """
    Start the teamspeak client.
    """
    ts3path = pathlib.Path(ts3_workdir) / ts3_runscript
    ts3path = ts3path.resolve()
    logger.info(f'starting teamspeak client in {ts3path}')
    subprocess.Popen([str(ts3path), ts3url], env=prep_env)


def assemble_ts3serverurl(server, port, username, server_password=None, channel_name=None, channel_id=None,
                          channel_password=None, token=None):
    """

    ts3server://host?port=9987&nickname=UserNickname&password=serverPassword&channel=MyDefaultChannel
        &cid=channelID&channelpassword=defaultChannelPassword&token=TokenKey&addbookmark=MyBookMarkLabel

    :param server: ip or url of ts3 server
    :param port: port of ts3 server
    :param username: wanted username
    :param server_password: password for the ts3 server
    :param channel_name: channel name to be connected to
    :param channel_id: channel id to be connected to (takes priority over name)
    :param channel_password: password for the channel to be connected to
    :param token: permission token
    :return: the assembled ts3 url
    """
    ts3url = f"ts3server://{server}?port={port}&nickname={urllib.parse.quote(username)}"

    if server_password is not None:
        ts3url += f"&password={urllib.parse.quote(server_password)}"

    if channel_name is not None:
        ts3url += f"&channel={urllib.parse.quote(channel_name)}"

    if channel_id is not None:
        ts3url += f"&cid={channel_id}"

    if channel_password is not None:
        ts3url += f"&channelpassword={urllib.parse.quote(channel_password)}"

    if token is not None:
        ts3url += f"&token={urllib.parse.quote(token)}"

    logger.debug(ts3url)
    return ts3url


def start_ekko(args):
    """
    Start the ekko bot.
    :param args: 
    :return: 
    """
    logger.info('starting ekko')
    bot = EkkoBot(args=args)
    bot.start()
    logger.info('ekko started')


def main():
    parser = ts3ekkoutil.parser.create_ekko_parser()
    args = vars(parser.parse_args())

    logging.basicConfig(level=int(args[epn.LOG_LEVEL]), format=args[epn.LOG_FORMAT])

    logger.info(f'ts3ekkosingle version: {ts3ekkosingle.__version__}')

    # Set DISPLAY env variable for dbus, pulseaudio and teamspeak xvfb
    prep_env = os.environ.copy()
    prep_env["DISPLAY"] = ':1'

    logger.debug(args)
    logger.debug(os.environ)

    # Start services and client
    prepare_platform(prep_env)
    ts3url = assemble_ts3serverurl(args[epn.TS3_SERVER_HOST], args[epn.TS3_SERVER_PORT], args[epn.TS3_USERNAME],
                                   args[epn.TS3_SERVER_PASSWORD], args[epn.TS3_CHANNEL_NAME], args[epn.TS3_CHANNEL_ID],
                                   args[epn.TS3_CHANNEL_PASSWORD], args[epn.TS3_SERVER_PERMISSION_TOKEN])

    # make some basics checks about things that definitely need to be configured
    if args[epn.TS3_IDENTITY_DATABASE_KEY] is None:
        logger.error(f'{epn.TS3_IDENTITY_DATABASE_KEY} must be configured')

    if args[epn.TS3_IDENTITY_DATABASE_PRECONF] is None or args[epn.TS3_IDENTITY] is None:
        logger.error(f'{epn.TS3_IDENTITY_DATABASE_PRECONF} and {epn.TS3_IDENTITY} must be configured')

    prepare_teamspeak(f'{args[epn.TS3_CONFIG_DIRECTORY]}settings.db', args[epn.TS3_IDENTITY_DATABASE_KEY],
                      args[epn.TS3_IDENTITY_DATABASE_PRECONF], args[epn.TS3_IDENTITY])
    start_teamspeak(prep_env, args[epn.TS3_DIRECTORY], args[epn.TS3_RUNSCRIPT], ts3url)
    start_ekko(args)


if __name__ == '__main__':
    main()
