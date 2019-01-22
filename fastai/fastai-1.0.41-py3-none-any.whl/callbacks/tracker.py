# Contribution from @fredguth, https://github.com/fredguth/fastai_playground.

from fastai.torch_core import *
from fastai.callback import *
from fastai.basic_train import *

__all__ = ['TerminateOnNaNCallback', 'EarlyStoppingCallback', 'SaveModelCallback', 'TrackerCallback', 'ReduceLROnPlateauCallback' ]

class TerminateOnNaNCallback(Callback):
    "A `Callback` that terminates training if loss is NaN."

    def __init__(self):
        self.stop = False

    def on_batch_end(self, last_loss, epoch, num_batch, **kwargs:Any)->None:
        "Test if `last_loss` is NaN and interrupts training."
        if self.stop: return True #to skip validation after stopping during traning
        if torch.isnan(last_loss):
            print (f'Epoch/Batch ({epoch}/{num_batch}): Invalid loss, terminating training.')
            self.stop = True
            return True

    def on_epoch_end(self, **kwargs:Any)->None:
        "Stop the training if necessary."
        return self.stop

class TrackerCallback(LearnerCallback):
    "A `LearnerCallback` that keeps track of the best value in `monitor`."
    def __init__(self, learn:Learner, monitor:str='val_loss', mode:str='auto'):
        super().__init__(learn)
        self.monitor,self.mode = monitor,mode
        if self.mode not in ['auto', 'min', 'max']:
            warn(f'{self.__class__} mode {self.mode} is invalid, falling back to "auto" mode.')
            self.mode = 'auto'
        mode_dict = {'min': np.less, 'max':np.greater}
        mode_dict['auto'] = np.less if 'loss' in self.monitor else np.greater
        self.operator = mode_dict[self.mode]

    def on_train_begin(self, **kwargs:Any)->None:
        "Initializes the best value."
        self.best = float('inf') if self.operator == np.less else -float('inf')

    def get_monitor_value(self):
        "Pick the monitored value."
        if self.monitor=='trn_loss' and len(self.learn.recorder.losses) == 0: return None
        elif len(self.learn.recorder.val_losses) == 0: return None
        values = {'trn_loss':self.learn.recorder.losses[-1:][0].cpu().numpy(),
                  'val_loss':self.learn.recorder.val_losses[-1:][0]}
        for i, name in enumerate(self.learn.recorder.names[3:]):
            values[name]=self.learn.recorder.metrics[-1:][0][i]
        if values.get(self.monitor) is None:
            warn(f'{self.__class__} conditioned on metric `{self.monitor}` which is not available. Available metrics are: {", ".join(map(str, self.learn.recorder.names[1:]))}')
        return values.get(self.monitor)

@dataclass
class EarlyStoppingCallback(TrackerCallback):
    "A `TrackerCallback` that terminates training when monitored quantity stops improving."
    def __init__(self, learn:Learner, monitor:str='val_loss', mode:str='auto', min_delta:int=0, patience:int=0):
        super().__init__(learn, monitor=monitor, mode=mode)
        self.min_delta,self.patience = min_delta,patience
        if self.operator == np.less:  self.min_delta *= -1

    def on_train_begin(self, **kwargs:Any)->None:
        "Initialize inner arguments."
        self.wait = 0
        super().on_train_begin(**kwargs)

    def on_epoch_end(self, epoch, **kwargs:Any)->None:
        "Compare the value monitored to its best score and maybe stop training."
        current = self.get_monitor_value()
        if current is None: return
        if self.operator(current - self.min_delta, self.best):
            self.best,self.wait = current,0
        else:
            self.wait += 1
            if self.wait > self.patience:
                print(f'Epoch {epoch}: early stopping')
                return True

class SaveModelCallback(TrackerCallback):
    "A `TrackerCallback` that saves the model when monitored quantity is best."
    def __init__(self, learn:Learner, monitor:str='val_loss', mode:str='auto', every:str='improvement', name:str='bestmodel'):
        super().__init__(learn, monitor=monitor, mode=mode)
        self.every,self.name = every,name
        if self.every not in ['improvement', 'epoch']:
            warn(f'SaveModel every {self.every} is invalid, falling back to "improvement".')
            self.every = 'improvement'

    def on_epoch_end(self, epoch, **kwargs:Any)->None:
        "Compare the value monitored to its best score and maybe save the model."
        if self.every=="epoch": self.learn.save(f'{self.name}_{epoch}')
        else: #every="improvement"
            current = self.get_monitor_value()
            if current is not None and self.operator(current, self.best):
                self.best = current
                self.learn.save(f'{self.name}')

    def on_train_end(self, **kwargs):
        "Load the best model."
        if self.every=="improvement" and (self.learn.path/f'{self.learn.model_dir}/{self.name}.pth').is_file():
            self.learn.load(f'{self.name}')

class ReduceLROnPlateauCallback(TrackerCallback):
    "A `TrackerCallback` that reduces learning rate when a metric has stopped improving."
    def __init__(self, learn:Learner, monitor:str='val_loss', mode:str='auto', patience:int=0, factor:float=0.2, 
                 min_delta:int=0):
        super().__init__(learn, monitor=monitor, mode=mode)
        self.patience,self.factor,self.min_delta = patience,factor,min_delta
        if self.operator == np.less:  self.min_delta *= -1

    def on_train_begin(self, **kwargs:Any)->None:
        "Initialize inner arguments."
        self.wait, self.opt = 0, self.learn.opt
        super().on_train_begin(**kwargs)

    def on_epoch_end(self, epoch, **kwargs:Any)->None:
        "Compare the value monitored to its best and maybe reduce lr."
        current = self.get_monitor_value()
        if current is None: return
        if self.operator(current - self.min_delta, self.best): self.best,self.wait = current,0
        else:
            self.wait += 1
            if self.wait > self.patience:
                self.opt.lr *= self.factor
                self.wait = 0
                print(f'Epoch {epoch}: reducing lr to {self.opt.lr}')
