from abc import ABC
import uuid


class Component(ABC):

    def __init__(self, log):
        self.logger = log
        self.id = uuid.uuid4()

'''
TODO:
Define functionalities that might be in common on all components for now the only thing that every componet
has is a logger
'''
