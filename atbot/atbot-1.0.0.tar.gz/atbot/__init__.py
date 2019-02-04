import asyncio
import aiohttp
from typing import Sequence, Union
from enum import Enum

from .tguser import TelegramUser
from .tgmessage import TelegramMessage
from .tgupdate import TelegramUpdate

ParseMode = Enum('ParseMode', {'TEXT': None, 'MARKDOWN': 'Markdown', 'HTML': 'Html'})
ChatAction = Enum('ChatAction', {name: name.lower() for name in 'TYPING UPLOAD_PHOTO RECORD_VIDEO UPLOAD_VIDEO RECORD_AUDIO UPLOAD_AUDIO UPLOAD_DOCUMENT FIND_LOCATION RECORD_VIDEO_NOTE UPLOAD_VIDEO_NOTE'.split(' ')})


class TelegramBot(object):
    def __init__(self, token: str):
        self.client = aiohttp.ClientSession()
        self.token = token
        self._last_offset = -1
    
    async def _post(self, endpoint: str, data: dict = None):
        if data:
            formdata = {
                k: data[k] for k in data.keys() if data[k] is not None
            }
        else:
            formdata = None
        resp = await self.client.post("https://api.telegram.org/bot{0}/{1}".format(self.token, endpoint), json=formdata)
        res = await resp.json()
        return res.get('result')

    async def get_me(self) -> TelegramUser:
        return TelegramUser(await self._post('getMe'))
    
    async def get_updates(self, offset: int = None, limit: int = None, timeout: int = None, allowed_updates: Sequence[str] = None) -> Sequence[TelegramUpdate]:
        updates = await self._post('getUpdates', {
            'offset': offset if offset is not None else (self._last_offset + 1),
            'limit': limit,
            'timeout': timeout,
            'allowed_updates': allowed_updates
            })
        res = [TelegramUpdate(update) for update in updates]
        if len(res) > 0:
            self._last_offset = res[-1].id
        return res

    async def send_message(self, chat_id: int, text: str, parse_mode: ParseMode = None, disable_web_page_preview: bool = None, disable_notification: bool = None, reply_to_message_id: int = None, reply_markup = None) -> TelegramMessage:
        return await self._post('sendMessage', {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode.value if parse_mode else None,
            'disable_web_page_preview': disable_web_page_preview,
            'disable_notification': disable_notification,
            'reply_to_message_id': reply_to_message_id,
            'reply_markup': reply_markup,
        })

    async def send_chat_action(self, chat_id: int, action: ChatAction) -> bool:
        return await self._post('sendChatAction', {
            'chat_id': chat_id,
            'action': action.value if action else None,
        })
