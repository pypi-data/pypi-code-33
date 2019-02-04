'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    \file inference.py

    \brief Code to evaluate a segmentation network on the ShapeNet dataset.

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
import progressbar

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'models'))
sys.path.append(os.path.join(BASE_DIR, 'utils'))

from PyUtils import visualize_progress, save_model
from MCCNNDataSet import MCCNNDataSet

current_milli_time = lambda: time.time() * 1000.0


def create_accuracy(logits, labels, scope):
    _, logitsIndexs = tf.nn.top_k(logits)
    with tf.variable_scope(scope):
        return tf.metrics.accuracy(labels, logitsIndexs)


def mccnn_inference_seg(mccnn):

    data = mccnn.data
    grow = mccnn.grow
    inTrainedModel = mccnn.trainedModel
    model = mccnn.model
    gpu = mccnn.gpu
    gpuMem = mccnn.gpuMem
    nExec = mccnn.nExec
    numClasses = mccnn.numClasses

    data_arr = [df.values for df in data]
    data_arr = np.array(data_arr)

    print("Trained model: "+inTrainedModel)
    print("Model: "+model)
    print("Grow: "+str(grow))
    print("nExec: "+str(nExec))

    #Colors asigned to each part (used to save the model as a file).
    colors = [  [228,26,28],
                [55,126,184],
                [77,175,74],
                [152,78,163],
                [255,127,0],
                [255,255,51]]

    #Load the model
    model = importlib.import_module(model)

    #Get train and test files
    mTestDataSet = MCCNNDataSet(data_arr, False, True, nExec, 1.0, [0], False)
    cat = mTestDataSet.get_categories()
    segClasses = mTestDataSet.get_categories_seg_parts()
    print(segClasses)
    numTestModels = mTestDataSet.get_num_models()
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

    #Create the network
    logits = model.create_network(inPts, inBatchIds, inFeatures, inCatLabels, 1, numClasses, 50,
        nExec, grow, isTraining, keepProbConv, keepProbFull, False, False)

    #Create predict labels
    predictedLabels = tf.argmax(logits, 1)

    #Create accuracy metric
    accuracyVal, accuracyAccumOp = create_accuracy(logits, inLabels, 'metrics')
    metricsVars = tf.contrib.framework.get_variables('metrics', collection=tf.GraphKeys.LOCAL_VARIABLES)
    resetMetrics = tf.variables_initializer(metricsVars)

    #Create init variables
    init = tf.global_variables_initializer()
    initLocal = tf.local_variables_initializer()

    #create the saver
    saver = tf.train.Saver()

    #Create session
    gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=gpuMem, visible_device_list=gpu)
    sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))

    #Init variables
    sess.run(init)
    sess.run(initLocal)

    #Restore the model
    saver.restore(sess, inTrainedModel)

    #Test the dataset.
    samplingTests = [
        "Uniform sampling",
        "Non-uniform split",
        "Non-uniform gradient",
        "Non-uniform lambert",
        "Non-uniform occlusion"]
    #Update the dataset.
    allowedSamplingsTest = [0]
    mTestDataSet.set_allowed_samplings(allowedSamplingsTest)
    mTestDataSet.start_iteration()

    bar = progressbar.ProgressBar(maxval=numTestModels, \
    widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    #Create the auxiliar variables.
    it = 0
    accumTime = 0.0
    step = 0
    epochStep = 0
    maxIoU = 0.0
    IoUxCat = [[] for i in range(len(cat))]
    #Iterate over the models.
    firstBatch = True
    while mTestDataSet.has_more_batches():

        bar.update(it+1)

        #Get the batch dataset.
        _, points, batchIds, features, labels, catLabels, modelsPath = mTestDataSet.get_next_batch(True)

        #Compute the predicted logits.
        startTimeMeasure = current_milli_time()
        predictedLabelsRes, _ = sess.run([predictedLabels, accuracyAccumOp],
                {inPts: points, inBatchIds: batchIds, inFeatures: features, inCatLabels: catLabels,
                inLabels: labels, isTraining: False, keepProbConv: 1.0, keepProbFull: 1.0})
        endTimeMeasure = current_milli_time()
        accumTime = accumTime + (endTimeMeasure - startTimeMeasure)

        if firstBatch == True:
            firstBatch = False
            pointsArr = points
            labelsArr = predictedLabelsRes
        else:
            pointsArr = np.vstack((pointsArr, points))
            labelsArr = np.vstack((labelsArr, predictedLabelsRes))

        #Save models
        """
        if saveModels:
            save_model("savedModels/"+modelsPath[0].replace("/", "-")+"_sampling_"+
                str(samp)+"_gt", points, labels, colors, 6)
            save_model("savedModels/"+modelsPath[0].replace("/", "-")+"_sampling_"+
                str(samp)+"_pred", points, predictedLabelsRes.reshape((-1,1)),
                colors, 6)
        """
        it += 1
    bar.finish()

    return np.hstack((pointsArr, labelsArr.reshape(-1, 1)))
