import cbor2 as cbor
import json
import math
import numpy as np
import pandas as pd
import redis
import types
import urllib2

import matplotlib.dates as dates
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import mpl_toolkits.axisartist as AA

from datetime import datetime, timedelta
from dateutil import tz
from matplotlib import rcParams
from mpl_toolkits.axes_grid1 import host_subplot
from numpy import inf


res = ['timeseries', 'event', 'minute']
barRes = [ 15000, 30000, 60000, 180000 ] # 15-sec, 30-sec, 1-min, and 3-mon bars

numericTypes = (types.IntType, types.LongType, types.FloatType, types.ComplexType)

colors = ['green', 'blue', 'red', 'brown', 'royalblue', 'hotpink',
          'olivedrab', 'magenta', 'blueviolet', 'aquamarine4', 'peacock',
          'brown4', 'cornflowerblue', 'darkolivegreen4', 'darkviolet']
markers = ['o', 'X', 'D', 's', 'P', '+', '^', 'v', '*', 'h']
linestyles = [':', '-.', '--']

ncol = len(colors)
nmrk = len(markers)
nlst = len(linestyles)
