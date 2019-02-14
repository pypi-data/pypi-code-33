import chainer
import cv2

import numpy as np

from chainer.backends import cuda
from chainer.training import extension
from chainer.training import trigger as trigger_module

from IPython.display import Image, display, clear_output

class WriteImage(extension.Extension):
    def __init__(self, filename=None, key=None, trigger=(100, 'iteration'), batch_channel=0, scale_factor=1.0, should_display=None):
        self.filename = filename
        self.key = key
        self._trigger = trigger_module.get_trigger(trigger)
        self.batch_channel = batch_channel
        self.scale_factor = scale_factor
        self.should_display = should_display

    def __call__(self, trainer):
        if self._trigger(trainer):
            data = trainer.observation[self.key]
            self.write_image(self.batch_channel, data, self.filename, self.scale_factor)
            if self.should_display is not None:
                if self.should_display is 'clear':
                    clear_output()
                display(Image(self.filename))

    @staticmethod
    def write_image(batch_channel, data, filename, scale):
        data = cuda.to_cpu(chainer.as_variable(data).array)
        if data.shape[1] != 3:
            data = data[batch_channel, 0, :, :]
            data = np.clip(data * scale, 0.0, 255.0)
        else:
            data = data[batch_channel, :, :, :]
            data = np.rollaxis(data, 2)
            data = np.rollaxis(data, 2)
            data = np.clip(data * scale, 0.0, 255.0)
        data = np.uint8(data)
        cv2.imwrite(filename, data)

    def serialize(self, serializer):
        if hasattr(self._trigger, 'serialize'):
            self._trigger.serialize(serializer['_trigger'])

