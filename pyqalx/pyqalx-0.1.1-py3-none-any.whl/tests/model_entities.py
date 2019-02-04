import datetime
from uuid import uuid4

item1_guid = uuid4().hex
item2_guid = uuid4().hex
item3_guid = uuid4().hex
item4_guid = uuid4().hex

set1_guid = uuid4().hex
set2_guid = uuid4().hex

group1_guid = uuid4().hex

info = {"created": datetime.datetime.now().isoformat()}
item_file_post = {
    "data": {"some": "data"},
    "file": "/path/to/a/file"
}
item_file_response = {
    "guid": item1_guid,
    "info": info,
    "data": {"some": "data"},
    "file": {
        'url': 'https://s3-signed-url.com'
    }
}
bot_post = {
    'guid': uuid4().hex,
    'info': {
        'credentials': {'token': 'AFAKETOKEN'}
    }
}
queue_post = {
    "parameters": {"some": "param"},
    "meta": {"queue_name": "reeeally unique name..."}
}
queue_response = {
    "guid": uuid4().hex,
    "info": {"created": datetime.datetime.now().isoformat(),
             "queue_url": "https://a.queue.com/123456789",
             "credentials":
                 {
                     'ACCESS_KEY_ID': 'AccessKeyId',
                     'SECRET_ACCESS_KEY': 'SecretAccessKey',
                     'SESSION_TOKEN': 'SessionToken',
                     'EXPIRATION': 'Expiration',
                 }
             },
    "parameters": {"some": "param"},
    "meta": {"queue_name": "reeeally unique name..."}

}
entities_response = {
    'item': [
        {
            "guid": item1_guid,
            "info": info,
            "data": {"some": "data"}
        },
        {
            "guid": item2_guid,
            "info": info,
            "data": {"some": "data"}
        },
        {
            "guid": item3_guid,
            "info": info,
            "data": {"some": "data"}
        },
        {
            "guid": item4_guid,
            "info": info,
            "data": {"some": "data"}
        },
    ],
    "set": [
        {
            "guid": set1_guid,
            "info": info,
            "item_guids": [item1_guid, item2_guid, item3_guid, item4_guid]
        },
        {
            "guid": set2_guid,
            "info": info,
            "item_guids": [item1_guid, item2_guid, item4_guid]
        },
    ],
    "group": [
        {
            "guid": group1_guid,
            "info": info,
            "set_guids": [set1_guid, set2_guid]
        }
    ]
}
