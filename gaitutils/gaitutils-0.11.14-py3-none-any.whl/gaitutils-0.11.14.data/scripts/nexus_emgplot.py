#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:25:38 2015

EMG plot from Nexus.

@author: Jussi (jnu@iki.fi)
"""

import logging

from gaitutils import Plotter, layouts, register_gui_exception_handler
from gaitutils.config import cfg


def do_plot():
    pl = Plotter()
    pl.open_nexus_trial()
    pdf_prefix = 'EMG_'
    maintitle = pl.title_with_eclipse_info('EMG plot for')

    layout = cfg.layouts.std_emg
    pl.layout = layouts.rm_dead_channels(pl.trial.emg, layout)
    pl.plot_trial(maintitle=maintitle)

    pl.create_pdf(pdf_prefix=pdf_prefix)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    register_gui_exception_handler()
    do_plot()
