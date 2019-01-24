import tensorflow as tf
from .dataset import Dataset
from .batch_iterators import MemoryXYIter


class KerasDataset(Dataset):
    def __init__(self, keras_dataset, class_num, min_a=0., max_a=1., shape=None, categorical=True, raw=False):
        self.keras_dataset = keras_dataset
        datas = self.keras_dataset.load_data()

        if not raw:
            datas = self.preprocess(datas, class_num=class_num,
                                    min_from=0, max_from=255,
                                    min_to=min_a, max_to=max_a,
                                    shape=shape, categorical=categorical)

        (self.x_train, self.y_train), (self.x_test, self.y_test) = datas

    def train_batch(self, batch_size):
        return MemoryXYIter(self.x_train, self.y_train, batch_size)

    def test_batch(self, batch_size):
        return MemoryXYIter(self.x_test, self.y_test, batch_size)


class Datasets:
    @staticmethod
    def mnist(min_a=0., max_a=1., shape=None, categorical=True, raw=False):
        mnist = tf.keras.datasets.mnist
        datasets = mnist.load_data()

        if raw:
            return datasets
        else:
            return Dataset.preprocess(datasets, class_num=10,
                                      min_from=0, max_from=255,
                                      min_to=min_a, max_to=max_a,
                                      shape=shape, categorical=categorical)

    @staticmethod
    def cifar10(min_a=0., max_a=1., shape=None, categorical=True, raw=False):
        cifar10 = tf.keras.datasets.cifar10
        datasets = cifar10.load_data()

        if raw:
            return datasets
        else:
            return Dataset.preprocess(datasets, class_num=10,
                                      min_from=0, max_from=255,
                                      min_to=min_a, max_to=max_a,
                                      shape=shape, categorical=categorical)

    @staticmethod
    def cifar100(min_a=0., max_a=1., shape=None, categorical=True, raw=False):
        cifar100 = tf.keras.datasets.cifar100
        datasets = cifar100.load_data()

        if raw:
            return datasets
        else:
            return Dataset.preprocess(datasets, class_num=100,
                                      min_from=0, max_from=255,
                                      min_to=min_a, max_to=max_a,
                                      shape=shape, categorical=categorical)

    def get_mnist(self, min_a=0., max_a=1., shape=None, categorical=True):
        return self.mnist(min_a, max_a, shape, categorical)

    def get_cifar10(self, min_a=0., max_a=1., shape=None, categorical=True):
        return self.cifar10(min_a, max_a, shape, categorical)


class MNIST(KerasDataset):
    def __init__(self, min_a=0., max_a=1., shape=None, categorical=True, raw=False):
        super().__init__(tf.keras.datasets.mnist, class_num=10,
                         min_a=min_a, max_a=max_a, shape=shape, categorical=categorical, raw=raw)


class CIFAR10(KerasDataset):
    def __init__(self, min_a=0., max_a=1., shape=None, categorical=True, raw=False):
        super().__init__(tf.keras.datasets.cifar10, class_num=10,
                         min_a=min_a, max_a=max_a, shape=shape, categorical=categorical, raw=raw)


class CIFAR100(KerasDataset):
    def __init__(self, min_a=0., max_a=1., shape=None, categorical=True, raw=False):
        super().__init__(tf.keras.datasets.cifar100, class_num=100,
                         min_a=min_a, max_a=max_a, shape=shape, categorical=categorical, raw=raw)
