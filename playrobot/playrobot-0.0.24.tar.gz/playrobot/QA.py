import jieba
import re
import wikipedia
import twstock
import os
from playrobot import QA

path = os.path.dirname(os.path.abspath(QA.__file__))
jieba.set_dictionary(path + '/dict.txt')

class wikiQA():
    
    def __init__(self,target):
        self.target = target
        self.head = ''
        wikipedia.set_lang("zh-tw")
    
    def headFinding(self):
        words = jieba.lcut(self.target)
        for word in words:
            if(word != u'是' and word != u'在'):
                self.head += word
            else:
                break
            
    def result(self):
        self.headFinding()
        message = wikipedia.summary(self.head,sentences=1)
        message2 = re.sub(u'[a-zA-Z(),（）「」]','',message)
        print(message)
        return message2
    
class stockQA():
    
    def __init__(self,target):
        self.target = target
        self.head = ''
        from playrobot import QA
        path = os.path.dirname(os.path.abspath(QA.__file__))
        with open(path + '/twcode.txt', encoding = 'utf-8-sig') as f:
            self.twlist = f.read()
            self.twlist = self.twlist.split(u'\n')
        self.tarName = ''
        self.tarNumber = ''
                
    def headFinding(self):
        text_temp = self.target[2:]
        print(text_temp)
        for i in self.twlist:
            temp = i.split(u'\t')
            if(text_temp == temp[0] or text_temp == temp[1]):
                self.tarNumber = temp[0]
                self.tarName = temp[1]
                break
            
    def result(self):
        self.headFinding()
        print(self.tarNumber)
        if(self.tarNumber != ''):
            temp = twstock.realtime.get(self.tarNumber)
            message = '股票名稱：' + self.tarName\
            + '、最新成交價：' + temp['realtime']['latest_trade_price'] + \
            '、開盤價：' + temp['realtime']['open'] +\
            '、高點：' + temp['realtime']['high'] +\
            '、低點：' + temp['realtime']['low']
        else:
            message = '此股票名稱或號碼不在台股上市列表喔'
        return message
