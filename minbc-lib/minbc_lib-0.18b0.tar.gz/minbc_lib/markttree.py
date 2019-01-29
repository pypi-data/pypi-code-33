#coding: utf-8
# マークル木

import matplotlib.pyplot as plt
from hashchain import calc_weakhash

def put_text(ax, line1, line2, pos, color="black"):
    # matplotlibに矩形で囲んだ文字を描く
    size = 14
    if line2:
        tt = r"$\frac{%s}{%s}$" % (line1, line2)
    else:
        tt = r"${%s}$" % line1
        size = 12
    ax.text(pos[0], pos[1], tt, fontsize=size, color=color,
                  bbox=dict(facecolor='none', edgecolor=color))


def calc_node_positions(tree):
    # ツリーの位置を計算する
    # treeには，リストのリストにツリーの情報が入っている
    h1 = 70   # 1段の高さ
    w1 = 420   # ブロックの幅
    offset_h = 20  # 横，縦のオフセット値
    offset_w = -200
    total_h = len(tree)*h1
    total_w = len(tree[-1])*w1
    positions = []
    # 一番下の段の位置を決める
    lp = []
    for i in range(len(tree[0])):
        lp.append((offset_w+i*w1, offset_h))
    positions.append(lp)
    # 二段以降の場所を決める
    for l in range(1, len(tree)):
        tt = tree[l]
        lp = []
        for i in range(len(tt)):
            x = (positions[l-1][i*2][0]+positions[l-1][i*2+1][0])//2
            lp.append((x, offset_h+(l)*h1))
        positions.append(lp)
    return positions


def choose_hash(s):
    # "hash,data"または"hash"という構造の文字列から，hashを取り出す
    if "," in s:
        return s.split(",")[0]
    return s


class MarktTree():
    # マークル木用のクラス
    MAX_LEAVES = 8
    VALID_LENGTH = [2, 4, 8, 16]

    def __init__(self):
        # マークル木を初期化する。下記のようなリストを作りながらマークル木をメンテする
        #     ["41", "42", "43", "44", "45", "46", "47", "48"],
        #    ["31", "32", "33", "34"],
        #    ["21", "22"],
        #    ["1"]
        self.tree = [[]]
        self.invalid = set()
    
    def clear(sefl):
        # マークル木をクリアする
        self.tree = [[]]
        self.invalid = set()

    def add_leaf(self, data):
        # 文字列を渡し，ハッシュを連結してリーフを1つ追加する
        if not data.isalnum():
            raise ValueError("英数字以外の文字は登録できません")
        if not data:
            raise ValueError("空の文字列は登録できません")
        # 空の文字列を除去
        self.tree[0] = [x for x in self.tree[0] if x]
        if len(self.tree[0])  >= self.MAX_LEAVES:
            raise Exception("これ以上リーフを追加できません")
        self.tree[0].append(calc_weakhash(data)+','+data)
        self.build_hash()
    
    def build_hash(self):
        # マークル記のハッシュ構造を作る
        # 必要があれば空のデータを追加して長さを整える
        tlen = len(self.tree[0])
        if len(self.tree[0]) not in self.VALID_LENGTH:
            for tlen in self.VALID_LENGTH:
                if len(self.tree[0]) <= tlen:
                    break
            for i in range(len(self.tree[0]), tlen):
                self.tree[0].append("")
        # ハッシュ値を計算，木を作る
        h = len(bin(tlen))-2
        self.tree = [self.tree[0]]
        for i in range(0, h-1):
            sub = []
            t = self.tree[i]
            for j in range(0, len(t), 2):
                sub.append(calc_weakhash(choose_hash(t[j])+choose_hash(t[j+1])))
            self.tree.append(sub)


    def replace(self, idx, data):
            # インデックスを指定して最下位レベルのデータを置き換える
            if idx >= len(self.tree[0]) or \
               (idx < len(self.tree[0]) and not self.tree[0][idx]):
                raise IndexError("指定のインデックス(%d)にデータはありません" % idx)
            if data == self.tree[0][idx].split(",")[1]:
                return
            self.tree[0][idx] = calc_weakhash(data)+','+data
            self.invalid.add(idx)


    def proof(self):
        # マークル木を描画する
        sz = len(self.tree)/4
        fig, ax = plt.subplots(figsize=(18*sz,8*sz))

        pp = calc_node_positions(self.tree)

        ax.set_xlim([0, 3000*sz])
        ax.set_ylim([0, 300*sz])
        plt.axis("off")

        # ボックスを描く
        for i in range(len(pp)):
            for j in range(len(pp[i])):
                t = self.tree[i][j]
                cl = "black"
                if i == 0 and j in self.invalid:
                    cl = "red"
                if not t:
                    put_text(ax, calc_weakhash(""), "xxx", pp[i][j], cl)
                elif "," in t:
                    tt = t.split(",")
                    put_text(ax, tt[0], tt[1], pp[i][j], cl)
                else:
                    put_text(ax, t, "", pp[i][j], cl)

        oy = 10
        ox = 210

        # ラインを書く
        for i in range(len(pp)-1):
            exy = 0
            if i == 0: exy = 6;
            for j in range(0, len(pp[i]), 2):
                cx = (pp[i][j][0]+pp[i][j+1][0])/2+ox
                cl = "b"
                if i == 0 and j in self.invalid:
                    cl = "r"
                plt.plot((pp[i][j][0]+ox, cx), (pp[i][j][1]+oy+exy, pp[i+1][j//2][1]-oy//2), cl, marker="o")
                cl = "b"
                if i == 0 and j+1 in self.invalid:
                    cl = "r"
                plt.plot((pp[i][j+1][0]+ox, cx), (pp[i][j][1]+oy+exy, pp[i+1][j//2][1]-oy//2), cl, marker="o")



