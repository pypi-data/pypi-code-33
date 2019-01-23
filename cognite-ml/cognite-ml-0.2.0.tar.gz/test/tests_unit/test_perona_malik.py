#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import matplotlib.pyplot as plt
import numpy as np
import os 
import pandas as pd
import sys


sys.path.append('../../')
import numpy as np
from cognite_ml.filters import perona_malik


if __name__ == "__main__":    
    X = np.random.rand(1000)
    is_ok = 0
    try:
        for method in ['classic', 'exponential', 'tukey', 'guo','weikert']:
            for integration in ['explicit', 'implicit']:
                perona_malik(X, method=method, gradient_threshold=20, smoothing_factor=50, integration=integration)
        is_ok =1
    except:
        is_ok =0

    # Check the results 
    assert(is_ok==1)