from .tgtype import TelegramType

class TelegramChat(TelegramType):
    FIELDS = {
        'id': int,
        'type': str,
        'title': str,
        'username': str,
        'first_name': str,
        'last_name': str,
        'all_members_are_administrators': bool,
        # photo
        'description': str,
        'invite_link': str,
        'pinned_message': 'TelegramMessage',
        'sticker_set_name': str,
        'can_set_sticker_set': bool,
    }

    REQUIRED = {'chat_id', 'type'}

    def __init__(self, obj):
        super().__init__(obj)

        assert self.id is not None
    
    def __repr__(self):
        return ""
