#coding: utf-8
# シーザー暗号

def caesar_cipher(word, key):
    # シーザー暗号で文字列を書き換える関数
    encripted = ""  # 書き換え後の文字列を初期化
    for c in word:
        # 文字列から1文字ずつ取り出してループ
        before = ord(c)-65  # Aを起点とした数を計算
        after = (before+key)%26 # keyの数だけずらす
        encripted = encripted+chr(after+65)
    return encripted
