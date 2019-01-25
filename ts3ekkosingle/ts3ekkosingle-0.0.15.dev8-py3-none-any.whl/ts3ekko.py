import asyncio
import ts3
import re
import time
import logging

# local
try:
    from ts3ekkosingle.errors import TS3AuthenticationFailed, TS3InsufficientPermissions, TS3InvalidCommand, \
        EkkoUnsuitedCommand, EkkoParsingError, EkkoArgparserMessage
    from ts3ekkosingle.command import Command
    from ts3ekkosingle.event_type import EventType
except ImportError:
    from .errors import TS3AuthenticationFailed, TS3InsufficientPermissions, TS3InvalidCommand, EkkoUnsuitedCommand, \
        EkkoParsingError, EkkoArgparserMessage
    from .command import Command
    from .event_type import EventType

logger = logging.getLogger('ekkoclient-ts3ekko')


class ProbeResult:
    SUCCESS = 1
    UNSUITED = 2
    PARSING_ERROR = 3
    CONN_RESET = 4
    PARSING_ABORT = 5


class TS3Ekko:
    def __init__(self, apikey, server='localhost', port='25639', loop=None, bot_username=None):
        self.server = server
        self.port = port

        self.apikey = apikey
        logger.debug('apikey=' + apikey)

        self.ts3conn = self.create_connection()
        self.bot_username = bot_username
        self.loop = loop or asyncio.get_event_loop()

        self.commands = []

    def add_command(self, hooks, func, **kwargs):
        """
        Add a command to the list of enabled commands and sort the list according to command priority.
        
        :param hooks: List of EventTypes on which the command should be called
        :param func: callback func for the command
        :param kwargs: various parameter for Command() creation
        """
        cmd = Command(hooks, func, **kwargs)

        self.commands.append(cmd)
        self.commands.sort(key=lambda cmd: cmd.priority)
        self.commands.reverse()

    def add_cog(self, cog):
        """
        Adds a cog to the bot. A cog is a collection of commands. The commands should be stored in the `.command`
         attribute in the following form:

         list of tuple in format: (EventType-int, callback-func, priority-int, name-str, help_cmd_str-str)

        For more information about these command configuration see :class:`Command`.
        :param cog:
        :return:
        """
        logger.debug(f'adding cog: {cog}')
        for cmd in cog.commands:
            try:
                self.add_command(cmd[0], cmd[1], priority=cmd[2], name=cmd[3], help_cmd_str=cmd[4])
            except Exception as e:
                logger.error(f'failed to add cog-command to collection: {cmd},'
                             f'\nexception: \n{e}')

    def create_connection(self, timeout=20):
        """
        Create a ts3query connection and authenticate with the apikey.
        
        :param timeout: Number of re-tries on failure.
        :return: authenticated ts3query connection
        """
        for to in range(0, timeout):
            try:
                _ts3conn = ts3.query.TS3ClientConnection(self.server, self.port)
                _ts3conn.auth(apikey=self.apikey)
                logger.debug(f'created TS3ClientQuery to {self.server}:{self.port}')
                return _ts3conn
            except OSError as e:
                logger.debug(f'failed to create TS3ClientQuery connection (os failed): {e}')
                time.sleep(1)
            except ts3.query.TS3QueryError as e:
                logger.debug(f'failed to create TS3ClientQuery connection (auth failed): {e.resp.error["msg"]}')
                time.sleep(1)
        logger.critical('failed to create TS3ClientQuery connection - TIMEOUT REACHED!')
        raise TS3AuthenticationFailed()

    async def poll_events(self):
        """
        Poll the ts3query connection for all possible events. Dispatch handling-process on event receive.
        """
        self.ts3conn.clientnotifyregister(event="any", schandlerid=0)
        while True:
            logger.debug('polling new events')
            self.ts3conn.send_keepalive()
            try:
                ts3_event = await self.loop.run_in_executor(None, self.ts3conn.wait_for_event, 60)
            except ts3.query.TS3TimeoutError:
                pass
            except Exception as e:
                logger.critical(f'while polling for event: {e}')
            else:
                logger.debug('found an event')
                # do all the work here and block here as well
                # all work on query has to be finished before the polling starts again
                try:
                    await self.handle_event(ts3_event)
                except Exception as e:
                    logger.critical(e)

    def _safe_handle_probe(self, cmd: Command, ts3event):
        """
        Probe and execute a Command if the command matches the received event.
        
        :param cmd: a ts3ekko command to be probed and executed if matching to event
        :param ts3event: a received ts3query event
        :return: ProbeResult
        """
        try:
            logger.debug(f'matching hook found, attempt handling: {cmd}')
            cmd.func(ts3event)
            # event got handled successfully
            # stop searching for handlers
            logger.debug(f'success handling')
            return ProbeResult.SUCCESS
        except EkkoUnsuitedCommand:
            # handler did not want the event or failed to handle it
            # continue probing other handlers
            logger.debug(f'failure handling')
            return ProbeResult.UNSUITED
        except EkkoParsingError:
            # Parser failed to parse the event successfully
            return ProbeResult.PARSING_ERROR
        except EkkoArgparserMessage:
            # Parser successfully parsed event but user requested help or usage information
            return ProbeResult.PARSING_ABORT
        except Exception as f:
            logger.critical(f)
            # Sometimes (for whatever reason) the connection is just not good
            logger.warning(f'resetting clientquery connection ...')
            self.ts3conn = self.create_connection()
            self.ts3conn.clientnotifyregister(event="any", schandlerid=0)
            return ProbeResult.CONN_RESET

    async def handle_event(self, ts3event):
        """
        Process a received event and dispatch the associated/matching command.
        :param ts3event: a received ts3query event
        """
        if ts3event[0].get('invokername', '') == self.bot_username:
            logger.debug(f"filtered message {ts3event[0]} (self sourced)")
            return
        # self.commands is sorted by priority already
        logger.debug(f'event arrived: {ts3event.__dict__}')
        logger.debug(f'current available commands: {self.commands}')
        logger.debug(f'event type: {EventType.get_type(ts3event)}')
        for cmd in self.commands:
            # check if the command hooks on the present ts3event
            if EventType.get_type(ts3event) in cmd.event_hooks:
                probe_result = self._safe_handle_probe(cmd, ts3event)
                if probe_result == ProbeResult.CONN_RESET:
                    if self._safe_handle_probe(cmd, ts3event) == ProbeResult.SUCCESS:
                        # went wrong on first try, but corrected after connreset
                        break
                    else:
                        # went wrong even after connreset
                        break
                elif probe_result == ProbeResult.SUCCESS:
                    # success on first try
                    break
                elif probe_result == ProbeResult.PARSING_ERROR:
                    # matching command was not able to parse the input correctly, abort!
                    break
                elif probe_result == ProbeResult.PARSING_ABORT:
                    # matching command was successfully parsed, but user requested help or usage information
                    break
                else:
                    # not a suited command
                    continue

    async def periodic_update(self, delay: int = 10):
        """
        A coroutine which performs updates/calls functions in a periodic manner. 
        
        It currently does not have any features implemented, other than a keep-alive/debug whoami call. 
        
        :param delay: number of seconds between updates.
        """

        def create_tconn():
            logger.debug('entered periodic update')
            temp_conn = self.create_connection()
            temp_conn.clientnotifyregister(event='any', schandlerid=0)
            logger.debug('created temporary p-u connection')
            return temp_conn

        temp_conn = create_tconn()

        while True:
            temp_conn.send_keepalive()
            try:
                logger.debug('PERIODIC_UPDATE_WHOAMI: ' + str(temp_conn.whoami()[0]))
            except Exception as f:
                logger.critical(f)
                temp_conn = create_tconn()
            await asyncio.sleep(delay)
            logger.debug('p-u sleep done')

    @staticmethod
    def check_cmd_suitability(regex, text, match: bool = False):
        """
        Wrapper for re.match, checks if a regex matches a given text. 
        Raises EkkoUnsuitedCommand on failure to find or to match regex.
        
        :param regex: regular expression to match/find
        :param text: text for regex match/find
        :param match: if regex should be matched (True) or only searched (False)
        :return: True if regex matched/was found and the command was deemed suitable.
        """
        if match:
            if not re.match(regex, text):
                raise EkkoUnsuitedCommand()
        else:
            if not re.search(regex, text):
                raise EkkoUnsuitedCommand()
        # if nothing got raised yet, then the command is suitable
        return True

    def start(self):
        """
        Initiates event polling and periodic updates. 
        """
        self.loop.run_until_complete(
            asyncio.wait([
                self.poll_events(),
                self.periodic_update(),
            ])
        )
