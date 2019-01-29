#!/usr/bin/env pythonw

#import pandas as pd
#import numpy as np
print('starting')
import matplotlib
if matplotlib.get_backend() != "TKAgg":
    matplotlib.use("TKAgg")
from matplotlib import pyplot as plt
print('imports done')

plt.figure(num=1, figsize=(5, 5))
print('figure done')


from pmagpy import ipmag
from pmagpy import pmag

from pmag_env import set_env
import pmagpy.contribution_builder as cb




def one():
    plt.figure(num=1, figsize=(5, 5))
    x = np.linspace(0, 2, 100)
    plt.plot(x, x, label='linear')
    # PmagPy uses plt.ion/plt.ioff
    #plt.ion()
    plt.draw()  # just draws the figure
    #plt.show()  # shows the figure in a "blocking" way so that it doesn't disappear
    #plt.ioff()
    res = input("hi")

# using plt.ion/plt.ioff semi defeats the blocking-ness of plt.show() so that you can get to the input() line

#def two():
#    pmagplotlib.plot_init(1, 5, 5)
#    x = np.linspace(0, 2, 100)
#    plt.plot(x, x, label="linear")
#    pmagplotlib.draw_figs({"linear": 1})
#    res = input("hi")


#def three():
#    ipmag.thellier_magic(input_dir_path="/Users/nebula/Python/PmagPy/data_files/3_0/Megiddo",
#                         n_specs=2, interactive=True)

one()
#two()
#print(matplotlib.get_backend())
#three()
