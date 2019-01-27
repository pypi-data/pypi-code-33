#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time
import random

# Import flask dependencies
from flask import Blueprint, Response, render_template, request, jsonify, current_app as app

import anybadge

# Define a blueprint
badger = Blueprint('badger', __name__, url_prefix='/')

# Define thresholds: <2=red, <4=orange <8=yellow <10=green
thresholds = {20: 'red',
              40: 'orange',
              60: 'yellow',
              100: 'green'}

################################################################################
# home blueprint functions
################################################################################


@badger.route('scan', methods=['GET'])
def scan():
    name = request.args.get('name', default="-")
    low = int(request.args.get('low', default="0"))
    high = int(request.args.get('high', default="0"))

    def badge(name):
        while True:
            badge = anybadge.Badge(name, "{:#.2g}".format(random.uniform(low, high)), thresholds=thresholds)
            print(badge.badge_svg_text.replace('\n', '').replace('\r', ''))
            yield """data: {}""".format(badge.badge_svg_text.replace('\n', '').replace('\r', '')) + "\n\n"
            time.sleep(0.8)

    return Response(badge(name), mimetype= 'text/event-stream')


@badger.route('sensors', methods=['GET'])
def index():
    badge = anybadge.Badge('-', '-', thresholds=thresholds)

    sensors = [
      dict(name="Température (°C)", low=15, high=24),
      dict(name="Humidité (%)", low=50, high=99),
      dict(name="PH", low=5, high=7)
    ]

    return render_template('badge.html', sensors=sensors)
