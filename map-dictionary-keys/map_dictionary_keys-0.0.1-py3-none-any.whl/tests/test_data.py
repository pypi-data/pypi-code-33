input_dict = {
    'key1': {
        'key2': {
            'key3': 'value1'
        }
    },
    'key4': [
        {
            'key5': {
                'key6': 'value2'
            }
        },
        {
            'key7': 'value3'
        }
    ],
    'key8': [
        'value4',
        5
    ],
    'key9': 'value6',
    'key10': 7
}

expected_output = {
    'KEY1': {
        'KEY2': {
            'KEY3': 'value1'
        }
    },
    'KEY4': [
        {
            'KEY5': {
                'KEY6': 'value2'
            }
        },
        {
            'KEY7': 'value3'
        }
    ],
    'KEY8': [
        'value4',
        5
    ],
    'KEY9': 'value6',
    'KEY10': 7
}