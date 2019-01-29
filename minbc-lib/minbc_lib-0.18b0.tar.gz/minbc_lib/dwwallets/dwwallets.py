#coding: utf-8
# 入出金履歴用ユーティリティ

from IPython.display import display

from pandas import DataFrame

from collections import Counter
from math import pi

import matplotlib.pyplot as plt

from bokeh.palettes import Category20c
from bokeh.plotting import figure, show
from bokeh.transform import cumsum
from bokeh.io import output_notebook

from .plist_a import pl_a
from .plist_b import pl_b
from .plist_c import pl_c

YEAR = 2018

__all__ = ('CDataFrame', 'get_wallet', 'bar_chart')

class CDataFrame(list):
    """
    DataFrame由来のクラス，簡単な計算やグラフ描画を行う
    """
    _metadata = "pl"
    COLS = ['0:金額', '1:大分類', '2:小分類',
            '3:支払い方法',  '4:日付']
    
    def __init__(self, payment_list):
        """
        インスタンスの初期化を行う。
        """
        self.df = DataFrame(payment_list)
        super().__init__(payment_list)
        self.df.columns = self.COLS
        #self.pl = payment_list

    def __repr__(self):
        display(self.df)
        return ""


    '''
    def __getitem__(self, item):
        return self.pl[item]


    def __iter__(self):
        return iter(self.pl)
    '''


    def query(self, month=0, day=0,
              class1='', class2='', payment=''):
        """
        科目から検索を行う
        """
        result =  query(self, YEAR, month, day, 
                        incw=class1, incw2=class2, incw3=payment)
        if result:
            return CDataFrame(result)


    def describe(self):
        """
        概要を表示する
        """
        df = self.df
        income = sum(x for x in df[self.COLS[0]] if x > 0)
        payment = -sum(x for x in df[self.COLS[0]] if x < 0)
        inc_pm = income/12
        pay_pm = payment/12
        desc = DataFrame([[income, inc_pm, payment, pay_pm]],
                         dtype=int)
        desc.columns = ['収入', '平均月収', '支出', '平均月支出']
        return desc


    def pie_chart(self, category=0):
        """
        円グラフを描く
        """
        # Notebookに出力
        output_notebook()
        # 描画するデータ
        
        df = self.df
        x = Counter()
        
        idx = 1
        if category == 1:
            idx = 2
        for item in self.query():
            if item[0] < 0:
                x.update({item[idx]: -item[0]})

        if len(x) > 20:
            msg = ("カテゴリーが多すぎて表示できません。"
                   "データを絞り込んでみてください。")
            raise ValueError(msg)
        total = sum(x.values())
        
        items = list(x.items())
        items.sort(key=lambda x: x[1])
        items.reverse()
        x = {}
        for k, v in items:
            k = (k[:8] + '..') if len(k) > 8 else k
            x[k+'({}%)'.format(int(v/total*100))] = v
        
        data = DataFrame.from_dict(x, orient='index').reset_index()
        data = data.rename(index=str, columns={0:'value', 'index':'label'})
        data['angle'] = data['value']/sum(x.values()) * 2*pi
        data['color'] = Category20c[len(x)]
        
        p = figure(plot_height=350, title="円グラフ", toolbar_location=None,
                   tools="hover", tooltips=[("分類", "@label"),("値", "@value")])
        
        p.wedge(x=0, y=1, radius=0.4, 
                start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                line_color="white", fill_color='color', legend='label', source=data)
        
        p.axis.axis_label=None
        p.axis.visible=False
        p.grid.grid_line_color = None
        
        show(p)


    def sum(self):
        """
        金額の合計を計算して返す
        """
        return sum(x[0] for x in self)


# A,B,Cの履歴をそれぞれCDataFrameとして保持
# get_wallet()で返せるようにする

all_data = [CDataFrame(pl_a), CDataFrame(pl_b), CDataFrame(pl_c)]

def get_wallet(idx):
    """
    CDataFrameを取得する
    """
    if idx >= 0 and idx < len(all_data):
        return all_data[idx]
    raise IndexError("引数には0から2までを指定してください。")


def query(pl, year, month=0, day=0,
          incw='', justw='', incw2='', justw2='',
          incw3='', justw3=''):
    """
    履歴リストから，指定の年月日の履歴を取る
    dayが指定されていなかったら月のリスト全部
    incwが指定されていたらitem[1]を部分一致(優先)
    justwが指定されていたらitem[1]を完全一致
    どっちもなかったら全て
    """
    rl = []
    for item in pl:
        go = False
        if day:
            # 日付まで指定
            dts = '{0:04d}/{1:02d}/{2:02d}'.format(year, month, day)
            if item[4] == dts:
                go = True
        elif month:
            # 日付まで指定
            dts = '{0:04d}/{1:02d}/'.format(year, month)
            if dts in item[4]:
                go = True
        else:
            dts = '{0:04d}/'.format(year)
            if dts in item[4]:
                go = True

        if go:
            if incw:
                if incw in item[1]:
                    rl.append(item)
            elif justw:
                if justw == item[1]:
                    rl.append(item)
            elif incw2:
                if incw2 in item[2]:
                    rl.append(item)
            elif justw2:
                if justw2 == item[2]:
                    rl.append(item)
            elif incw3:
                if incw3 in item[3]:
                    rl.append(item)
            elif justw3:
                if justw3 == item[3]:
                    rl.append(item)
            else:
                rl.append(item)
    return rl


def bar_chart(a_list, line=None):
    """
    a_listを元に棒グラフを描く。
    lineに数値が与えられていたら，平行な線を描く
    """
    fig, ax = plt.subplots()
    ax.bar(range(len(a_list)), a_list)
    if line:
        ax.axhline(line)
