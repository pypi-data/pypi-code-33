from numpy import *
from cmml.regression.ridgeRegression import ridgeTest
from cmml.error.rsserror import rssError

def crossValidation(xArr,yArr,numVal=10):
    m = len(yArr)                           
    indexList = arange(m)
    errorMat = zeros((numVal,30))#create error mat 30columns numVal rows创建error mat 30columns numVal 行
    for i in arange(numVal):
        trainX=[]; trainY=[]
        testX = []; testY = []
        random.shuffle(indexList)
        for j in arange(m):#create training set based on first 90% of values in indexList
                          #基于indexList中的前90%的值创建训练集
            if j < m*0.9: 
                trainX.append(xArr[indexList[j]])
                trainY.append(yArr[indexList[j]])
            else:
                testX.append(xArr[indexList[j]])
                testY.append(yArr[indexList[j]])
        wMat = ridgeTest(trainX,trainY)    #get 30 weight vectors from ridge
        for k in arange(30):#loop over all of the ridge estimates
            matTestX = mat(testX); matTrainX=mat(trainX)
            meanTrain = mean(matTrainX,0)
            varTrain = var(matTrainX,0)
            matTestX = (matTestX-meanTrain)/varTrain #regularize test with training params
            yEst = matTestX * mat(wMat[k,:]).T + mean(trainY)#test ridge results and store
            errorMat[i,k]=rssError(yEst.T.A,array(testY))
            #print (errorMat[i,k])
    meanErrors = mean(errorMat,0)#calc avg performance of the different ridge weight vectors  一个模型的平均误差
    '''
    print (meanErrors)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(meanErrors)
    '''
    minMean = float(min(meanErrors))  #最小的一个模型的误差
    bestWeights = wMat[nonzero(meanErrors==minMean)]   #误差最小的模型的权重
    #can unregularize to get model
    #when we regularized we wrote Xreg = (x-meanX)/var(x)
    #we can now write in terms of x not Xreg:  x*w/var(x) - meanX/var(x) +meanY
    xMat = mat(xArr); yMat=mat(yArr).T
    meanX = mean(xMat,0); varX = var(xMat,0)
    unReg = bestWeights/varX
    print ("the best model from Ridge Regression is:\n",unReg)
    print ("with constant term: ",-1*sum(multiply(meanX,unReg)) + mean(yMat))
