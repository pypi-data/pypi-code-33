from . import collection_util

_config = {
    "emails": {
        'beastiedog@163.com': {
            'password': '*'
        },
        'tianh@smnpc.com.cn': {
            'password': '*'
        }
    }
}

_config = collection_util.dotdict(_config)