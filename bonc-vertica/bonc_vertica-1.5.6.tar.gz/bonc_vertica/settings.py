import logging


logging.basicConfig(level=logging.DEBUG)


account_dict = {
    'lzchenzr': 'chenzr.vtc.108',
    'lzdongyj': 'dongyj.vtc.148',
    'lzliyk': 'liyk.vtc.115',
    'lzniexc': 'niexc.vtc.137',
    'lzyuwq': 'yuwq.vtc.107'
    }

db2_account_dict = {
    'lzdmt03': 'L03DMT03'
}


conn_info = {
    "host": "134.96.226.186",
    "port": "5433",
    "user": "lzchenzr",
    "password": "chenzr.vtc.108",
    "database": "zjdw",
    "unicode_error": "replace",
    'connection_timeout': 30,
    }


csv_format_info = {
    'delimiter': ',',
    'quotechar': '"',
    'quoting': True,
    'encoding': 'gb18030'
    }


encodings = (
    'UTF8',
    'GB18030',
    'GB2312',
    'GBK'
    )
