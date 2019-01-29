#coding: utf-8
# 単一換字暗号

from random import shuffle, seed

def get_ctable(s=10):
    # 単一換字暗号の対応表を作る関数
    ctable = []   # 対応表のリストを初期化
    # AからZまでの文字列を持つリストを作る
    for i in range(0, 26): # 0から25までループ
        ctable = ctable+[chr(i+65)]
    seed(10)          # 結果を固定
    shuffle(ctable)  # リストをシャッフルする

    return ctable


def encrypt_ssc(ptext, table):
    # 単一換字暗号で暗号化する関数
    ctext = "" # 暗号文を初期化
    for i in ptext:  # 平文でループ
        idx = ord(i)-65   # Aからの順番を計算
        ctext = ctext+table[idx]  # 対応表を使って置き換え
    return ctext


def decrypt_ssc(ctext, table):
    # 単一換字暗号で復号化する関数
    ptext = "" # 復号化する平文を初期化
    for i in ctext:  # 暗号文でループ
        idx = table.index(i)  # 対応表のインデックスに変換
        ptext = ptext+chr(idx+65)  # 文字を復号化
    return ptext
