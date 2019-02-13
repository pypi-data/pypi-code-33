from numpy import *
from cmml.error.rsserror import rssError


def stageWise(xArr, yArr, eps=0.01, numIt=100):
    xMat = mat(xArr)
    yMat = mat(yArr).T
    yMean = mean(yMat, 0)
    yMat = yMat - yMean  # 也可以规则化ys但会得到更小的coef
    #xMat = regularize(xMat)
    m, n = shape(xMat)
    returnMat = zeros((numIt, n))  # 测试代码删除
    ws = zeros((n, 1))
    wsTest = ws.copy()
    wsMax = ws.copy()
    for i in range(numIt):
        #print(ws.T)
        lowestError = inf
        for j in range(n):
            for sign in [-1, 1]:
                wsTest = ws.copy()
                wsTest[j] += eps * sign
                yTest = xMat * wsTest
                rssE = rssError(yMat.A, yTest.A)
                if rssE < lowestError:
                    lowestError = rssE
                    wsMax = wsTest
        ws = wsMax.copy()
        returnMat[i, :] = ws.T
    return returnMat


def stageWisepredict(trainX,trainY,testX):
    wMat = stageWise(trainX,trainY)
    #print (wMat)
    #matTestX=testX
    for k in range(30):
            # 读取训练集和数据集
            matTestX = mat(testX); matTrainX=mat(trainX)
            # 对数据进行标准化
            meanTrain = mean(matTrainX,0)
            varTrain = var(matTrainX,0)
            matTestX = (matTestX-meanTrain)/varTrain
            # 测试回归效果并存储
            yEst = matTestX * mat(wMat[k,:]).T + mean(trainY)
    #print (yEst)
    return yEst
