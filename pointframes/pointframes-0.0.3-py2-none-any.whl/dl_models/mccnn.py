import pointframes as pf

class MCCNN(object):

    def __init__(self):

        # Deafults from original implementation
        self._data = None
        self._num_points = 4096
        self._logFolder = './logs'
        self._model = 'MCSeg'
        self._grow = 32
        self._batchSize = 1
        self._maxEpoch = 500
        self._initLearningRate = 0.005
        self._learningDeacyFactor = 0.2
        self._learningDecayRate = 15
        self._maxLearningRate = 0.00001
        self._useDropOut = True
        self._dropOutKeepProb = 0.5
        self._useDropOutConv = False
        self._dropOutKeepProbConv = 0.8
        self._weightDecay = 0.0
        self._ptDropOut = 0.8
        self._augment = False
        self._nonunif = False
        self._maxNumPts = 600000
        self._gpu = '0'
        self._gpuMem = 0.5
        self._trainedModel = None
        self._nExec = 1
        self.numClasses = 0

    @property
    def data(self):
        return self._data
    @data.setter
    def data(self, data):
        self._data = data

    @property
    def num_points(self):
        return self._num_points
    @num_points.setter
    def num_points(self, num_points):
        self._num_points = num_points

    @property
    def logFolder(self):
        return self._logFolder
    @logFolder.setter
    def logFolder(self, logFolder):
        self._logFolder = logFolder

    @property
    def model(self):
        return self._model
    @model.setter
    def model(self, model):
        self._model = model

    @property
    def grow(self):
        return self._grow
    @grow.setter
    def grow(self, grow):
        self._grow = grow

    @property
    def batchSize(self):
        return self._batchSize
    @batchSize.setter
    def batchSize(self, batchSize):
        self._batchSize = batchSize

    @property
    def maxEpoch(self):
        return self._maxEpoch
    @maxEpoch.setter
    def maxEpoch(self, maxEpoch):
        self._maxEpoch = maxEpoch

    @property
    def initLearningRate(self):
        return self._initLearningRate
    @initLearningRate.setter
    def initLearningRate(self, initLearningRate):
        self._initLearningRate = initLearningRate

    @property
    def learningDeacyFactor(self):
        return self._learningDeacyFactor
    @learningDeacyFactor.setter
    def learningDeacyFactor(self, learningDeacyFactor):
        self._learningDeacyFactor = learningDeacyFactor

    @property
    def learningDecayRate(self):
        return self._learningDecayRate
    @learningDecayRate.setter
    def learningDecayRate(self, learningDecayRate):
        self._learningDecayRate = learningDecayRate

    @property
    def maxLearningRate(self):
        return self._maxLearningRate
    @maxLearningRate.setter
    def maxLearningRate(self, maxLearningRate):
        self._maxLearningRate = maxLearningRate

    @property
    def useDropOut(self):
        return self._useDropOut
    @useDropOut.setter
    def useDropOut(self, useDropOut):
        self._useDropOut = useDropOut

    @property
    def dropOutKeepProb(self):
        return self._dropOutKeepProb
    @dropOutKeepProb.setter
    def dropOutKeepProb(self, dropOutKeepProb):
        self._dropOutKeepProb = dropOutKeepProb

    @property
    def useDropOutConv(self):
        return self._useDropOutConv
    @useDropOutConv.setter
    def useDropOutConv(self, useDropOutConv):
        self._useDropOutConv = useDropOutConv

    @property
    def dropOutKeepProbConv(self):
        return self._dropOutKeepProbConv
    @dropOutKeepProbConv.setter
    def dropOutKeepProbConv(self, dropOutKeepProbConv):
        self._dropOutKeepProbConv = dropOutKeepProbConv

    @property
    def weightDecay(self):
        return self._weightDecay
    @weightDecay.setter
    def weightDecay(self, weightDecay):
        self._weightDecay = weightDecay

    @property
    def ptDropOut(self):
        return self._ptDropOut
    @ptDropOut.setter
    def ptDropOut(self, ptDropOut):
        self._ptDropOut = ptDropOut

    @property
    def augment(self):
        return self._augment
    @augment.setter
    def augment(self, augment):
        self._augment = augment

    @property
    def nonunif(self):
        return self._nonunif
    @nonunif.setter
    def nonunif(self, nonunif):
        self._nonunif = nonunif

    @property
    def maxNumPts(self):
        return self._maxNumPts
    @maxNumPts.setter
    def maxNumPts(self, maxNumPts):
        self._maxNumPts = maxNumPts

    @property
    def gpu(self):
        return self._gpu
    @gpu.setter
    def gpu(self, gpu):
        self._gpu = gpu

    @property
    def gpuMem(self):
        return self._gpuMem
    @gpuMem.setter
    def gpuMem(self, gpuMem):
        self._gpuMem = gpuMem

    @property
    def trainedModel(self):
        return self._trainedModel
    @trainedModel.setter
    def trainedModel(self, trainedModel):
        self._trainedModel = trainedModel

    @property
    def nExec(self):
        return self._nExec
    @nExec.setter
    def nExec(self, nExec):
        self._nExec = nExec

    @property
    def numClasses(self):
        return self._numClasses
    @numClasses.setter
    def numClasses(self, numClasses):
        self._numClasses = numClasses

    def train(self):
        assert self._data is not None, 'You must set the training data before running.'
        if self._model == 'MCSeg':
            pf.train_mccnn_seg(self)
        elif self._model == 'MCSegScanNet':
            pf.train_mccnn_scannet(self)
        else:
            raise ValueError("Model must be either MCSeg or MCSegScanNet.")

    def inference(self):
        assert self._data is not None, 'You must set the inference data before running.'

        if self._model == 'MCSeg':
            labels = pf.mccnn_inference_seg(self)
        elif self._model == 'MCSegScanNet':
            labels = pf.mccnn_inference_scannet(self)
        else:
            raise ValueError("Model must be either MCSeg or MCSegScanNet.")
        return labels
