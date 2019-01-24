# Здесь собраны "классические" определения сервисов


# Все нижеописанные сервисы подразумевают наличие канала отправки сообщений, причем неважно, на чем реализованного
class IMsgOStream:
    def push_single_message(self, msg: dict) -> None:
        raise NotImplementedError()

    def push_multiple_messages(self, messages: (list, tuple)) -> None:
        assert isinstance(messages, (list, tuple)), messages
        for m in messages:
            self.push_single_message(m)

    def flush(self) -> None:
        pass


class IHandshakeService:
    def salute(self, inst_name: str) -> None:
        raise NotImplementedError()


class ISetValueService:
    def set_tag(self, tag_name_or_id: (str, int), value, quality: int = 0, tstamp: ('datetime.datetime', None) = None) -> None:
        raise NotImplementedError()


class IFindTagHandler:
    def on_find_tag_ok(self, tag_id: int, tag_name: str, vt: str, user_data):
        raise NotImplementedError()

    def on_find_tag_err(self, tag_name_or_id: (int, str), user_data):
        raise NotImplementedError()


class IFindTagService:
    def find_tag(self, tag_name_or_id: (str, int), handler: IFindTagHandler, user_data=None) -> None:
        raise NotImplementedError()


class IEchoService:
    def echo(self, callback, *args, **kwargs) -> None:
        raise NotImplementedError()


class ITagUpdateHandler:
    def on_tag_updated(self, tag_name_or_id: (int, str), val_raw, quality: int, tstamp_n: ('datetime.datetime', None)):
        raise NotImplementedError()


class ISubscribeService:
    def subscribe(self, tag_name_or_id: (int, str), send_tstamp: bool, handler: ITagUpdateHandler) -> None:
        raise NotImplementedError()


class ISubscribeAllService:
    def subscribe_all(self, send_tstamp: bool, use_tag_id: bool, handler: ITagUpdateHandler):
        raise NotImplementedError()


class ITagIterHandler:
    def on_next_tag(self, tag_id: int, tag_name: str, vt: str, atts: dict):
        raise NotImplementedError()

    def on_next_end(self):
        raise NotImplementedError()

    def on_next_err(self):
        raise NotImplementedError()


class ITagIterService:
    def first(self, handler: ITagIterHandler):
        raise NotImplementedError()

    def next(self, tag_name_or_id: (int, str), handler: ITagIterHandler):
        raise NotImplementedError()
