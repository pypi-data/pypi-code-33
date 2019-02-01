#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ecabc/abc.py
#  v.2.2.1
#  Developed in 2018 Hernan Gelaf-Romer <hernan_gelafromer@student.uml.edu>
#
#  This program implements an artificial bee colony to tune ecnet hyperparameters
#

import sys as sys
import os.path
from random import randint
import numpy as np
from colorlogging import ColorLogger
from multiprocessing import Pool, cpu_count
from numpy.random import choice

try:
    import ujson as json
except:
    import json as json

# artificial bee colony packages
from ecabc.bees import Bee, SUPPORTED_TYPES


class ABC:

    '''
    ABC object: Manages bee and onlooker bees to optimize a set of generic values
    given a generic user defined fitness function. Handles data transfer and manipulation
    between bees.
    '''

    def __init__(self, fitness_fxn, value_ranges=[], num_employers=50, print_level='info', file_logging='disable', processes=4, args={}):
        self._logger = ColorLogger(stream_level=print_level, file_level=file_logging)
        self._value_ranges = value_ranges
        self._num_employers = num_employers
        self._best_bee = None
        self._fitness_fxn = fitness_fxn
        self._processes = processes
        self._processes = processes
        self._bees = []
        self._args = args
        self._average_score = 0
        self._unmodified_average = 0
        if processes > 1:
            self._pool = Pool(processes)
        else:
            self._pool = None

        if len(value_ranges) > 0:
            self._limit = len(value_ranges) * num_employers
        else:
            self._limit = num_employers * 2

        if not callable(self._fitness_fxn):
            raise ValueError('submitted *fitness_fxn* is not callable')

    def add_argument(self, arg_name, arg_value):
        '''
        Add an argument that will be processed by the fitness
        function. Doing this after you have initiliazed the abc
        bees and have started running the abc may produce
        some weird results\n

        Args:\n
        arg_name: The keyword name of your argument\n
        arg_value: The value of the given argument
        '''
        if len(self._bees) > 0:
            self._logger.log('warn', 'Adding an argument after the bees have been created')
        if self._args is None:
            self._args = {}
        self._args[arg_name] = arg_value

    def add_value(self, value_type, value_min, value_max):
        '''
        Add another value that will be factored into the calculation
        of the bee's fitness. Calling this after the abc has run for
        a few iterations may produce wonky results\n
        Args:\n
        value_type: Either of type 'int' or type 'float'\n
        value_min: Minimum numerical value\n
        value_max: Maximum numerical value\n
        '''
        if len(self._bees) > 0:
            self._logger.log('warn', 'Adding a value after bees have been created')
        value = (value_type,  (value_min, value_max))
        self._value_ranges.append(value)
        self._limit = self._num_employers * len(self._value_ranges)

    @property
    def args(self):
        '''
        Arguments that will be passed to the fitness function at runtime
        '''
        return self._args

    @args.setter
    def args(self, args):
        self._args = args
        self._logger.log('debug', "Args set to {}".format(args))

    @property
    def num_employers(self):
        return self._num_employers

    @num_employers.setter
    def num_employers(self, num_employers):
        if num_employers < 10:
            self._logger.log('warn', "Cannot set num_employers to < 10, setting to 10")
            self._num_employers = 10
        else:
            self._num_employers = num_employers
            self._logger.log('debug', "Number of bees set to {}".format(num_employers))

    @property
    def processes(self):
        '''
        Value which indicates how many processes are allowed to be a spawned
        for various methods/calculations at a time. If the number is less than 1,
        multiprocessing will be disabled and the program will run everything synchroniously
        '''
        return self._processes

    @processes.setter
    def processes(self, processes):
        if self._processes > 1:
            self._pool.close()
            self._pool.join()

        self._processes = processes
        if self._processes > 1:
            self._pool = Pool(processes)
        else:
            self._pool = None
        self._logger.log('debug', "Number of processes set to {}".format(processes))

    def infer_process_count(self):
        '''
        Set the amount of processes that will be used to
        the amount of CPU's in your system 
        '''
        try:
            self.processes = cpu_count()
        except NotImplementedError:
            self._logger.log('error', "Could not get cpu count, setting amount of processes back to 4")
            self.processes = 4

    @property
    def value_ranges(self):
        return self._value_ranges

    @value_ranges.setter
    def value_ranges(self, value_ranges):
        self._value_ranges = value_ranges
        self._logger.log('debug', "Value ranges set to {}".format(value_ranges))

    @property
    def best_performer(self):
        '''
        Return a tuple (best_score, best_values)
        '''
        return (self._best_bee.unmodified_score, self._best_bee.values.copy())

    @property
    def limit(self):
        '''
        Get the maximum amount of times a bee can perform below average
        before completely abandoning its current food source and seeking
        a randomly generated one
        '''
        return self._limit

    @property
    def average(self):
        '''
        Returns the current average of all bee scores. This average will be a 
        number between 0 and 1
        '''
        return self._average_score

    @property
    def unmodified_average(self):
        '''
        Returns the average of all the bee scores. This average will reflect the
        results from the fitness function directly.
        '''
        return self._unmodified_average

    @limit.setter
    def limit(self, limit):
        '''
        Set the maximum amount of times a bee can perform below average
        before completely bandoning its current food source and seeking
        a randomly generate done
        '''
        self._limit = limit

    def run_iteration(self):
        '''
        Run a single iteration of the bee colony. This will produce fitness scores
        for each bee, merge bees based on probabilities, and calculate new positions for
        bees if necessary. At the end of this method, the best_performer attribute may 
        or may not have been updated if a better food source was found
        '''
        self._calc_average()
        self._search()

    def create_employers(self):
        '''
        Gerenate a set of employer bees. This method must be called before 
        actually running the artificial bee colony
        '''
        self.__verify_ready(True)
        self._logger.log('debug', "Args : {}".format([arg for arg in self._args.keys()]))
        unmodified_scores = []
        self._logger.log('debug', "Generating employers")
        for i in range(self._num_employers):
            bee = Bee(self.__gen_random_values(), i < self._num_employers)
            if self._processes > 1:
                unmodified_scores.append(self._pool.apply_async(self._fitness_fxn, [bee.values], self._args))
            else:
                bee.update_score(self._fitness_fxn(bee.values, **self._args), bee.values)
                self._logger.log('debug', "Employer number {} created".format(i + 1))
            self._bees.append(bee)
        if self._processes > 1:
            for i, bee in enumerate(self._bees):
                try:
                    bee.update_score(unmodified_scores[i].get(), bee.values)
                    self._logger.log('debug', "Bee number {} created".format(i + 1))
                except Exception as e:
                    raise e
        self._calc_average()
        self._create_onlooker_bees()

    def _create_onlooker_bees(self):
        '''
        Generate all onlooker bees
        '''
        probabilities = self._calc_probabilities()
        onlookers = []
        self._logger.log('debug', "Generating Onlookers")
        for i in range(self._num_employers):
            chosen_bee = np.random.choice(self._bees, p=probabilities)
            new_values = chosen_bee.mutate(self._value_ranges)
            bee = Bee(new_values, False)
            if self._processes > 1:           
                bee.score = self._pool.apply_async(self._fitness_fxn, [new_values], self._args)
            else:
                bee.update_score(self._fitness_fxn(new_values, **self._args), new_values)
                self._logger.log('debug', "Onlooker number {} created".format(i + 1))
            onlookers.append(bee)
        if self._processes > 1:
            for i, bee in enumerate(onlookers):
                try:
                    score = bee.score.get()
                    bee.score = None
                    bee.update_score(score, bee.values)
                    self._logger.log('debug', "Onlooker number {} created".format(i + 1))
                except Exception as e:
                    raise e
        self._bees.extend(onlookers)

    def _search(self):
        '''
        Iterate num_employers amount of times. Choose a bee based on probability
        and mutate it if it has not exceeded the limit based on its failed_trials, or
        give it a completely new food source if it has. 
        '''
        self._logger.log('debug', "Initializing search")
        self.__verify_ready()
        if self._processes > 1:
            self._multiprocessed_search()
        else:
            for bee in self._bees:
                if bee.failed_trials < self._limit:
                    mutated_values = bee.mutate(self._value_ranges)
                    if bee.update_score(self._fitness_fxn(mutated_values, **self._args), mutated_values):
                        bee.failed_trials = 0
                    else:
                        bee.failed_trials += 1
                else:
                    if bee.is_employers:
                        new_values = self.__gen_random_values()
                    else:
                        probabilities = self._calc_probabilities()
                        chosen_bee = np.random.choice(self._bees, p=probabilities)
                        new_values = chosen_bee.mutate(self._value_ranges)
                    bee.override_score(self._fitness_fxn(new_values, **self._args))
                    bee.values = new_values
                    bee.failed_trials = 0
                    bee.calculate_probability(self._bees)
                if self.__update(bee) is True:
                    self._logger.log('info', "Best score update to score: {} | values: {}".format(bee.unmodified_score, bee.values))

    def _multiprocessed_search(self):
        '''
        Do search but with multiple processes
        '''
        probabilities = self._calc_probabilities()
        new_scores = []
        bees = []
        for bee in self._bees:
            if bee.failed_trials < self._limit:
                new_values = bee.mutate(self._value_ranges)
                new_scores.append([self._pool.apply_async(self._fitness_fxn, [new_values], self._args), new_values, 'below_limit'])
            else:
                if bee.is_employer:
                    new_values = self.__gen_random_values()
                else:
                    chosen_bee = np.random.choice(self._bees, p=probabilities)
                    new_values = chosen_bee.mutate(self._value_ranges)
                new_scores.append([self._pool.apply_async(self._fitness_fxn, [new_values], self._args), new_values, 'above_limit'])
            bees.append(bee)
        for bee, info in zip(bees, new_scores):
            try:
                new_score = info[0].get()
                if info[1] =='above_limit':
                    bee.override_score(new_score)
                    bee.values = info[1]
                    bee.failed_trails = 0
                else:
                    if bee.update_score(new_score, info[1]):
                        bee.failed_trials = 0
                    else:
                        bee.failed_trials += 1
            except Exception as e:
                raise e

    def _calc_average(self):
        '''
        Calculate the average of bee cost. Will also update the best score
        '''
        self._logger.log('debug', "calculating average")
        self.__verify_ready()
        self._average_score = 0
        self._unmodified_average = 0
        for bee in self._bees:
            self._average_score += bee.score
            self._unmodified_average += bee.unmodified_score
            # While iterating through bees, look for the best fitness score/value pairing
            if self.__update(bee) is True:
                self._logger.log('info', "Best score update to score: {} | values: {}".format(bee.unmodified_score, bee.values))
        self._average_score /= len(self._bees)
        self._unmodified_average /= len(self._bees)

        # Now calculate each bee's probability
        self.__gen_probability_values()

    def _calc_probabilities(self):
        probs = []
        for bee in self._bees:
            probs.append(bee.probability)
        return probs

    def import_settings(self, filename):
        '''
        Import settings from a JSON file
        '''
        if not os.path.isfile(filename):
            self._logger.log('error', "file: {} not found, continuing with default settings".format(filename))
        else:
            with open(filename, 'r') as jsonFile:
                data = json.load(jsonFile)
                self._best_bee = None
                if data['best_values'] is not None:
                    self._best_bee = Bee()
                    for index, value in enumerate(data['best_values']):
                        if self._value_ranges[index] == 'int':
                            self._best_bee.values.append(int(value))
                        else:
                            self._best_bee.values.append(float(value)) 
                    self._best_bee.score = float(data['best_score'])
                    self._best_bee.unmodified_score = float(data['best_unmodified_score'])
                self._value_ranges = data['valueRanges']         
                self.num_employers = data['num_employers']
                self.limit = data['limit']
                self.processes = data['processes']
                self._logger.log('info', "Imported settings from file {}.".format(filename))
                self._logger.log('debug', "Settings imported {}".format(data))

    def save_settings(self, filename):
        '''
        Save settings to a JSON file
        '''
        data = dict()
        if self._best_bee is None:
            data['best_score'] = None
            data['best_unmodified_score'] = None
            data['best_values'] = None
        else:
            data['best_score'] = str(self._best_bee.score)
            data['best_values'] = [str(value) for value in self._best_bee.values]
            data['best_unmodified_score'] = str(self._best_bee.unmodified_score)
        data['valueRanges'] = self._value_ranges
        data['num_employers'] = self._num_employers
        data['limit'] = self._limit
        data['processes'] = self._processes
        with open(filename, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)
            self._logger.log('info', "Settings saved to {}".format(filename))
            self._logger.log('debug', "Settings saved {}".format(data))

    def __update(self, bee):
        '''
        Update the best score and values if the given
        score is better than the current best score
        '''
        if self._best_bee is None or bee.score > self._best_bee.score:
            self._best_bee = bee.copy()
            return True
        return False

    def __gen_random_values(self):
        '''
        Generate a random list of values based on the allowed value ranges
        '''
        values = []
        if self._value_ranges == None:
            self._logger.log('crit', "must set the type/range of possible values")
            raise RuntimeError("must set the type/range of possible values")
        else:
            # t[0] contains the type of the value, t[1] contains a tuple (min_value, max_value)
            for t in self._value_ranges:
                if t[0] == 'int':
                    values.append(randint(t[1][0], t[1][1]))
                elif t[0] == 'float':
                    values.append(np.random.uniform(t[1][0], t[1][1]))
                else:
                    self._logger.log('crit', "value type must be either an 'int' or a 'float'")
                    raise RuntimeError("value type must be either an 'int' or a 'float'")
        return values

    def __gen_probability_values(self):
        '''
        Calculate probability for all bees. A bee's 
        probability is it's score divided by the average
        score of all bees
        '''
        for bee in self._bees:
            bee.calculate_probability(self._bees)

    def __verify_ready(self, creating=False):
        '''
        Some cleanup, ensures that everything is set up properly to avoid random
        errors during execution
        '''
        if len(self._value_ranges) == 0:
            self._logger.log('crit', 'Attribute value_ranges must have at least one value')
            raise RuntimeWarning('Attribute value_ranges must have at least one value')
        if len(self._bees) == 0 and creating == False:
            self._logger.log('crit', "Need to create bees")
            raise RuntimeWarning("Need to create bees")

    def __getstate__(self):
        '''
        Returns appropriate dictionary for correctly
        pickling the ABC object in case of multiprocssing
        '''
        state = self.__dict__.copy()
        del state['_logger']
        del state['_pool']
        return state
