import pointframes as pf
import numpy as np
from DataSet import DataSet

class MCCNNDataSet(DataSet):

    def __init__(self, data, train, inference, batchSize, ptDropOut, allowedSamplings=[0], augment=False, useNormalsAsFeatures=False, seed=None):

        self._inference = inference

        if train == True:
            self._data = data
        else:
            trainTestSplit = 0.2
            choice = np.random.randint(0, len(data), int(len(data)*trainTestSplit))
            self._data = data[choice]

        if inference == True:
            self._data = data

        self.useNormalsAsFeatures_ = useNormalsAsFeatures

        augmentedFeatures = []
        if useNormalsAsFeatures:
            augmentedFeatures = [0]

        super(MCCNNDataSet,self).__init__(0, ptDropOut, useNormalsAsFeatures, True, True,
            True, True, batchSize, allowedSamplings, 100000000, 0,
            augment, 1, True, False, augmentedFeatures, [], seed)

        # We want to load from a numpy array, so set the fileList
        # as the array index.
        # TODO: Add ability to load from disk for very large point clouds
        self.fileList_ = [i for i in range(0, len(self._data))]

        # Give category names as index as this is all handled by PointFrames

        unique = [arr[:, 6] for arr in self._data]
        unique_ = np.unique(np.array(unique))

        self.catNames_ = [str(u) for u in unique_]
        self.segClasses_ = unique_
        self.categories_ = [len(np.unique(u)) for u in unique]
        self.numPts_ = [0 for i in range(len(self.fileList_))]

    def get_categories(self):
        return self.catNames_


    def get_categories_seg_parts(self):
        return self.segClasses_


    def _load_model_from_disk_(self, model_idx):

        pts_idx = [0, 1, 2]
        pts = self._data[model_idx][:, pts_idx]
        #centroid = np.mean(pts, axis=0)
        #pts = pts-centroid

        if self._inference == False:
            labels_idx = [6]
            labels = self._data[model_idx][:, labels_idx]
        else:
            labels = np.zeros((self._data.shape[1], 1))

        # Return None for normals and features for now.
        return pts, None, None, labels
