import chainer

import numpy as np

from chainer.training import extension
from chainer.training import trigger as trigger_module

class PrintNoLog(extension.Extension):
    def __init__(self, keys=None, trigger=(1, 'iteration')):
        self._keys = keys
        self._trigger = trigger_module.get_trigger(trigger)

    def __call__(self, trainer):
        if not self._trigger(trainer):
            return

        observation = trainer.observation
        stats_cpu = {}

        if self._keys is None:
            self._keys = []
            for k in observation:
                if observation[k].shape == ():
                    self._keys.append(k)
            self._keys.sort()

        for k in self._keys:
            if k not in observation:
                continue
            stats_cpu[k] = float(chainer.backends.cuda.to_cpu(chainer.as_variable(observation[k]).array))  # copy to CPU

        out = ['E {0} I {1}'.format(trainer.updater.epoch, trainer.updater.iteration)]
        for _,k in enumerate(stats_cpu):
            out.append('{0}: {1: 6.2f}'.format(k.replace('main/',''),stats_cpu[k]))
        print('   '.join(out))

class LogHyperparameter(extension.Extension):
    def __init__(self, key='alpha', scale=1.0):
        self.key = key
        self.scale = scale

    def __call__(self, trainer):
        optimizer = trainer.updater.get_optimizer('main')
        observation = trainer.observation
        observation[self.key] = chainer.Variable(np.asarray(getattr(optimizer, self.key) * self.scale))
