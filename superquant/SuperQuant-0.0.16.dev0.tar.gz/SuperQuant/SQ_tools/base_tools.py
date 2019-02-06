import pandas as pd
import numpy as np
import random
import math
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn
seaborn.set(palette='deep',style='darkgrid')
import QUANTAXIS as QA

def SQ_tools_get_random_position(data):
    data['SQ_position'] = np.random.randint(-1,2,len(data))
    return data




