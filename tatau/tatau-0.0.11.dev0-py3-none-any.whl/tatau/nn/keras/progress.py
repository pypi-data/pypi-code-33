import time

from keras.callbacks import Callback

from tatau.nn.tatau.progress import TrainProgress


class ProgressCallback(Callback):
    def __init__(self, train_progress: TrainProgress):
        super().__init__()
        self.train_progress = train_progress
        self.epoch_started_at = None

    def on_epoch_begin(self, epoch, logs=None):
        self.epoch_started_at = time.time()
        self.train_progress.on_epoch_start(epoch + 1)

    def on_epoch_end(self, epoch, logs=None):
        self.train_progress.on_epoch_end(
            epoch=epoch + 1,
            accuracy=logs['acc'],
            loss=logs['acc'],
            epoch_time=time.time() - self.epoch_started_at,
        )
