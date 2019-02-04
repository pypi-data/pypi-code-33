import pointframes as pf

class PointNet(object):

    def __init__(self):

        # Deafults from original implementation
        self._batch_size = 8
        self._num_points = 4096
        self._max_epoch = 100
        self._learning_rate = 0.001
        self._gpu = 0
        self._momentum = 0.9
        self._optimizer = 'adam'
        self._decay_step = 200000
        self._decay_rate = 0.5
        self._train_data = None
        self._model = 'pointnet_model'
        self._log_dir = None

    @property
    def batch_size(self):
        return self._batch_size
    @batch_size.setter
    def batch_size(self, batch_size):
        self._batch_size = batch_size

    @property
    def num_points(self):
        return self._num_points
    @num_points.setter
    def num_points(self, num_points):
        self._num_points = num_points

    @property
    def max_epoch(self):
        return self._max_epoch
    @max_epoch.setter
    def max_epoch(self, _max_epoch):
        self._max_epoch = _max_epoch

    @property
    def learning_rate(self):
        return self._learning_rate
    @learning_rate.setter
    def learning_rate(self, learning_rate):
        self._learning_rate = learning_rate

    @property
    def gpu(self):
        return self._gpu
    @gpu.setter
    def gpu(self, gpu):
        self._gpu = gpu

    @property
    def momentum(self):
        return self._momentum
    @momentum.setter
    def momentum(self, momentum):
        self._momentum = momentum

    @property
    def optimizer(self):
        return self._optimizer
    @optimizer.setter
    def optimizer(self, optimizer):
        self._optimizer = optimizer

    @property
    def decay_step(self):
        return self._decay_step
    @decay_step.setter
    def decay_step(self, decay_step):
        self._decay_step = decay_step

    @property
    def decay_rate(self):
        return self._decay_rate
    @decay_rate.setter
    def decay_rate(self, decay_rate):
        self._decay_rate = decay_rate

    @property
    def train_data(self):
        return self._train_data
    @train_data.setter
    def train_data(self, data):
        self._train_data = data

    @property
    def log_dir(self):
        return self._log_dir
    @log_dir.setter
    def log_dir(self, log_dir):
        self._log_dir = log_dir

    @property
    def model(self):
        return self._model
    @model.setter
    def model(self, model):
        self._model = model

    def train(self):
        pf.dl_models.train_pointnet(self)

    def predict(self):
        inference_array = pf.dl_models.pointnet_prediction(self)
        return inference_array

class PointNet_Data():
    ''' PointNet training data class.
        Contains all variables to train an instance
        of PointNet defined in this file.
    '''

    def __init__(self):

        self._train_data = None
        self._test_data = None
        self._train_labels = None
        self._test_labels = None
        self._num_classes = None

    @property
    def train_data(self):
        return self._train_data
    @train_data.setter
    def train_data(self, train_data):
        self._train_data = train_data

    @property
    def test_data(self):
        return self._test_data
    @test_data.setter
    def test_data(self, test_data):
        self._test_data = test_data

    @property
    def train_labels(self):
        return self._train_labels
    @train_labels.setter
    def train_labels(self, train_labels):
        self._train_labels = train_labels

    @property
    def test_labels(self):
        return self._test_labels
    @test_labels.setter
    def test_labels(self, test_labels):
        self._test_labels = test_labels

class PointNet_Predict(object):

    def __init__(self):

        self._eval_data = None
        self._model = None

    @property
    def eval_data(self):
        return self._eval_data
    @eval_data.setter
    def eval_data(self, eval_data):
        self._eval_data = eval_data
