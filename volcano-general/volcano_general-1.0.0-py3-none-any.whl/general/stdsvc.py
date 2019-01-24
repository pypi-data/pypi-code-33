
import datetime

from .tstamp import serialize_tstamp, deserialize_tstamp_w
from .stdsvcdef import IMsgOStream, IHandshakeService, ISetValueService, IFindTagHandler, IFindTagService, IEchoService, ITagUpdateHandler, ISubscribeService, ISubscribeAllService, ITagIterHandler, ITagIterService
from .stddef import VOLCANO_PROTOCOL_VERSION_STR


def msg_get_w(msg: dict, param_name: str, test_type=None, optional: bool = False, default=None):
    assert isinstance(msg, dict), msg
    assert isinstance(param_name, str), param_name

    if param_name not in msg:
        if optional:
            return default
        raise Warning('Message "{}" does not have obligatory property "{}"'.format(msg, param_name))

    val = msg[param_name]
    if test_type is not None and not isinstance(val, test_type):
        raise Warning('Property "{}={}" should be {} in message {}'.format(param_name, val, test_type, msg))

    return val


def msg_get_tstamp_w(msg: dict, param_name: str, optional: bool = False) -> (None, datetime.datetime):
    s = msg_get_w(msg, param_name, str, optional, None)
    return deserialize_tstamp_w(s)


class HandshakeService(IHandshakeService, IMsgOStream):
    protocol_version = VOLCANO_PROTOCOL_VERSION_STR

    def __init__(self, transport: IMsgOStream):
        assert isinstance(transport, IMsgOStream), transport

        # self.transport_: IMsgOStream = transport
        self.transport_ = transport

    def salute(self, inst_name: str) -> None:
        assert isinstance(inst_name, str), inst_name
        self.transport_.push_single_message({'c': "hello", 'name': inst_name, 'protocol': self.protocol_version})

    def push_single_message(self, msg: dict) -> None:
        if msg['c'] != 'welcome':
            raise Exception('Expected welcome from server, got {}'.format(msg))


class SingleThreadEchoService(IEchoService, IMsgOStream):
    def __init__(self, transport: IMsgOStream):
        assert isinstance(transport, IMsgOStream), transport
        self.transport_ = transport
        self.echo_cbs_ = []  # [(counter, callback, *args, **kwargs), ...]
        self.echo_cbs_ctr_ = 0

    def echo(self, callback, *args, **kwargs) -> None:
        self.echo_cbs_ctr_ += 1
        self.echo_cbs_.append((self.echo_cbs_ctr_, callback, args, kwargs))

        self.transport_.push_single_message({'c': 'echo', 'ctr': self.echo_cbs_ctr_})

    def push_single_message(self, msg: dict) -> None:
        assert isinstance(msg, dict), msg

        if not self.echo_cbs_:
            raise Exception('Echo Request/response mismatch')

        ctr = msg['ctr']

        requested_ctr, cb, args, kwargs = self.echo_cbs_.pop(0)
        if requested_ctr != ctr:
            raise Exception('Echo Request/response mismatch. Requested {}, got {}'.format(requested_ctr, ctr))

        cb(*args, **kwargs)


class SingleThreadFindTagService(IFindTagService, IMsgOStream):
    def __init__(self, transport: IMsgOStream):
        assert isinstance(transport, IMsgOStream), transport
        self.transport_ = transport
        self.find_tag_cbs_ = []

    def find_tag(self, tag_name_or_id: (int, str), handler: IFindTagHandler, user_data=None) -> None:
        assert isinstance(tag_name_or_id, (int, str)), tag_name_or_id
        assert isinstance(handler, IFindTagHandler), handler

        self.find_tag_cbs_.append((tag_name_or_id, handler, user_data))
        self.transport_.push_single_message({'c': 'find', 'tag': tag_name_or_id})

    def push_single_message(self, msg: dict) -> None:
        assert isinstance(msg, dict), msg

        assert self.find_tag_cbs_

        tag_name_or_id, handler, user_data = self.find_tag_cbs_.pop(0)

        if msg['c'] == 'find_ok':
            tag_id = msg_get_w(msg, 'id', test_type=int)
            tag_name = msg_get_w(msg, 'name', test_type=str)
            vt = msg_get_w(msg, 'type', test_type=str)

            handler.on_find_tag_ok(tag_id, tag_name, vt, user_data)
        else:
            assert msg['c'] == 'find_err'
            handler.on_find_tag_err(tag_name_or_id, user_data)


