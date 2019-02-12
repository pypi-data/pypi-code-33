#!/usr/bin/env python
'''
navigator_tf
Created by Seria at 04/02/2019 4:48 PM
Email: zzqsummerai@yeah.net

                    _ooOoo_
                  o888888888o
                 o88`_ . _`88o
                 (|  0   0  |)
                 O \   。   / O
              _____/`-----‘\_____
            .’   \||  _ _  ||/   `.
            |  _ |||   |   ||| _  |
            |  |  \\       //  |  |
            |  |    \-----/    |  |
             \ .\ ___/- -\___ /. /
         ,--- /   ___\<|>/___   \ ---,
         | |:    \    \ /    /    :| |
         `\--\_    -. ___ .-    _/--/‘
   ===========  \__  NOBUG  __/  ===========
   
'''
# -*- coding:utf-8 -*-
import tensorflow as tf
import time
from copy import deepcopy
from collections import defaultdict
from .navigator import Stage

class NavigatorTF(object):
    roman_numeral = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
    def __init__(self, dashboard, time_machine, fuel_depot, spacecraft):
        config = {'NG': spacecraft.engine.param, 'TM':time_machine.param,
                  'FD': {}, 'DB': dashboard.param, 'BP': spacecraft.blueprint.param}
        ft = fuel_depot.dataset
        for k in ft.keys():
            config['FD'][k] = ft[k].param

        self.propellants = defaultdict(list)
        self.epoch = 0
        self.mile = 0
        self.mpe = 0
        self.batch = {}
        self.destination = {}
        self.macro_stage = ''
        # start a session
        self.sess = tf.Session(config=spacecraft.engine.config_proto)
        self.time_machine = time_machine
        self.fuel_depot = fuel_depot
        self.spacecraft = spacecraft
        self.dashboard = dashboard
        self.feedPropellant(Stage.START, self.time_machine._setParams,
                            sess=self.sess, mile=self.spacecraft.mile, scope=self.spacecraft.scope, config=config)
        self.feedPropellant(Stage.START, self.time_machine.backTo)

    def feedPropellant(self, stage, propellant, position=None, condition='True', **kwargs):
        if isinstance(position, int):
            quantity = len(self.propellants[stage])
            if position < quantity:
                self.propellants[stage][position] = (propellant, condition, kwargs)
            else:
                for p in range(quantity, position):
                    self.propellants[stage].append((None, 'False'))
        self.propellants[stage].append((propellant, condition, kwargs))

    def _airDrop(self, stage, n, **kwargs):
        # kwargs.update(self.propellants[stage][n][2])
        self.propellants[stage][n] = self.propellants[stage][n][0:2] + (kwargs,)

    def _triggerStage(self, curr_stage):
        for stg in Stage.stages:
            exec('%s = "%s"' % (stg, stg))
        mile = self.mile+1
        epoch = self.epoch+1
        stage = self.macro_stage
        stats = []
        cnt = 0
        for ppl, cond, kwargs in self.propellants[curr_stage]:
            cnt += 1
            if_meet = eval(cond)
            if (ppl is None) or (not if_meet):
                stats.append(None)
                continue
            stats.append(ppl(**kwargs))
        return stats

    def runAMile(self, fuel_line, pass_by=(), destination=(), interval=1):
        assert len(pass_by)+len(destination) > 0
        start = time.time()
        fl = {}
        filled_fl = {}
        quan_preflight = len(self.propellants[Stage.PREFLIGHT])
        if quan_preflight == 0: # no propellant in Preflight stage
            for i, k in enumerate(fuel_line.keys()):
                if isinstance(fuel_line[k], str):
                    fl[self.spacecraft.layout[k]] = self.batch[fuel_line[k]]
                    filled_fl[k] = self.batch[fuel_line[k]]
                else:
                    fl[self.spacecraft.layout[k]] = fuel_line[k]
                    filled_fl[k] = fuel_line[k]
        else:
            for i, k in enumerate(fuel_line.keys()):
                filled_fl[k] = self.batch[fuel_line[k]]
            for i in range(quan_preflight):
                self._airDrop(Stage.PREFLIGHT, i, fuel_line=filled_fl)
            temp_fl = self._triggerStage(Stage.PREFLIGHT)
            for tfl in temp_fl:
                if not tfl is None:
                    for k in tfl.keys():
                        fl[self.spacecraft.layout[k]] = tfl[k]
                    break

        pb = [self.spacecraft.layout[k] for k in pass_by]
        dst = [self.spacecraft.layout[k] for k in destination]
        spot = self.sess.run(pb + dst, fl)
        spot = spot[len(pass_by):len(pass_by)+len(destination)]
        sp = {}
        filled_sp = {}
        for j in range(len(destination)):
            filled_sp[destination[j]] = spot[j]
        quan_analyzer = len(self.propellants[Stage.ANALYZE])
        if quan_analyzer == 0:  # no propellants in Analyze stage
            sp = deepcopy(filled_sp)
        else:
            for j in range(quan_analyzer):
                self._airDrop(Stage.ANALYZE, j, fuel_line=filled_fl, destination=filled_sp)
            temp_sp = self._triggerStage(Stage.ANALYZE)
            for tsp in temp_sp:
                if not tsp is None:
                    sp = tsp
                    break

        prefix = self.macro_stage + ':'
        for k in sp.keys():
            self.destination[prefix + k] = sp[k]
        self.dashboard._gauge(self.destination.items(), self.mile, self.epoch, self.mpe,
                                  time.time()-start, interval)

    def runAnEpoch(self, fuel_tank, miles=-1):
        self.mpe = self.fuel_depot.milesPerEpoch(fuel_tank)
        if miles < 0:
            miles = self.mpe
        # cores = cpu_count() // 1
        # print("Creating %d-process pool" % cores)
        # pool = Pool(cores)
        for mi in range(miles):
            self.mile = mi
            # begin = time.time()
            self.batch = self.fuel_depot.nextBatch(fuel_tank)
            # print('%.3fs' % (time.time() - begin))
            for stg in Stage.phases[-1]:
                self._triggerStage(stg)

        self.destination = {}

    def log(self, guage=True, tachograph=True, blueprint=True):
        self.dashboard._log(guage, tachograph)
        if blueprint:
            self.spacecraft.blueprint.log(self.dashboard.param['log_path'])

    def launch(self, epochs=1):
        try:
            print('+' + 35 * '-' + '+')
            print('| The Spacecraft is being launched. |')
            print('+' + 35 * '-' + '+')
            self._triggerStage(Stage.START)
            if epochs < 0 or not isinstance(epochs, int):
                raise ValueError('epochs must be a non-positive integer.')
            for ep in range(epochs):
                self.epoch = ep
                for stg in Stage.phases[0]:
                    self.macro_stage = stg
                    self._triggerStage(stg)
            self._triggerStage(Stage.END)
            print('+' + 44 * '-' + '+')
            print('| The Spacecraft has arrived at destination. |')
            print('+' + 44 * '-' + '+')

        except BaseException as e:
            if Stage.BREAK_DOWN in self.propellants:
                self._triggerStage(Stage.BREAK_DOWN)
            else:
                raise e