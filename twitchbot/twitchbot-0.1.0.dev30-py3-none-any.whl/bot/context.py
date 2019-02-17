import twitchbot.irc
import twitchbot.bot.user
import twitchbot.api.user


class Context:
    def __init__(self, bot, message: twitchbot.irc.Message = None, invoked_with: str = None, args: list = None):
        self.bot: twitchbot.bot.bot.Bot = bot
        self._message = message
        if self._message:
            if self._message.author:
                self.author = self._message.author
                self.mention = None
            else:
                self.author = None
                self.mention = None
            self.content = self._message.content
            if self._message.channel:
                self.channel = self._message.channel
            else:
                self.channel = None
            self.tags = self._message.tags
            self.command = self._message.command
        else:
            self.author = None
            self.mention = None
            self.channel = None
            self.command = None
            self.tags = None
        self.invoked_with: str = invoked_with
        self.arguments: list = args

    async def init(self):
        if self.channel and not isinstance(self.channel, twitchbot.bot.user.User):
            self.channel = await self.bot.user(self.channel)
        if self.author and not isinstance(self.author, twitchbot.bot.user.User):
            self.author = await self.bot.user(self.author)
        if isinstance(self.author, twitchbot.bot.user.User) and self.author.is_api():
            self.mention = self.author.mention

    def argument(self, num):  # Return the original argument before conversion passed to context
        if len(self.arguments) >= num:
            return self.arguments[num - 1]
        return False

    async def send(self, message):
        await self.bot.irc.send_pmsg(message)
