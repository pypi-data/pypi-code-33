import keras
from modelchimp import settings


class ModelChimpCallback(keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs={}):
        if not logs:
            return

        tracker = settings.current_tracker

        if tracker:
            for l in logs:
                tracker.add_metric(l, logs[l], epoch=epoch)
