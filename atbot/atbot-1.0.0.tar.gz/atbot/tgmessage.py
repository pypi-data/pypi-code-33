from .tgtype import TelegramType
from .tguser import TelegramUser
from .tgchat import TelegramChat

class TelegramMessage(TelegramType):
    FIELDS = {
        'message_id': ('id', int),
        'from': ('sender', TelegramUser),
        'date': int,
        'chat': TelegramChat,
        'forward_from': TelegramUser,
        'forward_from_chat': TelegramChat,
        'forward_from_message_id': int,
        'forward_signature': str,
        'forward_date': int,
        # 'reply_to_message': 'TelegramMessage',
        'edit_date': int,
        'media_group_id': str,
        'author_signature': str,
        'text': str,
        # entities,
        # caption_entities,
        # audio
        # document
        # animation
        # game
        # photo
        # sticker
        # video
        # voice
        # video_note
        'caption': str,
        # contact
        # location
        # venue
        # new_chat_members
        'left_chat_member': TelegramUser,
        'new_chat_title': str,
        # new_chat_photo
    }

    REQUIRED = {'message_did', 'date', 'chat'}

    def __init__(self, obj):
        super().__init__(obj)
    
    def __repr__(self):
        return "<TelegramMessage from:{0} msg:{1}>".format(self.sender, self.text)
