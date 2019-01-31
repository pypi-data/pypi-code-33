# -*- coding: utf-8 -*-

"""
A training plan. With this, the trainer can set up a proper training cycle for our model.
"""

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class Plan:
    def __init__(self):
        self.batch_size: int = 1

        # This will end the training, whichever is reached first.
        # Set to 0 for infinite.
        self.epochs: int = 10
        self.timeout_minutes: float = 60

        # Optimizer.

        # Learning Rate Schedule.

        # Loss Function.
        pass
