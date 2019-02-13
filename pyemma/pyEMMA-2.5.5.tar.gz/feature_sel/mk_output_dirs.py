
lags = [750, 1000, 1250, 1500, 1750, 2000]
import os
base = '/home/marscher/NO_BACKUP/'
for l in lags:
    os.makedirs(os.path.join(base, 'final_lag_%s' % l, 'logs'), exist_ok=True)
