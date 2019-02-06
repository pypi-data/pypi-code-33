'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    \file train.py

    \brief Code to train a segmentation network on a dataset.

    \copyright Copyright (c) 2018 Visual Computing group of Ulm University,
                Germany. See the LICENSE file at the top-level directory of
                this distribution.

    \author pedro hermosilla (pedro-1.hermosilla-casajus@uni-ulm.de)
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

import sys
import math
import time
import argparse
import importlib
import os
import numpy as np
import tensorflow as tf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'models'))
sys.path.append(os.path.join(BASE_DIR, 'utils'))

from PyUtils import visualize_progress
from MCCNNDataSet import MCCNNDataSet

current_milli_time = lambda: time.time() * 1000.0


def create_loss(logits, labels, weigthDecay):
    labels = tf.to_int64(tf.reshape(labels, [-1]))
    cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(labels=labels, logits=logits, name='xentropy')
    xentropyloss = tf.reduce_mean(cross_entropy, name='xentropy_mean')
    regularizer = tf.contrib.layers.l2_regularizer(scale=weigthDecay)
    regVariables = tf.get_collection('weight_decay_loss')
    regTerm = tf.contrib.layers.apply_regularization(regularizer, regVariables)
    return xentropyloss, regTerm


def create_accuracy(logits, labels, scope):
    _, logitsIndexs = tf.nn.top_k(logits)
    with tf.variable_scope(scope):
        return tf.metrics.accuracy(labels, logitsIndexs)


def create_trainning(lossGraph, learningRate, maxLearningRate, learningDecayFactor, learningRateDecay, global_step):
    learningRateExp = tf.train.exponential_decay(learningRate, global_step, learningRateDecay, learningDecayFactor, staircase=True)
    learningRateExp = tf.maximum(learningRateExp, maxLearningRate)
    optimizer = tf.train.AdamOptimizer(learning_rate =learningRateExp)
    update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
    with tf.control_dependencies(update_ops):
        train_op = optimizer.minimize(lossGraph, global_step=global_step)
    return train_op, learningRateExp

