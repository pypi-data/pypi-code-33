from .user import User as _User
from .game import Game as _Game
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


class User(Converter, _User):
    @staticmethod
    async def convert(ctx, user):
        _user = await ctx.bot.user(user)
        if isinstance(_user, _User) and _user.is_api():
            return _user
        raise ConvertError(f'User {user} does not exist!')


class Game(Converter, _Game):
    @staticmethod
    async def convert(ctx, game):
        _game = await ctx.bot.game(game)
        if isinstance(_game, _Game) and _game.is_api():
            return _game
        raise ConvertError(f'Game {game} does not exist!')


class ConvertError(BaseException):
    pass
