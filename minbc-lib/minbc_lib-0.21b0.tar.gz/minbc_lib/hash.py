#coding: utf-8
# ハッシュ

import binascii

def calc_checksum(word):
    # 英数字のチェックサムを計算する
    checksum = 0   # チェックサムを初期化
    for c in word: # 1文字ずつ取り出してループ
        checksum += ord(c) # 文字に相当する数を足す
    return checksum & 0b11111111 # 下位8ビットを取り出す


s1_orig = b'4dc968ff0ee35c209572d4777b721587d36fa7b21bdc56b74a3dc0783e7b9518afbfa200a8284bf36e8e4b55b35f427593d849676da0d1555d8360fb5f07fea2'

s2_orig = b'4dc968ff0ee35c209572d4777b721587d36fa7b21bdc56b74a3dc0783e7b9518afbfa202a8284bf36e8e4b55b35f427593d849676da0d1d55d8360fb5f07fea2'

s1 = binascii.unhexlify(s1_orig)
s2 = binascii.unhexlify(s2_orig)