class SingleThreadTagIterService(ITagIterService, IMsgOStream):
    def __init__(self, transport: IMsgOStream):
        assert isinstance(transport, IMsgOStream), transport
        self.transport_ = transport
        # self.handler_: ITagIterHandler = None
        self.handler_ = None

    def first(self, handler: ITagIterHandler):
        assert isinstance(handler, ITagIterHandler), handler

        self.handler_ = handler
        self.transport_.push_single_message({'c': 'first'})

    def next(self, tag_name_or_id: (int, str), handler: ITagIterHandler):
        assert isinstance(tag_name_or_id, (int, str)), tag_name_or_id
        assert isinstance(handler, ITagIterHandler), handler

        self.handler_ = handler
        self.transport_.push_single_message({'c': 'next', 'tag': tag_name_or_id})

    def push_single_message(self, msg: dict) -> None:
        assert isinstance(msg, dict), msg

        handler = self.handler_
        self.handler_ = None    # сбросить надо имеено здесь, так как в handler.on_next_tag с большой вероятностью будет вызван .next()
        assert handler

        if msg['c'] == 'next_tag':
            tag_id = msg_get_w(msg, 'id', test_type=int)
            tag_name = msg_get_w(msg, 'name', test_type=str)
            vt = msg_get_w(msg, 'type', test_type=str)
            atts = msg_get_w(msg, 'atts')

            handler.on_next_tag(tag_id, tag_name, vt, atts)

        elif msg['c'] == 'next_end':
            handler.on_next_end()
        else:
            assert msg['c'] == 'next_err'
            handler.on_next_err()


class PipeMarker(IMsgOStream):
    def __init__(self, channel: IMsgOStream, channel_uid):
        self.out_channel_ = channel
        self.uid_ = channel_uid

    def push_single_message(self, msg: dict) -> None:
        msg['ch'] = self.uid_
        self.out_channel_.push_single_message(msg)


# Поскольку данный сервис не имеет собственного кэша сообщений, он является многопоточным (транспорт в свою очередь тоже должен быть МП)
class MultiThreadSetValueService(ISetValueService):
    def __init__(self, transport: IMsgOStream):
        assert isinstance(transport, IMsgOStream), transport

        # self.transport_: IMsgOStream = transport
        self.transport_ = transport

    def set_tag(self, tag_name_or_id: (str, int), value, quality: int = 0, tstamp: ('datetime.datetime', None) = None) -> None:
        assert isinstance(tag_name_or_id, (str, int)), tag_name_or_id
        assert isinstance(quality, int), quality
        assert tstamp is None or isinstance(tstamp, datetime.datetime), tstamp

        req = {'c': 'set', 'tag': tag_name_or_id, 'v': value}
        if quality:
            req['q'] = quality
        if tstamp:
            req['t'] = serialize_tstamp(tstamp)

        self.transport_.push_single_message(req)


class SingleThreadSubscribeService(ISubscribeService):
    def __init__(self, transport: IMsgOStream):
        assert isinstance(transport, IMsgOStream), transport

        # self.transport_: IMsgOStream = transport
        self.transport_ = transport
        self.subs_ = {}  # {name_or_id:(handler, *args, **kwargs), ...}

    def subscribe(self, tag_name_or_id: (int, str), send_tstamp: bool, handler: ITagUpdateHandler) -> None:
        assert isinstance(tag_name_or_id, (int, str)), tag_name_or_id
        assert isinstance(send_tstamp, bool), send_tstamp
        assert isinstance(handler, ITagUpdateHandler), handler

        assert tag_name_or_id not in self.subs_, tag_name_or_id

        self.subs_[tag_name_or_id] = handler

        self.transport_.push_single_message({'c': 'sub', 'tag': tag_name_or_id, 'tstamp': send_tstamp})

    def push_single_message(self, msg: dict) -> None:
        assert isinstance(msg, dict), msg
        assert msg['c'] == 'upd', msg

        tag_name_or_id = msg_get_w(msg, 'tag', test_type=(int, str))
        val_raw = msg_get_w(msg, 'v')
        quality = msg_get_w(msg, 'q', test_type=int)
        tstamp_n = msg_get_tstamp_w(msg, 't', optional=True)

        assert tag_name_or_id in self.subs_, tag_name_or_id
        handler = self.subs_[tag_name_or_id]
        handler.on_tag_updated(tag_name_or_id, val_raw, quality, tstamp_n)


class SingleThreadSubscribeAllService(ISubscribeAllService):
    def __init__(self, transport: IMsgOStream):
        assert isinstance(transport, IMsgOStream), transport

        # self.transport_: IMsgOStream = transport
        self.transport_ = transport
        self.handler_ = None

    def subscribe_all(self, send_tstamp: bool, use_tag_id: bool, handler: ITagUpdateHandler) -> None:
        assert isinstance(send_tstamp, bool), send_tstamp
        assert isinstance(use_tag_id, bool), use_tag_id
        assert isinstance(handler, ITagUpdateHandler), handler

        assert self.handler_ is None, 'Duplicated subscribe All call'

        # self.handler_: ITagUpdateHandler = handler
        self.handler_ = handler

        self.transport_.push_single_message({'c': 'sub', 'tag': '*', 'tstamp': send_tstamp, 'ref': 'id' if use_tag_id else 'name'})

    def push_single_message(self, msg: dict) -> None:
        assert isinstance(msg, dict), msg
        assert msg['c'] == 'upd', msg

        tag_name_or_id = msg_get_w(msg, 'tag', test_type=(int, str))
        val_raw = msg_get_w(msg, 'v')
        quality = msg_get_w(msg, 'q', test_type=int)
        tstamp_n = msg_get_tstamp_w(msg, 't', optional=True)

        assert self.handler_
        self.handler_.on_tag_updated(tag_name_or_id, val_raw, quality, tstamp_n)


