import logging
import traceback
import re
import datetime
import asyncio
import inspect
import socket

import twitchbot.api
import twitchbot.irc
import twitchbot.bot.user
import twitchbot.bot.command
import twitchbot.bot.event
import twitchbot.bot.context
import twitchbot.bot.stream
import twitchbot.bot.converter
import twitchbot.bot.check
import twitchbot.bot.interval
import twitchbot.bot.cache
import twitchbot.bot.game

from .user import User, Viewer
from typing import List, Union


class Bot:
    commands: dict = {}
    events: dict = {}
    intervals: dict = {}

    def __init__(self, client_id_api: str, token_api: str, token_irc: str, channel: str = None, reconnect: bool = False,
                 capabilities: list = None, command_prefix: str = '!', loop=None):
        self.log = logging.getLogger(__name__)
        self.log.debug('Initialization complete')

        self._client_id_api: str = client_id_api
        self._token_api: str = token_api
        self._token_irc: str = token_irc
        self._reconnect: bool = reconnect
        self._capabilities: list = capabilities if isinstance(capabilities, list) else []
        self._command_prefix = command_prefix if isinstance(command_prefix, str) and len(command_prefix) == 1 else '!'
        self._event_loop = loop if loop is not None else asyncio.get_event_loop()
        self._channel: str = channel

        self._running: bool = False
        self._states: dict = {}
        self.irc: twitchbot.irc.TwitchClient = None
        self.api: twitchbot.api.helix.Helix = None
        self.api_with_token_irc: twitchbot.api.helix.Helix = None
        self.api_kraken: twitchbot.api.kraken.Kraken = None
        self.users_cache: twitchbot.bot.cache.Cache = twitchbot.bot.cache.Cache()
        self.games_cache: twitchbot.bot.cache.Cache = twitchbot.bot.cache.Cache()

        interval_context = twitchbot.bot.context.Context(self)
        self._interval_handler = twitchbot.bot.interval.IntervalHandler(interval_context)

        self._last_stream_state_check = None

        self.api = twitchbot.api.helix.Helix(client_id=self._client_id_api, token=self._token_api)
        self.api_with_token_irc = twitchbot.api.helix.Helix(client_id=self._client_id_api, token=self._token_irc)
        self.api_kraken = twitchbot.api.kraken.Kraken(client_id=self._client_id_api, token=self._token_api)

    @property
    def channel(self):
        return self._channel

    @property
    def prefix(self):
        return self._command_prefix

    def start(self, print_exc=False):
        self.log.debug('Starting event loop')

        try:
            self._event_loop.run_until_complete(self.run())
        except KeyboardInterrupt:
            pass
        except Exception:
            if print_exc:
                traceback.print_exc()
                self.log.exception('An exception occurred')
        finally:
            self._event_loop.run_until_complete(self.stop())
            self._event_loop.close()
            self.log.debug('Event loop closed')

    async def stop(self):
        self._running = False
        self.log.info('Shutting down')

        if hasattr(self.on_close, '__super__'):
            if asyncio.iscoroutinefunction(self.on_close):
                await self.on_close()
        else:
            if asyncio.iscoroutinefunction(Bot.on_close) and asyncio.iscoroutinefunction(self.on_close):
                await Bot.on_close(self)
                await self.on_close()

        if self.api:
            await self.api.close()
        if self.api_with_token_irc:
            await self.api_with_token_irc.close()
        if self.api_kraken:
            await self.api_kraken.close()
        if self.irc:
            await self.irc.close()

        # Cancel running tasks
        for task in [task for task in asyncio.Task.all_tasks(loop=self._event_loop)
                     if task is not asyncio.tasks.Task.current_task()]:
            task.cancel()

    async def run(self):
        self._running = True

        if not self._channel:
            channel = await self.api.user()
            if not isinstance(channel, twitchbot.api.user.User):
                raise LookupError('Could not retrieve channel name with given api token')
            self._channel = channel.login
        nickname = await self.api_with_token_irc.user()
        if not isinstance(nickname, twitchbot.api.user.User):
            raise LookupError('Could not retrieve nick name with given irc token')

        self.irc = twitchbot.irc.TwitchClient(nickname=nickname.login, token=self._token_irc, channel=self._channel,
                                              loop=self._event_loop)

        retry = 5  # The base amount of seconds to wait before retrying
        retry_step = 2  # retry will increase with retry_increase when retry divided by retry_step is 0 (no remainder)
        retry_increase = 10  # The amount retry will be increased every step
        retry_max = 120  # The maximum amount of seconds to wait before retrying
        tries = 0  # The number of tries connecting
        tries_max = 100  # The maximum amount of (re)tries

        while self._running:  # Reconnect loop
            try:
                tries += 1

                # Connect the IRC client
                await self.irc.connect()

                # Log in using the provided nickname and token
                await self.irc.login()

                # Request capabilities
                for cap in self._capabilities:
                    await self.irc.cap(cap)

                await self.irc.join()

                if hasattr(self.on_ready, '__super__'):
                    if asyncio.iscoroutinefunction(self.on_ready):
                        await self.on_ready()
                else:
                    if asyncio.iscoroutinefunction(Bot.on_ready) and asyncio.iscoroutinefunction(self.on_ready):
                        await Bot.on_ready(self)
                        await self.on_ready()

                while self._running:  # Main bot loop
                    if hasattr(self.on_loop_start, '__super__'):
                        if asyncio.iscoroutinefunction(self.on_loop_start):
                            await self.on_loop_start()
                    else:
                        if asyncio.iscoroutinefunction(Bot.on_loop_start) and asyncio.iscoroutinefunction(
                                self.on_loop_start):
                            await Bot.on_loop_start(self)
                            await self.on_loop_start()

                    # Receive a message
                    response = await self.irc.receive()

                    on_message_context = twitchbot.bot.context.Context(self, response)
                    await on_message_context.init()
                    if hasattr(self.on_message, '__super__'):
                        if asyncio.iscoroutinefunction(self.on_message):
                            await self.on_message(on_message_context)
                    else:
                        if asyncio.iscoroutinefunction(Bot.on_message) and asyncio.iscoroutinefunction(self.on_message):
                            await Bot.on_message(self, on_message_context)
                            await self.on_message(on_message_context)

                    # Process the message
                    await self._process(response)

                    if hasattr(self.on_loop_end, '__super__'):
                        if asyncio.iscoroutinefunction(self.on_loop_end):
                            await self.on_loop_end()
                    else:
                        if asyncio.iscoroutinefunction(Bot.on_loop_end) and asyncio.iscoroutinefunction(
                                self.on_loop_end):
                            await Bot.on_loop_end(self)
                            await self.on_loop_end()
            except (BrokenPipeError, TimeoutError, ConnectionError, EOFError, socket.gaierror):
                if (not self._reconnect) or ((tries >= tries_max) and (tries_max > 0)):
                    raise

                if ((retry < retry_max) or retry_max <= 0) and (tries % retry_step == 0):
                    retry += retry_increase

                if (retry > retry_max) and (retry_max > 0):
                    retry = retry_max

                self.log.exception(f'Reconnecting in {retry} seconds')
                await asyncio.sleep(retry, loop=self._event_loop)
                continue  # Try to reconnect in x seconds

    async def _process(self, message):
        matches = re.findall(r'("[^"]+"|\S+)', message.content)

        # Check for (sub) commands
        i = len(matches)
        while i > 0:
            cmd = ' '.join(matches[0:i])[1:]
            if cmd in self.commands:
                cmd_prefix = self.commands[cmd].prefix
                cmd_enabled = self.commands[cmd].enabled
                cmd_callback = self.commands[cmd].callback
                matched_args = matches[i:]
                context = twitchbot.bot.context.Context(self, message, invoked_with=cmd, args=matched_args)
                await context.init()

                if ((isinstance(cmd_prefix, str) and len(cmd_prefix) == 1 and cmd_prefix == matches[0][0])
                    or ((cmd_prefix is None or len(cmd_prefix) == 0) and self._command_prefix == matches[0][0])) \
                        and cmd_enabled and await self.commands[cmd].check(context):

                    obj = cmd_callback

                    signature = inspect.signature(obj)
                    parameters = signature.parameters.copy()

                    parameters_len = len(parameters) - 1
                    args = []

                    # For each parameter, grab the matched argument and append it to the args list.
                    # When more matched arguments are passed than parameters, combine them.
                    for i in range(0, parameters_len):
                        if len(matched_args) >= i + 1:
                            if i == parameters_len - 1:
                                args.append(' '.join([x for x in matched_args[i:]]).strip('"'))
                            else:
                                args.append(matched_args[i].strip('"'))

                    iterator = iter(parameters.items())

                    # Skip context parameter
                    next(iterator)

                    i = 0
                    completed_args = []

                    # For each parameter, check if an argument was passed. If none, try the default parameter value.
                    # If an annotation is specified, convert the given argument.
                    for name, param in iterator:
                        # If parameter has no default, it is a required parameter.
                        # If there's no more argument in the iterator, return.
                        if param.default == inspect._empty:
                            if len(args) - 1 < i:
                                await self.irc.send_pmsg(
                                    f'{context.mention}, the required parameter "{param.name}" was not passed.')
                                return

                        # If there's at least one more parameter to iterate through.
                        if len(args) - 1 >= i:
                            # If a annotation is specified, try to convert the argument passed.
                            if param.annotation is not inspect._empty:
                                if issubclass(param.annotation, twitchbot.bot.converter.Converter):
                                    try:
                                        completed_args.append(await param.annotation.convert(context, args[i]))
                                    except twitchbot.bot.converter.ConvertError as e:
                                        self.log.warning(f'Conversion for {name} failed: {e}')
                                        return
                                elif inspect.iscoroutinefunction(param.annotation):
                                    completed_args.append(await param.annotation(args[i]))
                                else:
                                    try:
                                        completed_args.append(param.annotation(args[i]))
                                    except Exception as e:
                                        self.log.warning(f'Chat command argument failed conversion: {e}')
                                        return
                            else:
                                completed_args.append(args[i])
                        else:
                            # No argument is given, use the default specified by the parameter.
                            completed_args.append(param.default)

                        i += 1

                    try:
                        if asyncio.iscoroutinefunction(obj):
                            await obj(context, *completed_args)
                        else:
                            raise TypeError('Chat commands must be a coroutine')
                    except TypeError:
                        traceback.print_exc()
                    except Exception as e:
                        traceback.print_exc()

                    return

            i -= 1

    def set_state(self, name, state: bool = True):
        self._states[name] = state

    def get_state(self, name, default: bool = None):
        if name in self._states:
            return self._states[name]

        if default is None or not isinstance(default, bool):
            raise KeyError(f'{name} state does not exist')
        return default

    async def on_ready(self):
        Bot.on_ready.__super__ = True
        self.set_state('bot_ready')
        self.log.info('Bot is ready')

        await self._interval_handler.start()

        if 'on_ready' in self.events:
            await self.events['on_ready'](self)

    async def on_close(self):
        Bot.on_close.__super__ = True
        self.set_state('bot_ready', False)

        await self._interval_handler.stop()

        if 'on_close' in self.events:
            await self.events['on_close'](self)

    async def on_loop_start(self):
        Bot.on_loop_start.__super__ = True

        if not self._last_stream_state_check or self._last_stream_state_check + datetime.timedelta(
                seconds=5) <= datetime.datetime.now():
            stream_state = await self.stream(self.channel)
            if isinstance(stream_state, twitchbot.bot.stream.Stream) and stream_state.live:
                self.set_state('stream_live', True)
            else:
                self.set_state('stream_live', False)
            self._last_stream_state_check = datetime.datetime.now()
            self.log.debug(f'Stream status set to {self.get_state("stream_live")}')

        if 'on_loop_start' in self.events:
            await self.events['on_loop_start'](self)

    async def on_loop_end(self):
        Bot.on_loop_end.__super__ = True
        if 'on_loop_end' in self.events:
            await self.events['on_loop_end'](self)

    async def on_message(self, ctx: 'twitchbot.bot.context.Context'):
        Bot.on_message.__super__ = True
        if 'on_message' in self.events:
            await self.events['on_message'](self, ctx)
        if ctx.tags and 'msg-id' in ctx.tags:
            if ctx.tags['msg-id'] == 'sub':
                if 'on_sub' in self.events:
                    await self.events['on_sub'](ctx)
            elif ctx.tags['msg-id'] == 'resub':
                if 'on_resub' in self.events:
                    await self.events['on_resub'](ctx)
            elif ctx.tags['msg-id'] == 'subgift':
                if 'on_subgift' in self.events:
                    await self.events['on_subgift'](ctx)
            elif ctx.tags['msg-id'] == 'anonsubgift':
                if 'on_anonsubgift' in self.events:
                    await self.events['on_anonsubgift'](ctx)
            elif ctx.tags['msg-id'] == 'raid':
                if 'on_raid' in self.events:
                    await self.events['on_raid'](ctx)
            elif ctx.tags['msg-id'] == 'ritual':
                if 'on_ritual' in self.events:
                    await self.events['on_ritual'](ctx)

    async def user(self, user, as_viewer: bool = False) -> Union[str, int, User]:
        if self.users_cache.has(user) and not self.users_cache.expired(user):
            return self.users_cache.get(user)

        if as_viewer:
            _user = twitchbot.bot.user.Viewer(self, user)
        else:
            _user = twitchbot.bot.user.User(self, user)
        if isinstance(_user, twitchbot.bot.user.User):
            self.users_cache.set(user, _user)
            await _user.init()
        else:
            self.users_cache.set(user, _user)
        return _user

    async def users(self, *users, as_viewer: bool = False) -> List[Union[str, int, User, Viewer]]:
        users = list(users)
        users_cached = []

        for user in users:
            if self.users_cache.has(user) and not self.users_cache.expired(user):
                users_cached.append(self.users_cache.get(user))
                users.remove(user)

        _users = await self.api.users(*users)
        _users_converted = []
        for i, user in enumerate(_users):
            if isinstance(user, twitchbot.api.user.User):
                if as_viewer:
                    _user = twitchbot.bot.user.Viewer(self, user.login, user)
                else:
                    _user = twitchbot.bot.user.User(self, user.login, user)
                _users_converted.append(_user)
                self.users_cache.set(user.login, _user)
            else:
                _users_converted.append(user)
                self.users_cache.set(user, user)

                _users_converted.extend(users_cached)
        return _users_converted

    async def game(self, game):
        if self.games_cache.has(game) and not self.games_cache.expired(game):
            return self.games_cache.get(game)

        _game = twitchbot.bot.game.Game(self, game)
        self.games_cache.set(game, _game)
        await _game.init()
        return _game

    async def games(self, *games):
        games = list(games)
        games_cached = []

        for game in games:
            if self.games_cache.has(game) and not self.games_cache.expired(game):
                games_cached.append(self.games_cache.get(game))
                games.remove(game)

        _games = await self.api.games(*games)
        for i, game in enumerate(_games):
            _games[i] = twitchbot.bot.game.Game(self, game.name, game)
            self.users_cache.set(game.name, _games[i])

        _games.extend(games_cached)
        return _games

    async def stream(self, stream):
        _stream = twitchbot.bot.stream.Stream(self, stream)
        await _stream.init()
        return _stream

    async def viewer(self, viewer: str):
        viewers = await self.irc.viewers()
        viewer_converted = None

        for _viewer in viewers['all']:
            if _viewer == viewer.lower():
                viewer_converted = await self.user(viewer, as_viewer=True)
                break

        if viewer_converted:
            if isinstance(viewer_converted, twitchbot.bot.user.User):
                for rank in viewers:
                    if rank == 'all':
                        continue

                    if viewer_converted.login in viewers[rank]:
                        viewer_converted.rank.add(rank)
        return False

    async def viewers(self):
        viewers = await self.irc.viewers()
        viewers_converted = await self.users(*viewers['all'], as_viewer=True)

        for viewer in viewers_converted:
            if isinstance(viewer, twitchbot.bot.user.User):
                for rank in viewers:
                    if rank == 'all':
                        continue

                    if viewer.login in viewers[rank]:
                        viewer.rank.add(rank)

        return viewers_converted

    @staticmethod
    def add_command(func):
        if not isinstance(func, twitchbot.bot.command.Command):
            return

        Bot.commands[func.name] = func
        for alias in func.aliases:
            Bot.commands[alias] = func

    @staticmethod
    def enabled_command(cmd):
        if cmd in Bot.commands:
            if not isinstance(Bot.commands[cmd], twitchbot.bot.command.Command):
                return
        Bot.commands[cmd].enabled = True

    @staticmethod
    def disable_command(cmd):
        if cmd in Bot.commands:
            if not isinstance(Bot.commands[cmd], twitchbot.bot.command.Command):
                return
        Bot.commands[cmd].enabled = False

    @staticmethod
    def add_event(func):
        if not isinstance(func, twitchbot.bot.event.Event):
            return

        Bot.events[func.__name__] = func

    @staticmethod
    def add_interval(func):
        if not isinstance(func, twitchbot.bot.interval.Interval):
            return

        Bot.intervals[func.__name__] = func


