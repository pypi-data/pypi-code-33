#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
Example analysis of the direct operational costs per flying hour based on a F41 Schedule P5.2 database from the United
States Department of Transportation
"""


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import aeropy.airlines.analysis


# Create analysis objects and select aircraft
# 694: A320
# 634: B737-800
# 614: B737-900
# Explanatory tables are available in the database, see airlines\database\F41SCHEDULE_P52_18082017\L_AIRCRAFT_TYPE.csv_
a320_costs = aeropy.airlines.analysis.DirectOperationalCostsData()
a320_costs.aircraft_type = 694
b737_costs = aeropy.airlines.analysis.DirectOperationalCostsData()
b737_costs.aircraft_type = [634, 614]

# Select year
a320_costs.year = 2015
b737_costs.year = 2015

# Analyse data
a320_cost_result = a320_costs.analyse()
b737_cost_result = b737_costs.analyse()

# Plot data
plot_data = np.column_stack((a320_cost_result['val'], b737_cost_result['val']))
plot_frame = pd.DataFrame(plot_data,
                          columns = ['A320 (n='+str(a320_costs.samples)+')',
                                     'B737 (n='+str(b737_costs.samples)+')'],
                          index = a320_cost_result['key'])
plot_frame.plot(kind='bar')
plt.ylabel('costs (in $/h)')
plt.title('direct operational cost analysis')
plt.tight_layout()
plt.show()
