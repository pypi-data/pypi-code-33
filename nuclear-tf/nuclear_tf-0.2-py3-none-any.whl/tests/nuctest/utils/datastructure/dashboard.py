import matplotlib.pyplot as plt
from abc import ABCMeta, abstractmethod


class Dashboard:
    __metaclass__ = ABCMeta

    @abstractmethod
    def draw(self):
        pass

    def show(self):
        self.draw()
        plt.show()

    def save(self, save_path, **kwargs):
        self.draw()
        plt.savefig(save_path, **kwargs)
