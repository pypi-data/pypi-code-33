#!/usr/bin/python
# coding:utf8
'''
Created on Jan 8, 2011
Update  on 2017-05-18
Author: Peter Harrington/小瑶
GitHub: https://github.com/apachecn/AiLearning
'''

from numpy import *
import matplotlib.pylab as plt
from time import sleep
import json
import urllib.request   # 在Python3中将urllib2和urllib3合并为一个标准库urllib,其中的urllib2.urlopen更改为urllib.request.urlopen

def loadDataSet(fileName):
    """ 加载数据
        解析以tab键分隔的文件中的浮点数
    Returns：
        dataMat ：  feature 对应的数据集
        labelMat ： feature 对应的分类标签，即类别标签
    """
    # 获取样本特征的总数，不算最后的目标变量
    numFeat = len(open(fileName).readline().split('\t')) - 1
    dataMat = []
    labelMat = []
    fr = open(fileName)
    for line in fr.readlines():
        # 读取每一行
        lineArr = []
        # 删除一行中以tab分隔的数据前后的空白符号
        curLine = line.strip().split('\t')
        # i 从0到2，不包括2
        for i in range(numFeat):
            # 将数据添加到lineArr List中，每一行数据测试数据组成一个行向量
            lineArr.append(float(curLine[i]))
            # 将测试数据的输入数据部分存储到dataMat 的List中
        dataMat.append(lineArr)
        # 将每一行的最后一个数据，即类别，或者叫目标变量存储到labelMat List中
        labelMat.append(float(curLine[-1]))
    return dataMat, labelMat