class SingleThreadAllService(IMsgOStream, IHandshakeService, ISetValueService, IEchoService, IFindTagService, ITagIterService,  # pylint: disable=too-many-ancestors
                             ISubscribeService, ISubscribeAllService):

    def __init__(self, transport: IMsgOStream):
        assert isinstance(transport, IMsgOStream), transport

        # self.transport_: IMsgOStream = transport
        self.transport_ = transport

        self.services_ = {
            'hs': HandshakeService(PipeMarker(transport, 'hs')),
            'set': MultiThreadSetValueService(transport),
            'echo': SingleThreadEchoService(PipeMarker(transport, 'echo')),
            'find': SingleThreadFindTagService(PipeMarker(transport, 'find')),
            'next': SingleThreadTagIterService(PipeMarker(transport, 'next')),
            'sub': SingleThreadSubscribeService(PipeMarker(transport, 'sub')),
            'suball': SingleThreadSubscribeAllService(PipeMarker(transport, 'suball')),
        }

    def salute(self, inst_name: str) -> None:
        self.services_['hs'].salute(inst_name)

    def set_tag(self, tag_name_or_id: (str, int), value, quality: int = 0, tstamp: ('datetime.datetime', None) = None) -> None:
        self.services_['set'].set_tag(tag_name_or_id, value, quality, tstamp)

    def echo(self, callback, *args, **kwargs) -> None:
        self.services_['echo'].echo(callback, *args, **kwargs)

    def find_tag(self, tag_name_or_id: (str, int), handler: IFindTagHandler, user_data=None) -> None:
        self.services_['find'].find_tag(tag_name_or_id, handler, user_data)

    def first(self, handler: ITagIterHandler):
        self.services_['next'].first(handler)

    def next(self, tag_name_or_id: (int, str), handler: ITagIterHandler):
        self.services_['next'].next(tag_name_or_id, handler)

    def subscribe(self, tag_name_or_id: (int, str), send_tstamp: bool, handler: ITagUpdateHandler) -> None:
        self.services_['sub'].subscribe(tag_name_or_id, send_tstamp, handler)

    def subscribe_all(self, send_tstamp: bool, use_tag_id: bool, handler: ITagUpdateHandler) -> None:
        self.services_['suball'].subscribe_all(send_tstamp, use_tag_id, handler)

    # as soon as this method is called from transport, it doesnt swallow exceptions
    def push_single_message(self, msg: dict) -> None:
        assert isinstance(msg, dict), msg

        assert 'ch' in msg
        ch_name = msg['ch']

        assert ch_name in self.services_
        self.services_[ch_name].push_single_message(msg)


'''
class SingleThreadOnDemandServices(IMsgOStream):
    def __init__(self, transport: IMsgOStream):
        assert isinstance(transport, IMsgOStream), transport

        #self.transport_: IMsgOStream = transport
        self.transport_ = transport
        self.services_ = {}

    @property
    def svc_set(self) -> ISetValueService:
        if 'set' not in self.services_:
            self.services_['set'] = MultiThreadSetValueService(self.transport_)
        return self.services_['set']

    @property
    def svc_find(self) -> IFindTagService:
        if 'find' not in self.services_:
            self.services_['find'] = SingleThreadFindTagService(PipeMarker(self.transport_, 'find'))
        return self.services_['find']

    @property
    def svc_echo(self) -> IEchoService:
        if 'echo' not in self.services_:
            self.services_['echo'] = SingleThreadEchoService(PipeMarker(self.transport_, 'echo'))
        return self.services_['echo']

    @property
    def svc_next(self) -> ITagIterService:
        if 'next' not in self.services_:
            self.services_['next'] = SingleThreadTagIterService(PipeMarker(self.transport_, 'next'))
        return self.services_['next']

    @property
    def svc_sub(self) -> ISubscribeService:
        if 'sub' not in self.services_:
            self.services_['sub'] = SingleThreadSubscribeService(PipeMarker(self.transport_, 'sub'))
        return self.services_['sub']

    @property
    def svc_sub_all(self) -> ISubscribeAllService:
        if 'suball' not in self.services_:
            self.services_['suball'] = SingleThreadSubscribeAllService(PipeMarker(self.transport_, 'suball'))
        return self.services_['suball']
    """
    def svc(self, svc_name: str):
        assert isinstance(svc_name, str), svc_name
        assert svc_name in self.services_, (svc_name, self.services_)

        return self.services_[svc_name]

    def add_svc(self, svc_name: str, svc_type):
        assert isinstance(svc_name, str), svc_name
        assert svc_name not in self.services_, svc_name

        self.services_[svc_name] = svc_type(PipeMarker(self.transport_, svc_name))
    """
'''     # pylint: disable=pointless-string-statement
