#coding: utf-8
# 論理演算を使った暗号化

from collections import Counter
import matplotlib.pyplot as plt

def binary_cipher(plist, key):
    # XORを使って数のリストを暗号化する
    result = []   # 結果を保存するリストを初期化
    for p, k in zip(plist, key):  # 2つのリストを使ってループ
        result.append(p ^ k)   # XORの結果をリストに追加
    return result


def KSA(key):
    # 0から255までのリストを作りシャッフルする
    k = list(range(256))  # 0から255までのリストを作る
    j = 0   # 入れ替えに使うインデックスを初期化
    for i in range(256): # 0から255までループ
        # 入れ替えに使うインデックスを計算
        j = (j+k[i]+ key[i % len(key)]) % 256
        k[i], k[j] = k[j], k[i]  # リストを入れ替える
    return k


def PRGA(k, l):
    # 0から255までの疑似乱数をl個生成する
    i = 0
    j = 0 # 入れ替えに使うインデックスを初期化
    key = []  # キーストリーム用のリストを初期化
    for c in range(l):
        i = (i + 1) % 256
        j = (j + k[i]) % 256  # 入れ替え用のインデックスを計算
        k[i], k[j] = k[j], k[i]  # リストを入れ替える
        key.append(k[(k[i] + k[j]) % 256])
    return key


def show_rc4_randdomness(keystream):
    # RC4のキーストリームを8ビットの値ごとに集計し
    # 出現回数を棒グラフに描画する
    c = Counter(keystream)
    ci = list(c.items())
    ci.sort(key = lambda x: x[0])
    plt.bar(list(range(256)), [x[1] for x in ci])


def p(num):
    # 4ビットの数を転置する
    res = (num&1)<<3 | (num&2)<<1 | (num&4)>>2 | (num&8)>>2
    return res


def r_p(num):
    # 4ビットの数を転置する(逆)
    res = (num&1)<<2 | (num&2)<<2 | (num&4)>>1 | (num&8)>>3
    return res


# 換字用のリスト
sbox = [12, 5, 6, 11, 9, 0, 10, 13, 3, 14, 15, 8, 4, 7, 1, 2]

def s(num):
    # 換字を行う関数
    return sbox[num]

def r_s(num):
    # 換字を行う関数(逆)
    return sbox.index(num)


def simple_bcipher(num, key):
    # ブロック暗号で暗号化する
    r = s(num)  # 転置
    r = r ^ key # ラウンド鍵でXOR
    r = p(r)      # 換字
    return r

def r_simple_bcipher(num, key):
    # ブロック暗号で復号化する
    r = r_p(num)      # 換字
    r = r ^ key # ラウンド鍵でXOR
    r = r_s(r)  # 転置
    return r


