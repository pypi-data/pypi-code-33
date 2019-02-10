from .user import User as _User
from .command import Command as _Command


class Converter:
    @staticmethod
    async def convert(ctx, param):
        return param


class ChatCommand(Converter, _Command):
    @staticmethod
    async def convert(ctx, cmd):
        if cmd in ctx.bot.commands:
            return ctx.bot.commands[cmd]
        raise ConvertError(f'Chat command {cmd} does not exist!')


class User(Converter):
    @staticmethod
    async def convert(ctx, user):
        _user = await ctx.bot.user(user)
        if isinstance(_user, _User) and _user.is_api():
            return _user
        raise ConvertError(f'User {user} does not exist!')


class ConvertError(BaseException):
    pass