def train_mccnn_seg(mccnn):

    data = mccnn.data
    logFolder = mccnn.logFolder
    model = mccnn.model
    grow = mccnn.grow
    batchSize = mccnn.batchSize
    maxEpoch = mccnn.maxEpoch
    initLearningRate = mccnn.initLearningRate
    learningDeacyFactor = mccnn.learningDeacyFactor
    learningDecayRate = mccnn.learningDecayRate
    maxLearningRate = mccnn.maxLearningRate
    useDropOut = mccnn.useDropOut
    dropOutKeepProb = mccnn.dropOutKeepProb
    useDropOutConv = mccnn.useDropOutConv
    dropOutKeepProbConv = mccnn.dropOutKeepProbConv
    weightDecay = mccnn.weightDecay
    ptDropOut = mccnn.ptDropOut
    augment = mccnn.augment
    nonunif = mccnn.nonunif
    gpu = mccnn.gpu
    gpuMem = mccnn.gpuMem

    #Create log folder.
    print (logFolder)
    if not os.path.exists(logFolder): os.mkdir(logFolder)
    os.system('cp %s/%s.py %s' % (os.path.join(BASE_DIR, 'models'), model, logFolder))
    os.system('cp %s/train.py %s' % (os.path.join(BASE_DIR), logFolder))
    logFile = logFolder+"/log.txt"

    data_arr = [df.values for df in data]
    data_arr = np.array(data_arr)

    #Write execution info.
    with open(logFile, "a") as myFile:
        myFile.write("Model: "+model+"\n")
        myFile.write("Grow: "+str(grow)+"\n")
        myFile.write("BatchSize: "+str(batchSize)+"\n")
        myFile.write("MaxEpoch: "+str(maxEpoch)+"\n")
        myFile.write("InitLearningRate: "+str(initLearningRate)+"\n")
        myFile.write("LearningDeacyFactor: "+str(learningDeacyFactor)+"\n")
        myFile.write("LearningDecayRate: "+str(learningDecayRate)+"\n")
        myFile.write("MaxLearningRate: "+str(maxLearningRate)+"\n")
        myFile.write("UseDropOut: "+str(useDropOut)+"\n")
        myFile.write("DropOutKeepProb: "+str(dropOutKeepProb)+"\n")
        myFile.write("UseDropOutConv: "+str(useDropOutConv)+"\n")
        myFile.write("DropOutKeepProbConv: "+str(dropOutKeepProbConv)+"\n")
        myFile.write("WeightDecay: "+str(weightDecay)+"\n")
        myFile.write("ptDropOut: "+str(ptDropOut)+"\n")
        myFile.write("Augment: "+str(augment)+"\n")
        myFile.write("Nonunif: "+str(nonunif)+"\n")

    print("Model: "+model)
    print("Grow: "+str(grow))
    print("BatchSize: "+str(batchSize))
    print("MaxEpoch: "+str(maxEpoch))
    print("InitLearningRate: "+str(initLearningRate))
    print("LearningDeacyFactor: "+str(learningDeacyFactor))
    print("LearningDecayRate: "+str(learningDecayRate))
    print("MaxLearningRate: "+str(maxLearningRate))
    print("UseDropOut: "+str(useDropOut))
    print("DropOutKeepProb: "+str(dropOutKeepProb))
    print("UseDropOutConv: "+str(useDropOutConv))
    print("DropOutKeepProbConv: "+str(dropOutKeepProbConv))
    print("WeightDecay: "+str(weightDecay))
    print("ptDropOut: "+str(ptDropOut))
    print("Augment: "+str(augment))
    print("Nonunif: "+str(nonunif))

    #Load the model
    model = importlib.import_module(model)

    #Get train and test files
    allowedSamplingsTrain=[]
    allowedSamplingsTest=[]
    if nonunif:
        allowedSamplingsTrain = [1, 2, 3, 4]
        allowedSamplingsTest = [0, 1, 2, 3, 4]
    else:
        allowedSamplingsTrain = [0]
        allowedSamplingsTest = [0]

    mTrainDataSet = MCCNNDataSet(data_arr, True, False, batchSize, ptDropOut,
        allowedSamplingsTrain, augment)
    mTestDataSet = MCCNNDataSet(data_arr, False, False, 1, 1.0,
        allowedSamplingsTest, False)

    numTrainModels = mTrainDataSet.get_num_models()
    numBatchesXEpoch = numTrainModels/batchSize
    if numTrainModels%batchSize != 0:
        numBatchesXEpoch = numBatchesXEpoch + 1
    numTestModels = mTestDataSet.get_num_models()

    cat = mTrainDataSet.get_categories()
    segClasses = mTrainDataSet.get_categories_seg_parts()
    print(segClasses)
    print("Train models: " + str(numTrainModels))
    print("Test models: " + str(numTestModels))

    #Create variable and place holders
    global_step = tf.Variable(0, name='global_step', trainable=False)
    inPts = tf.placeholder(tf.float32, [None, 3])
    inBatchIds = tf.placeholder(tf.int32, [None, 1])
    inFeatures = tf.placeholder(tf.float32, [None, 1])
    inCatLabels = tf.placeholder(tf.int32, [None, 1])
    inLabels = tf.placeholder(tf.int32, [None, 1])
    isTraining = tf.placeholder(tf.bool)
    keepProbConv = tf.placeholder(tf.float32)
    keepProbFull = tf.placeholder(tf.float32)
    iouVal = tf.placeholder(tf.float32)

    #Create the network
    logits = model.create_network(inPts, inBatchIds, inFeatures, inCatLabels, 1, len(cat), 50, batchSize,
        grow, isTraining, keepProbConv, keepProbFull, useDropOutConv, useDropOut)

    #Create predict labels
    predictedLabels = tf.argmax(logits, 1)

    #Create loss
    xentropyLoss, regularizationLoss = create_loss(logits, inLabels, weightDecay)
    loss = xentropyLoss + regularizationLoss

    #Create training
    trainning, learningRateExp = create_trainning(loss,
        initLearningRate, maxLearningRate, learningDeacyFactor,
        learningDecayRate*numBatchesXEpoch, global_step)
    learningRateSumm = tf.summary.scalar('learninRate', learningRateExp)

    #Create accuracy metric
    accuracyVal, accuracyAccumOp = create_accuracy(logits, inLabels, 'metrics')
    metricsVars = tf.contrib.framework.get_variables('metrics', collection=tf.GraphKeys.LOCAL_VARIABLES)
    resetMetrics = tf.variables_initializer(metricsVars)

    #Create sumaries
    lossSummary = tf.summary.scalar('loss', loss)
    xEntropyLossSummary = tf.summary.scalar('loss_XEntropy', xentropyLoss)
    regularizationLossSummary = tf.summary.scalar('loss_Regularization', regularizationLoss)
    trainingSummary = tf.summary.merge([lossSummary, xEntropyLossSummary, regularizationLossSummary, learningRateSumm])
    metricsSummary = tf.summary.scalar('accuracy', accuracyVal)
    metricsTestSummary = tf.summary.merge([tf.summary.scalar('Test_Accuracy', accuracyVal), tf.summary.scalar('Test_IoU', iouVal)], name='TestMetrics')

    #Create init variables
    init = tf.global_variables_initializer()
    initLocal = tf.local_variables_initializer()

    #create the saver
    saver = tf.train.Saver()

    #Create session
    gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=gpuMem, visible_device_list=gpu)
    sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))

    #Create the summary writer
    summary_writer = tf.summary.FileWriter(logFolder, sess.graph)
    summary_writer.add_graph(sess.graph)

    #Init variables
    sess.run(init)
    sess.run(initLocal)
    step = 0
    epochStep = 0
    np.random.seed(int(time.time()))

    best_acc = -1

    #Train
    for epoch in range(maxEpoch):

        startEpochTime = current_milli_time()
        startTrainTime = current_milli_time()

        epochStep = 0
        lossInfoCounter = 0
        lossAccumValue = 0.0

        sess.run(resetMetrics)

        #Iterate over all the train files
        mTrainDataSet.start_iteration()
        while mTrainDataSet.has_more_batches():

            _, points, batchIds, features, labels, catLabels, _ = mTrainDataSet.get_next_batch()

            _, lossRes, xentropyLossRes, regularizationLossRes, trainingSummRes, _ = \
                sess.run([trainning, loss, xentropyLoss, regularizationLoss, trainingSummary, accuracyAccumOp],
                {inPts: points, inBatchIds: batchIds, inFeatures: features, inCatLabels: catLabels, inLabels: labels,
                isTraining: True, keepProbConv: dropOutKeepProbConv, keepProbFull: dropOutKeepProb})


            summary_writer.add_summary(trainingSummRes, step)

            lossAccumValue += lossRes
            lossInfoCounter += 1

            if lossInfoCounter == 10:
                endTrainTime = current_milli_time()
                currAccuracy, metricsSummRes = sess.run([accuracyVal, metricsSummary])
                summary_writer.add_summary(metricsSummRes, step)

                visualize_progress(epochStep, numBatchesXEpoch, "Loss: %.6f | Accuracy: %.4f | Time: %.4f" % (
                    lossAccumValue/10.0, currAccuracy*100.0, (endTrainTime-startTrainTime)/1000.0))

                with open(logFile, "a") as myfile:
                    myfile.write("Step: %6d (%4d) | Loss: %.6f | Accuracy: %.4f\n" % (step, epochStep, lossAccumValue/10.0, currAccuracy*100.0))

                sess.run(resetMetrics)
                lossInfoCounter = 0
                lossAccumValue = 0.0
                startTrainTime = current_milli_time()

            step += 1
            epochStep += 1

        endEpochTime = current_milli_time()
        print("Epoch %3d  train time: %.4f" %(epoch, (endEpochTime-startEpochTime)/1000.0))
        with open(logFile, "a") as myfile:
            myfile.write("Epoch %3d  train time: %.4f \n" %(epoch, (endEpochTime-startEpochTime)/1000.0))

        if epoch%10==0:
            saver.save(sess, logFolder+"/model.ckpt")

        #Test data
        it = 0
        accumTestLoss = 0.0
        sess.run(resetMetrics)
        IoUxCat = [[] for i in range(len(cat))]
        mTestDataSet.start_iteration()
        while mTestDataSet.has_more_batches():

            _, points, batchIds, features, labels, catLabels, _ = mTestDataSet.get_next_batch()

            lossRes, predictedLabelsRes, _ = sess.run([loss, predictedLabels, accuracyAccumOp],
                    {inPts: points, inBatchIds: batchIds, inFeatures: features, inCatLabels: catLabels,
                    inLabels: labels, isTraining: False, keepProbConv: 1.0, keepProbFull: 1.0})

            accumTestLoss = accumTestLoss + lossRes

            #Compute IoU
            numParts = len(segClasses)
            accumIoU = 0.0
            for j in range(numParts):
                intersection = 0.0
                union = 0.0
                currLabel = segClasses[j]
                for k in range(len(labels)):
                    if labels[k] == predictedLabelsRes[k] and labels[k] == currLabel:
                        intersection = intersection + 1.0
                    if labels[k] == currLabel or predictedLabelsRes[k] == currLabel:
                        union = union + 1.0
                if union > 0.0:
                    accumIoU = accumIoU + intersection/union
                else:
                    accumIoU = accumIoU + 1.0
            accumIoU = accumIoU/float(numParts)
            IoUxCat[catLabels[0][0]].append(accumIoU)

            if it%100 == 0:
                visualize_progress(it, numTestModels)

            it += 1

        #Compute mean IoU
        meanIoUxCat = 0.0
        for i in range(len(IoUxCat)):
            if len(IoUxCat[i]) > 0:
                currMean = 0.0
                for currVal in IoUxCat[i]:
                    currMean = currMean + currVal
                currMean = currMean / float(len(IoUxCat[i]))
                print("Mean IoU category "+cat[i][0]+": "+str(currMean))
                meanIoUxCat = meanIoUxCat + currMean*float(len(IoUxCat[i]))
        meanIoUxCat = meanIoUxCat / float(numTestModels)

        totalAccuracy, metricsTestSummRes = sess.run([accuracyVal, metricsTestSummary], {iouVal: meanIoUxCat})
        accumTestLoss = accumTestLoss/float(numTestModels)
        summary_writer.add_summary(metricsTestSummRes, step)

        if totalAccuracy > best_acc:
            best_acc = totalAccuracy
            os.system('rm %s/best_model*' %logFolder)
            saver.save(sess, logFolder+"/best_model_epoch_%03d.ckpt"%(epoch))


        print("Loss: %.6f | Test accuracy: %.4f | Test IoU %.4f" % (accumTestLoss, totalAccuracy*100.0, meanIoUxCat*100.0))
        with open(logFile, "a") as myfile:
            myfile.write("Loss: %.6f | Test accuracy: %.4f | Test IoU %.4f\n" % (accumTestLoss, totalAccuracy*100.0, meanIoUxCat*100.0))
