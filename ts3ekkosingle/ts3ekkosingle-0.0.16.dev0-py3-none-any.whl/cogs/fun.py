import logging
import random

from ts3ekkoutil.envconsts import EkkoPropertyNames as epn

try:
    from ts3ekkosingle.event_type import EventType
    from ts3ekkosingle.errors import EkkoUnsuitedCommand
    from ts3ekkosingle.argparser import NonExitParser, FunParser
except ImportError:
    from ..event_type import EventType
    from ..errors import EkkoUnsuitedCommand
    from ..argparser import NonExitParser,  FunParser

class FunPermission:
    DICE = 'fun.dice'

class FunCog:
    def __init__(self, ekkobot, args):
        self.ekko_bot = ekkobot


    @property
    def commands(self):
        """
        Returns data for command hooks creation for events like mediaalias set/get, etc.

        :return list of tuple in format: (EventType-int, callback-func, priority-int, name-str, help_cmd_str-str)
        """
        return [
            (EventType.TEXTMESSAGE, self.cmd_dice, 100, None, '!dice'),
        ]


    def cmd_dice(self, event):
        """
        Command: !dice

        :param event: TS3Event
        """
        cmd_prefix = '!dice'
        if self.ekko_bot.check_cmd_suitability(f'^{cmd_prefix}', event[0]['msg']):
            if self.ekko_bot.can(FunPermission.DICE, event):
                force, string = self.ekko_bot.parse(FunParser.parse_force_dice, event, cmd_prefix, event[0]['msg'])
                if not force:
                    self.ekko_bot.reply("Who do you think I am, the Taninator ? ", event)
                else:
                    choices = string.split(',')
                    self.ekko_bot.reply(f"The die rolls and lands on {random.choice(choices)}.", event)