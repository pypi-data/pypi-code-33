#coding: utf-8
# RSA暗号

# 最大公約数を求める関数を読み込む
from math import gcd

def lcm(a, b):
    # aとbの最小公倍数を求める
    m = a*b    # aとbを掛け合わせる
    # a×bを最大公約数で割って最小公倍数を求める
    return m//gcd(a, b)


def generate_keys(p, q):
    # 暗号化の鍵を求める
    N = p*q  # p×qを求める
    L = lcm(p-1, q-1)  #p-1, q-1の最小公倍数を求める
    for i in range(2, L):
        # 1以上L以下でLとの最大公約数が1の数を求める
        if gcd(i, L) == 1:
            E = i  # 見つかったので変数に代入
            break  # ループを終了
    for i in range(2, L):
        # 1以上L以下でLとの最大公約数が1の数を求める
        if (E*i) % L == 1:
            D = i  # 見つかったので変数に代入
            break # ループを終了
    return E, D, N


def rsa_encrypt(p, E, N):
    # RSA暗号で暗号化
    return (p**E)%N


def rsa_decrypt(e, D, N):
    # RSA暗号で復号化
    return (e**D)%N



