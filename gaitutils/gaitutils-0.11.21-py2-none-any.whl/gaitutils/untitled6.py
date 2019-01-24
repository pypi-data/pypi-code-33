# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 13:47:01 2019

@author: hus20664877
"""

import gaitutils
import logging

#fn = r"C:\Users\hus20664877\Dropbox\File requests\trondheim_gait_data\Tobias Goihl - 4-511_P3_Tardieu02.c3d"
#gaitutils.Trial(fn)


fn = r"C:\Users\hus20664877\Desktop\Vicon_data\H0078_JH\2017_11_18_seur_JH\2017_11_18_seur_JH08.c3d"
#tr = gaitutils.trial.nexus_trial()
tr = gaitutils.Trial(fn)

pl = gaitutils.Plotter()
pl.layout = gaitutils.cfg.layouts.lb_kinetics

pl.plot_trial(tr)
