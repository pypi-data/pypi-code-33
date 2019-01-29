#coding: utf-8
# ハッシュチェーン

from  binascii import crc32

def calc_weakhash(text):
    # 文字列(text)から8桁の16進数ハッシュを得る
    # 初期値を変えたCRCを二回繰り返し
    # 結果を4桁の16進数にして順番を逆さにしたものをハッシュ値として返す
    f = ('00000000'+hex(crc32(text.encode('utf-8'), 0))[2:])[-8:]
    s = ('00000000'+hex(crc32(text.encode('utf-8'), 128))[2:])[-8:]
    return f+s


def proof(a_list, idx):
    # ハッシュチェーンが壊れているかどうかを確かめる
    h = calc_weakhash(data_list[idx])
    ph = data_list[idx+1].split(",")[1]
    if h == ph:
        return True
    else:
        return False


