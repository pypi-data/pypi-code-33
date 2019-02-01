#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ecabc/bees.py
#  v.2.2.1
#  Developed in 2018 by Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  This program defines the bee objects created in the artificial bee colony
#

import numpy as np
from random import randint

import uuid

class Bee:

    '''
    Class which stores individual bee bee information. A probability it will get picked, a score
    and the values that pertain to the score
    '''
    
    def __init__(self, values=[], is_employer=True):              
        self.values = values            
        self.unmodified_score = None
        self.probability = 0
        self.failed_trials = 0
        self.score = None
        self.id = uuid.uuid4()
        self.is_employer = is_employer

    def override_score(self, unmodified_score):
        '''
        Force this bee to accept the given score
        '''
        self.score = self.modify_score(unmodified_score)
        self.unmodified_score = unmodified_score

    def update_score(self, unmodified_score, values):
        '''
        Returns True if the score is better than what is 
        currently stored, False if not.
        '''
        score = self.modify_score(unmodified_score)
        if self.score is None or score > self.score:
            self.unmodified_score = unmodified_score
            self.score = score
            self.values = values
            return True
        return False

    def modify_score(self, score):
        if score >= 0:
            return 1 / (1 + score)
        else:
            return 1 + abs(score)

    def calculate_probability(self, bees):
        '''
        Calculate probability based on a given fitness average
        '''
        self.probability = self.score / sum(bee.score for bee in bees)

    def copy(self):
        '''
        Return a copy of this bee
        '''
        bee = Bee(self.values.copy())
        bee.score = self.score
        bee.unmodified_score = self.unmodified_score
        return bee

    def mutate(self, ranges):
        index = randint(0, len(self.values)-1)
        new_value = self.values[index] + np.random.uniform(-1 , 1) * (self.values[index]
             - SUPPORTED_TYPES[ranges[index][0]](ranges[index][1][0], ranges[index][1][1]))
        
        if new_value > ranges[index][1][1]:
            new_value = ranges[index][1][1]
        elif new_value < ranges[index][1][0]:
            new_value = ranges[index][1][0]
        elif ranges[index][0] == 'int':
            new_value = int(new_value)
        
        values = self.values.copy()
        values[index] = new_value
        return values

SUPPORTED_TYPES = {
    'float' : np.random.uniform,
    'int' : randint
}
