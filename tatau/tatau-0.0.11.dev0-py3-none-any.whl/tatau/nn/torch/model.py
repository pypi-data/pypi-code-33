import time
from abc import ABCMeta
from collections import Iterable
from logging import getLogger

import torch
# noinspection PyUnresolvedReferences
# pylint: disable=E0611
from torch import cuda, from_numpy
from torch.nn import DataParallel

from tatau.nn.tatau import model, TrainProgress
from .dataset import NumpyChunkedDataset, AutoDataLoader

logger = getLogger(__name__)


class Model(model.Model, metaclass=ABCMeta):
    weights_serializer_class = 'tatau.nn.torch.serializer.WeightsSerializer'
    weights_summarizer_class = 'tatau.nn.torch.summarizer.Mean'

    def __init__(self, optimizer_class, optimizer_kwargs, criterion, is_fp16=False):
        super(Model, self).__init__()

        self._optimizer_kwargs = optimizer_kwargs

        self._device = 'cuda' if torch.cuda.is_available() else 'cpu'

        logger.info('Model device: {}'.format(self.device))

        self._model = self.native_model_factory()

        self._is_fp16 = is_fp16
        if self._is_fp16:
            # Lazy load apex framework
            # noinspection PyUnresolvedReferences
            from apex.fp16_utils import network_to_half, FP16_Optimizer
            self._model = network_to_half(self._model)

        self._gpu_count = torch.cuda.device_count() if torch.cuda.is_available() else 0

        logger.info("GPU count: {}".format(self._gpu_count))

        self._model = DataParallel(self._model)

        self._model = self._model.to(self.device)

        self._criterion = criterion.to(self.device)

        self._optimizer = optimizer_class(self._model.parameters(), **optimizer_kwargs)

        if self._is_fp16:
            self._optimizer = FP16_Optimizer(self._optimizer)

    def get_data_loader(self, chunk_dirs: Iterable, batch_size, transform, target_transform, **kwargs):
        return AutoDataLoader(
            dataset=NumpyChunkedDataset(chunk_dirs=chunk_dirs,
                                        transform=transform,
                                        mmap_mode=None,
                                        target_transform=target_transform),
            batch_size=batch_size, shuffle=True, pin_memory=True)

    @property
    def device(self):
        return self._device

    @property
    def criterion(self):
        return self._criterion

    @classmethod
    def native_model_factory(cls):
        raise NotImplementedError()

    def adjust_learning_rate(self, epoch):
        pass

    def get_weights(self):
        state = {
            'weights': self.native_model.state_dict(),
            'optimizer': self.optimizer.state_dict(),
            # 'criterion': self._criterion.state_dict()
        }
        return state

    def set_weights(self, weights: dict):
        self.native_model.load_state_dict(weights['weights'])
        self.optimizer.load_state_dict(weights['optimizer'])
        # self._criterion.load_state_dict(weights['criterion'])

    def optimizer_step(self, loss):
        self.optimizer.zero_grad()
        if self._is_fp16:
            self.optimizer.backward(loss)
        else:
            loss.backward()
        self.optimizer.step()

    def train(self, chunk_dirs: Iterable, batch_size: int, current_iteration: int,
              nb_epochs: int, train_progress: TrainProgress):

        self.native_model.train()
        batch_size = batch_size * max(1, self._gpu_count)
        logger.info('Batch size: {}'.format(batch_size))

        loader = self.get_data_loader(chunk_dirs=chunk_dirs,
                                      batch_size=batch_size,
                                      transform=self.transform_train,
                                      target_transform=self.transform_target)

        train_history = {'loss': [], 'acc': []}
        for epoch in range(1, nb_epochs + 1):
            train_progress.on_epoch_start(epoch)

            epoch_started_at = time.time()
            nb_epoch = (current_iteration - 1) * nb_epochs + epoch
            self.adjust_learning_rate(nb_epoch)
            epoch_loss = 0.0
            correct = 0
            batch_started_at = time.time()
            for batch_idx, (input_, target) in enumerate(loader, 0):
                # noinspection PyUnresolvedReferences
                if self._is_fp16 and not isinstance(input_, torch.HalfTensor):
                    input_ = input_.half()
                if self._gpu_count:
                    input_, target = input_.to(self.device), target.to(self.device)

                # pylint: disable=E1102
                output = self.native_model(input_)
                loss = self._criterion(output, target)
                loss_item = loss.item()
                epoch_loss += loss_item
                # noinspection PyUnresolvedReferences
                _, predicted = torch.max(output.data, 1)
                correct += predicted.eq(target).sum().item()
                self.optimizer_step(loss)
                batch_finished_at = time.time()
                batch_time = batch_finished_at - batch_started_at
                batch_started_at = batch_finished_at
                logger.info(
                    'Train Epoch: {epoch} [{it}/{total_it} ({progress:.0f}%)]\tLoss: {loss:.4f}\tTime: {time:.2f} secs'.format(
                        epoch=epoch,
                        it=(batch_idx + 1) * len(input_),
                        total_it=len(loader.dataset),
                        progress=100. * batch_idx / len(loader),
                        loss=epoch_loss / (batch_idx + 1),
                        time=batch_time
                    ))
            epoch_time = time.time() - epoch_started_at
            epoch_loss = epoch_loss / len(loader)
            epoch_acc = correct / len(loader.dataset)

            train_history['loss'].append(epoch_loss)
            train_history['acc'].append(epoch_acc)

            train_progress.on_epoch_end(epoch=epoch, accuracy=epoch_acc, loss=epoch_loss, epoch_time=epoch_time)

        return train_history

    def eval(self, chunk_dirs: Iterable, batch_size: int):
        # noinspection PyUnresolvedReferences
        # from torch import from_numpy
        self.native_model.eval()
        test_loss = 0
        correct = 0

        loader = self.get_data_loader(
            chunk_dirs=chunk_dirs,
            batch_size=batch_size,
            transform=self.transform_eval,
            target_transform=self.transform_target
        )

        with torch.no_grad():
            for input_, target in loader:
                if self._gpu_count:
                    input_, target = input_.to(self.device), target.to(self.device)
                outputs = self.native_model(input_)
                loss = self._criterion(outputs, target)
                test_loss += loss.item()
                # noinspection PyUnresolvedReferences
                _, predicted = torch.max(outputs.data, 1)
                correct += predicted.eq(target).sum().item()
                # correct += (predicted == target).sum().item()

        test_loss /= len(loader)
        test_acc = correct / len(loader.dataset)
        logger.info('\nTest set: Average loss: {:.8f}, Accuracy: {}/{} ({:.4f}%)\n'.format(
            test_loss, correct, len(loader.dataset), test_acc))
        return test_loss, test_acc

