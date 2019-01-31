from . import collection_util

_config = {
    "emails": {
        'beastiedog@163.com': {
            'password': 'Password163'
        },
        'tianh@smnpc.com.cn': {
            'password': 'Sm123321'
        }
    }
}

_config = collection_util.dotdict(_config)