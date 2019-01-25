import asyncio
from aiohttp import ClientSession as Session
from bs4 import BeautifulSoup
from .player import Player
import re

user_agent = {'User-Agent': 'pybuff'}


class BadBattletag(Exception):
    """ Raised when a battletag is invalid """
    def __init__(self, message, btag):
        super().__init__(message)
        self.btag = btag


async def get_player(battletag, platform='pc', session=None):
    """ Return a Player object from a battletag.

        :param str battletag:
            A player's Battlenet tag.
            ex. Tydra#11863
        :param str platform:
            The platform the player is on; default is 'pc'
            Valid platforms:
                - pc
                - xbl
                - psn
        :param aiohttp.ClientSession session:
            Session to make requests with.
            Passing an existing session would be a little quicker when calling this method a lot.
        :rtype:
            Player object
        :returns:
            An overview of a player's profile.
    """

    pc_btag = re.compile('\w{1,}#\d{4,6}')
    if not pc_btag.match(battletag) and platform == 'pc':
        raise BadBattletag(
            f"\"{battletag}\" is not a valid battletag.",
            battletag,
        )

    url_tag = battletag.replace('#', '-')
    url = f"https://overbuff.com/players/{platform}/{url_tag}"

    async def _get_player(client_session: Session) -> Player:
        async with client_session.get(url, headers=user_agent) as page:
            if page.status == 404:
                raise BadBattletag(
                    f"Unable to find \"{battletag}\".",
                    battletag,
                )

            soup = BeautifulSoup(await page.text(), 'html.parser')
            return Player(battletag, platform, soup)

    if not session:
        async with Session() as session:
            return await _get_player(session)
    else:
        return await _get_player(session)
