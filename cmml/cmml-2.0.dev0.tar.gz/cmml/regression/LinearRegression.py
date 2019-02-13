#!/usr/bin/python
# coding:utf8
'''
Created on Jan 8, 2011
Update  on 2017-05-18
Author: 曹明
GitHub: https://github.com/Mark
'''
#from cmml.data.LoadData import loadDataSet
from numpy import *
import matplotlib.pylab as plt
from time import sleep
import json
import urllib.request   # 在Python3中将urllib2和urllib3合并为一个标准库urllib,其中的urllib2.urlopen更改为urllib.request.urlopen


def standRegression(xtrain, ytrain):
    '''
    Description：
        线性回归
    Args:
        xArr ：输入的样本数据，包含每个样本数据的 feature
        yArr ：对应于输入数据的类别标签，也就是每个样本对应的目标变量
    Returns:
        ws：回归系数
    '''

    # mat()函数将xArr，yArr转换为矩阵 mat().T 代表的是对矩阵进行转置操作
    xMat = mat(xtrain)
    yMat = mat(ytrain).T
    # 矩阵乘法的条件是左矩阵的列数等于右矩阵的行数
    xTx = xMat.T * xMat
    # 因为要用到xTx的逆矩阵，所以事先需要确定计算得到的xTx是否可逆，条件是矩阵的行列式不为0
    # linalg.det() 函数是用来求得矩阵的行列式的，如果矩阵的行列式为0，则这个矩阵是不可逆的，就无法进行接下来的运算
    if linalg.det(xTx) == 0.0:
        print("This matrix is singular, cannot do inverse")
        return
    # 最小二乘法
    # http://www.apache.wiki/pages/viewpage.action?pageId=5505133
    # 书中的公式，求得w的最优解
    ws = xTx.I * (xMat.T * yMat)
    return ws

def standRegressionpredict(xtrain, ytrain,xtest):
    ws=standRegression(xtrain, ytrain)
    y=xtest*ws
    return y
'''
if __name__ == '__main__':
trainX,trainY = loadDataSet("C:\\abalone.txt")
print (trainX1)
y=predict(trainX,trainY,[1,1,2,5,4,6,7,1])
print (y)
''' 
