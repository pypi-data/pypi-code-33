
class TelegramUser(object):
    def __init__(self, obj):
        self.id = obj.get('id')
        self.is_bot = obj.get('is_bot')
        self.first_name = obj.get('first_name')
        self.last_name = obj.get('last_name')
        self.username = obj.get('username')
        self.language_code = obj.get('language_code')

        assert self.id is not None and self.first_name is not None and self.is_bot is not None
    
    def __repr__(self):
        dn = '"' + self.first_name
        if self.last_name:
            dn += " " + self.last_name
        dn += '"'
        if self.username:
            dn += " @" + self.username
        if self.is_bot:
            dn += " [BOT]"
        return "<TelegramUser {0}>".format(dn)
