import typing
import logging
from contextlib import contextmanager

from discord.ext import commands


logger = logging.getLogger(__name__)

to_override: typing.List[commands.Command] = []


def override(cmd):
    if not isinstance(cmd, commands.Command):
        raise TypeError('@override must be placed '
                        'above @commands.command(...).')
    if any(cmd.name == o.name for o in to_override):
        logger.warning(f'Multiple override Command named {cmd.name}.')
    to_override.append(cmd)
    return cmd


@contextmanager
def setup(bot: commands.Bot) -> typing.Dict[str,
                                            typing.Optional[commands.Command]]:
    removed_commands = {}
    for cmd in to_override:
        removed_commands[cmd.name] = bot.remove_command(cmd.name)

    yield removed_commands
    
    for name, cmd in removed_commands.items():
        if name not in bot.all_commands:
            logger.warning(f'{name} was never added to bot, '
                           'the original will be used.')
            bot.add_command(cmd)
