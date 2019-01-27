#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import json

# Import flask dependencies
from time import sleep

from flask import Blueprint, render_template, request, jsonify, current_app as app
from aws360api import socketio
from threading import Thread, Event

import anybadge

# Define a blueprint
iot = Blueprint('iot', __name__, url_prefix='/')

# Define thresholds: <2=red, <4=orange <8=yellow <10=green
thresholds = {20: 'red',
              40: 'orange',
              60: 'yellow',
              100: 'green'}

sensors = [
  dict(t=Thread(), delay=2, namespace="/sensor/temperature", name="Température (°C)", low=15, high=24),
  dict(t=Thread(), delay=5, namespace="/sensor/humidity", name="Humidité (%)", low=50, high=99),
  dict(t=Thread(), delay=1, namespace="/sensor/ph", name="PH", low=5, high=7)
]

thread_stop_event = Event()


class ScanThread(Thread):
    def __init__(self, sensor):
        self.sensor = sensor
        super(ScanThread, self).__init__()

    def randomSensorGenerator(self):
        print("Making random weather")
        while not thread_stop_event.isSet():
            svg = badge(self.sensor["name"], self.sensor["low"], self.sensor["high"])
            socketio.emit('svg', {"data": svg}, namespace=self.sensor["namespace"])
            sleep(self.sensor['delay'])

    def run(self):
        self.randomSensorGenerator()


@socketio.on('connect', namespace='/sensor/ph')
def test_connect():
    print('Client connected')

    #Start the random number generator thread only if the thread has not been started before.
    for sensor in sensors:
        # if not sensor['t'].isAlive():
            print("Starting Thread")
            sensor["t"] = ScanThread(sensor=sensor)
            sensor["t"].start()


@socketio.on('disconnect', namespace='/scan')
def test_disconnect():
    print('Client disconnected')

################################################################################
# home blueprint functions
################################################################################


def badge(name, low, high):
    badge = anybadge.Badge(name, "{:#.2g}".format(random.uniform(low, high)), thresholds=thresholds)
    return badge.badge_svg_text

# def scan():
#     name = request.args.get('name', default="-")
#     low = int(request.args.get('low', default="0"))
#     high = int(request.args.get('high', default="0"))


#     print("RECEIVED CONN")
#     # socketio.emit('data', badge(name, low, high))
#     socketio.emit('data', {"msg": "hello"})


@iot.route('sensors', methods=['GET'])
def index():
    return render_template('badge.html', sensors=sensors)
