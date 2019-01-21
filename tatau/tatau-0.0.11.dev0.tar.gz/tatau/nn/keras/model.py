from abc import ABC
from collections import Iterable
from itertools import cycle

import keras
import numpy as np

from tatau.nn import tatau
from .progress import ProgressCallback


class Model(tatau.Model, ABC):
    weights_serializer_class = 'tatau.nn.keras.serializer.WeightsSerializer'
    weights_summarizer_class = 'tatau.nn.keras.summarizer.Median'

    def __init__(self, *args, **kwargs):
        super(Model, self).__init__(*args, **kwargs)
        self._callbacks = kwargs.get('callbacks', [])
        self.loader = None

    @property
    def optimizer(self):
        return self.native_model.optimizer

    @optimizer.setter
    def optimizer(self, value):
        self.native_model.optimizer = value

    @classmethod
    def native_model_factory(cls) -> keras.models.Model:
        """
        Construct Keras Model.

        """
        raise NotImplementedError()

    def get_weights(self):
        return self.native_model.get_weights()

    def set_weights(self, weights: list):
        self.native_model.set_weights(weights=weights)

    @property
    def callbacks(self):
        return self._callbacks

    @callbacks.setter
    def callbacks(self, value):
        self._callbacks = value

    def collate_function(self, batch):
        # replace torchvision ToTensor() function
        x = np.array([np.array(element[0], dtype=np.float32) / 255 for element in batch])
        y = np.array([element[1] for element in batch])

        return x, y

    def get_data_loader(self, chunk_dirs: Iterable, batch_size, transform, target_transform, **kwargs):
        from torch.utils.data import DataLoader
        from tatau.nn.torch.dataset import NumpyChunkedDataset

        loader = DataLoader(
            dataset=NumpyChunkedDataset(chunk_dirs=chunk_dirs,
                                        mmap_mode=None,
                                        transform=transform,
                                        target_transform=target_transform),
            batch_size=batch_size, shuffle=True, pin_memory=True, collate_fn=self.collate_function)

        return loader

    def _get_data_loader(self, chunk_dirs: Iterable, batch_size, **kwargs):
        self.loader = self.get_data_loader(chunk_dirs, batch_size, **kwargs)

        def generator(loader):
            for i, (x, y) in enumerate(loader):
                yield x, y

        return cycle(generator(self.loader))

    def train(self, chunk_dirs: Iterable, batch_size: int, current_iteration: int,
              nb_epochs: int, train_progress: tatau.TrainProgress):

        callbacks = [
            ProgressCallback(train_progress=train_progress)
        ]

        callbacks.extend(self.callbacks)

        history = self.native_model.fit_generator(
            generator=self._get_data_loader(chunk_dirs,
                                            batch_size,
                                            transform=self.transform_train,
                                            target_transform=self.transform_target),
            steps_per_epoch=len(self.loader),
            epochs=nb_epochs,
            shuffle=False,
            callbacks=callbacks
        )

        train_history = dict()

        for metric in history.history.keys():
            train_history[metric] = [float(val) for val in history.history[metric]]

        return train_history

    def eval(self, chunk_dirs: Iterable, batch_size: int):
        return self.native_model.evaluate_generator(
            generator=self._get_data_loader(chunk_dirs,
                                            batch_size,
                                            transform=self.transform_eval,
                                            target_transform=self.transform_target),
            steps=len(self.loader)
        )
