#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:25:38 2015

Nexus specific plotting

@author: Jussi (jnu@iki.fi)
"""

import logging

from gaitutils import (Plotter, layouts, trial, plot_plotly, cfg)


def single_trial_plot(layout):
    """ Plot a single trial loaded in Nexus """

    tr = trial.nexus_trial()

    if cfg.plot.backend == 'matplotlib':
        pl = Plotter()
        pl.trial = tr
        pl.layout = layout
        maintitle = pl.title_with_eclipse_info('EMG plot for')
        pl.plot_trial(maintitle=maintitle)
        pdf_prefix = 'EMG_'
        pl.create_pdf(pdf_prefix=pdf_prefix)

    elif cfg.plot.backend == 'plotly':
        plot_plotly.plot_trials_browser([tr], layout,
                                        legend_type='short_name_with_cyclename')

    else:
        raise ValueError('Invalid plotting backend')
