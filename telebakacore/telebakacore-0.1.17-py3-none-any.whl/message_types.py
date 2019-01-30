from telegram import Bot, InputMediaPhoto, constants


class TextMessage:
    def __init__(self, text, chat_id=None, disable_web_page_preview=None, reply_markup=None,
                 parse_mode=None, disable_notification=None):
        self.chat_id = chat_id
        self.text = text
        self.parse_mode = parse_mode
        self.disable_web_page_preview = disable_web_page_preview
        self.reply_markup = reply_markup
        self.disable_notification = disable_notification

    def send(self, bot: Bot):
        bot.send_message(self.chat_id, self.text, self.parse_mode, self.disable_web_page_preview,
                         self.disable_notification, reply_markup=self.reply_markup)


class PhotoMessage:
    def __init__(self, photos, chat_id=None, caption=None, disable_notification=None, reply_markup=None,
                 parse_mode=None):
        self.chat_id = chat_id
        self.photos = photos if isinstance(photos, list) else [photos]
        self.caption = caption or ''
        self.disable_notification = disable_notification
        self.reply_markup = reply_markup
        self.parse_mode = parse_mode

    def send(self, bot: Bot):
        caption = self.caption if len(self.caption) <= constants.MAX_CAPTION_LENGTH else None
        if len(self.photos) == 1:
            bot.send_photo(self.chat_id, self.photos[0], caption, self.disable_notification,
                           reply_markup=self.reply_markup, parse_mode=self.parse_mode, timeout=20)
        else:
            media = []
            for i, p in enumerate(self.photos):
                media.append(InputMediaPhoto(p, i == 0 and caption, self.parse_mode))
            bot.send_media_group(self.chat_id, media, self.disable_notification, timeout=20)
        if caption is None:
            bot.send_message(self.chat_id, self.caption, self.parse_mode,
                             disable_notification=self.disable_notification)
