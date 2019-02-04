import pointframes as pf
import numpy as np
from DataSet import DataSet

class MCCNNDataSet(DataSet):

    def __init__(self, data, train, inference, batchSize, ptDropOut, maxNumPtsxBatch=600000,
                    augment=False, useColorsAsFeatures=False, dataFolder="data_mccnn", seed=None):

        self._inference = inference

        if train == True:
            self._data = data
        else:
            trainTestSplit = 0.2
            choice = np.random.randint(0, len(data), int(len(data)*trainTestSplit))
            self._data = data[choice]

        if inference == True:
            self._data = data

        self.useColorsAsFeatures_ = useColorsAsFeatures

        super(MCCNNDataSet,self).__init__(0, ptDropOut,
            useColorsAsFeatures, True, False,
            False, False, batchSize, [0], 0, maxNumPtsxBatch,
            augment, 2, False, False, [], [], seed)

        # We want to load from a numpy array, so set the fileList
        # as the array index.
        # TODO: Add ability to load from disk for very large point clouds
        self.fileList_ = [i for i in range(0, len(self._data))]

        # Give category names as index as this is all handled by PointFrames
        unique = [arr[:, 6] for arr in self._data]
        unique_ = np.unique(np.array(unique))

        self.semLabels_ = [str(u) for u in unique_]
        self.numPts_ = [0 for i in range(len(self.fileList_))]
        self.weights_ = [np.ones(np.array(self.semLabels_).astype(np.float32).shape)]


    def get_weights(self, labels):

        if len(self.weights_) == 0:
            raise RuntimeError('No weights associated to the labels.')

        #outWeights = np.array([[self.weights_[currLab[0]]] for currLab in labels])
        #return outWeights
        return np.ones((labels.shape), dtype=np.float32)

    def get_labels(self):
        return self.semLabels_


    def get_accuracy_masks(self, labels):
        """Method to get the list of mask for each label to compute the accuracy.

        Args:
            labels (np.array): Labels for which we want the weights.
        Returns:
            masks (np.array): List of mask for each label to compute
                the accuracy.
        """
        outMasks = np.array([[1.0] if lab[0] != 0 else [1.0] for lab in labels])
        return outMasks


    def _load_model_from_disk_(self, model_idx):

        pts_idx = [0, 1, 2]
        pts = self._data[model_idx][:, pts_idx]
        centroid = np.mean(pts, axis=0)
        pts = pts - centroid

        if self._inference == False:
            labels_idx = [6]
            labels = self._data[model_idx][:, labels_idx]
        else:
            labels = np.zeros((self._data.shape[1], 1))

        # Return None for normals and features for now.
        return pts, None, None, labels.reshape((-1, 1))
