# 引入哈希库
import hashlib
import random
import datetime
from .sqlalchemy import BaseModel, Base
from sqlalchemy import Column, Integer, String, DATETIME
from .config import config


class UrlUuid(Base, BaseModel):
    # 表的名字:
    __tablename__ = 'short_urls'
    __label__ = 'mysql_short_url'
    __database__ = config(__label__, 'database')
    id = Column(String(16), primary_key=True)
    url = Column(String(128))
    create_time = Column(DATETIME())
    modify_time = Column(DATETIME())


def get_md5(s):
    s = s.encode('utf8')
    m = hashlib.md5()
    print(m)
    m.update(s)
    return m.hexdigest()


def get_sha224(s):
    code = hashlib.sha3_256(s.encode('utf8'))
    return code.hexdigest()


code_map = (
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
    'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
    'q', 'r', 's', 't', 'u', 'v', 'w', 'x',
    'y', 'z', '0', '1', '2', '3', '4', '5',
    '6', '7', '8', '9', 'A', 'B', 'C', 'D',
    'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
    'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
    'U', 'V', 'W', 'X', 'Y', 'Z'
)


def get_hash_key(long_url):
    hkeys = []
    hex = get_sha224(long_url)
    for i in range(0, 8):
        n = int(hex[i * 8:(i + 1) * 8], 16)
        v = []
        e = 0
        for j in range(0, 7):
            x = 0x0000003D & n
            e |= ((0x00000002 & n) >> 1) << j
            v.insert(0, code_map[x])
            n = n >> 6
        e |= n << 5
        v.insert(0, code_map[e & 0x0000003D])
        hkeys.append(''.join(v))
    return hkeys


def get_url_uuid_list(long_url):
    uuid_list = get_hash_key(long_url)
    return uuid_list


def insert_url_hash_key(long_url):
    uuid_list = get_url_uuid_list(long_url)
    _res = {
        'code': -1,  # 0插入成功，1已插入，-1失败
        'msg': 'error',
        'uuid': ''
    }
    res = UrlUuid.get_by_ids(uuid_list)
    _now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for url_entity in res:
        if url_entity.url == long_url:
            _res['uuid'], _res['code'], _res['msg'] = url_entity.id, 1, 'success'
            return _res
        else:
            uuid_list.remove(url_entity.id)
    if len(uuid_list) == 0:
        _res['msg'] = 'not enough uuid'
    else:
        uuid = uuid_list[random.randint(0, len(uuid_list))]
        url_entity = UrlUuid(id=uuid, url=long_url, create_time=_now, modify_time=_now)
        UrlUuid.save(url_entity)
        _res['uuid'], _res['code'], _res['msg'] = uuid, 0, 'success'
    return _res
