from numpy import *
import numpy as np

def pdev(etha,namda,a):
    if linalg.norm(etha)<namda:
        return np.sign(etha)*namda/(a)
    else:
        return np.sign(etha)*(a*namda-linalg.norm(etha))

def D(b,namda,a,kes):
    return 1/2*pdev(b,namda,a)/(kes+b)

def scad(xArr, yArr,namda=1,a=2,kes=2):
    xMat = mat(xArr)
    yMat = mat(yArr).T
    # 矩阵乘法的条件是左矩阵的列数等于右矩阵的行数
    xTx = xMat.T * xMat
    m, n = np.shape(xMat)
    # 最大迭代次数，假装迭代这么多次就能收敛2333
    max_cycles = 500
    # 学习率，learning rate
    alpha = 0.001
    ws = np.ones((n, 1))
    for k in range(max_cycles):
        # 这里是点乘  m x 3 dot 3 x 1
        # 这里比较建议看一下推导，为什么这么做可以，这里已经是求导之后的
        ws = (xTx+1/2*n*D(ws,namda,a,kes)).I*(xMat.T * yMat)
    return ws


def scadTest(xArr, yArr):
    '''
        Desc：
            函数 ridgeTest() 用于在一组 λ 上测试结果
        Args：
            xArr：样本数据的特征，即 feature
            yArr：样本数据的类别标签，即真实数据
        Returns：
            wMat：将所有的回归系数输出到一个矩阵并返回
    '''

    xMat = mat(xArr)
    yMat = mat(yArr).T
    # 计算Y的均值
    yMean = mean(yMat, 0)
    # Y的所有的特征减去均值
    yMat = yMat - yMean
    # 标准化 x，计算 xMat 平均值
    xMeans = mean(xMat, 0)
    # 然后计算 X的方差
    xVar = var(xMat, 0)
    # 所有特征都减去各自的均值并除以方差
    xMat = (xMat - xMeans) / xVar
    # 可以在 30 个不同的 lambda 下调用 ridgeRegres() 函数。
    numTestPts = 30
    # 创建30 * m 的全部数据为0 的矩阵
    wMat = zeros((numTestPts, shape(xMat)[1]))
    for i in range(numTestPts):
        # exp() 返回 e^x
        ws=scad(xArr, yArr,namda=i,a=2,kes=2)
        #ws = ridgeRegres(xMat, yMat, exp(i - 10))
        wMat[i, :] = ws.T
    return wMat

def scadpredict(trainX,trainY,testX):
    wMat = scadTest(trainX,trainY)
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
