from .tgtype import TelegramType
from .tgmessage import TelegramMessage

class TelegramUpdate(TelegramType):
    FIELDS = {
        'update_id': ('id', int),
        'message': TelegramMessage,
        'edited_message': TelegramMessage,
        'channel_post': TelegramMessage,
        'edited_channel_post': TelegramMessage,
    }
    REQUIRED = {'update_id', }

    def __init__(self, obj):
        super().__init__(obj)
        
        assert self.id is not None
        assert len(self._populated_fields) == 1
        self.field = self._populated_fields.pop()
        self.obj = self.__getattribute__(self.field)

    def get_obj(self):
        return self.obj
    
    def __repr__(self):
        return "<TelegramUpdate:{0} {1}>".format(self.field, self.obj.__repr__())