def command(name: str = None, aliases: list = None, enabled: bool = True, pass_context: bool = True, prefix: str = None,
            help: dict = None, *args, **kwargs):
    if aliases is None:
        aliases = []
    if help is None:
        help = []

    def decorator(func):
        result = twitchbot.bot.command.Command(func, *args, name=name, aliases=aliases, enabled=enabled,
                                               pass_context=pass_context, prefix=prefix, help=help, **kwargs)
        Bot.add_command(result)
        return result

    return decorator


def check(*checks):
    def decorator(func):
        if isinstance(func, twitchbot.bot.command.Command):
            func.set_check(*checks)
        else:
            func.__command_checks__ = list(checks)
        return func

    return decorator


def event(enabled: bool = True, pass_context: bool = True):
    def decorator(func):
        result = twitchbot.bot.event.Event(func, enabled=enabled, pass_context=pass_context)
        Bot.add_event(result)
        return result

    return decorator


def interval(timedelta: datetime.timedelta, enabled: bool = True, pass_context: bool = True, wait_after: bool = False):
    def decorator(func):
        result = twitchbot.bot.interval.Interval(func, timedelta=timedelta, enabled=enabled, pass_context=pass_context,
                                                 wait_after=wait_after)
        Bot.add_interval(result)
        return result

    return decorator
