from . import collection_util
from . import _config_private

# mail

config = {
    "emails": {
        'beastiedog@163.com': {
            'username': 'beastiedog',
            'fullname': 'SweetRiver',
            'smtp': "smtp.163.com",
            'port': 465,
            'ssl': True,
            'password': 'Password163'
        },
        'tianh@smnpc.com.cn': {
            'username': 'tianh',
            'fullname': 'Tian He',
            'smtp_host': "smtp.smnpc.com.cn",
            'smtp_port': 465,
            'ssl': True,
            'password': 'Sm123321'
        }
    }
}

config = collection_util.dotdict(config)

