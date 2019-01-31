# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 00:02:39 2018

@author: stasb
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .models import crtbp3_model
from .scaler import scaler
from .mapper import mapper


class plotter:

    label_mapper = {'T': {
                        'm':'min',
                        'h':'hours',
                        'd':'days',
                        'w':'weeks',
                        'M':'months',
                        'Y':'years'
                        },
                    'L': {
                        'Mm': r'${\cdot}10^3$ km',
                        'Gm': r'${\cdot}10^6$ km',
                        'au': 'AU'}
                    }
                    
    @staticmethod
    def get_label(units, category):
        u = units[category][1]
        if category == 'V':
            l, t = u.split('/')
            return plotter.label_mapper['L'].get(l, l) + '/' + \
                   plotter.label_mapper['T'].get(t, t)
        return plotter.label_mapper[category].get(u, u)
    
    def __init__(self, 
                 time_units='d',
                 length_units='km',
                 velocity_units='km/s',                 
                 nondim='nd'):
        self.scaler = scaler()

    @classmethod
    def from_model(cls, model,
                        time_units='d',
                        length_units='km',
                        velocity_units='km/s',
                        nondim='nd'):
        if not isinstance(model, crtbp3_model):
            raise TypeError('Only crtbp3_model currently supported')
        me = cls()
        me.scaler = scaler.from_model(model, 
                                      time_units=(nondim, time_units),
                                      length_units=(nondim, length_units),
                                      velocity_units=(nondim+'/'+nondim, velocity_units),
                                      nondim=nondim)        
        return me 
    
    def plot_proj(self, data, 
                  projections=('x-y','x-z','y-z'),
                  centers={'x':0., 'y':0., 'z':0.},
                  vertical=False,
                  colors='b',
                  ax=None,
                  fsize=(5., 5.),
                  ls='-',
                  marker='',
                  lw=1.,
                  alpha=1.0,
                  grid=False,
                  xlabel=True,
                  ylabel=True,
                  legend=False,
                  **kwargs):
                
        n = len(projections)
        if n < 1:
            raise ValueError("Projections wasn't specified")
            
        second = False
        if ax is None:
            if vertical:
                fig, ax = plt.subplots(n,1,figsize=(fsize[0],fsize[1]*n))
            else:
                fig, ax = plt.subplots(1,n,figsize=(fsize[0]*n,fsize[1]))
        else:
            second = True
            fig = (ax[0] if isinstance(ax, np.ndarray) else ax).figure
        
        cdata = data.copy()
        for c in centers:
            if isinstance(data, pd.DataFrame):
                if c in cdata:
                    col = cdata.index if c == 't' else cdata[c]
                    col -= centers[c]
            else:
                i = mapper.col2idx(c)
                if i < cdata.shape[1]:
                    col = cdata[:,i]
                    col -= centers[c]
        
        cdata = self.scaler.convert_data(cdata)
        
        for ip, prj in enumerate(projections):
            if n > 1 and ip >= ax.shape[0]:
                break
            p = tuple(prj.split('-'))
            if isinstance(data, pd.DataFrame):
                h = cdata.index if p[0] == 't' else cdata[p[0]]
                v = cdata.index if p[1] == 't' else cdata[p[1]]             
            else:
                i, j = mapper.col2idx(p[0]), mapper.col2idx(p[1])
                h, v = cdata[:,i], cdata[:,j]
                        
            xlbl = '%s, %s'%(p[0], self.get_label(self.scaler.units, mapper.col2cat(p[0])))
            ylbl = '%s, %s'%(p[1], self.get_label(self.scaler.units, mapper.col2cat(p[1])))
            ylbl2 = '%s, %s'%(mapper.col2cat(p[1]), 
                              self.get_label(self.scaler.units, mapper.col2cat(p[1])))
                        
            cur_ax = ax[ip] if isinstance(ax, np.ndarray) else ax
            cur_ax.plot(h, v, 
                        colors[ip%len(colors)],
                        ls=ls, marker=marker, lw=lw, label=ylbl,
                        alpha=alpha)
            
            if xlabel: cur_ax.set_xlabel(xlbl)
            if ylabel: cur_ax.set_ylabel(ylbl2 if second else ylbl)
            cur_ax.grid(grid)
            if legend: cur_ax.legend()
            
        fig.tight_layout()
        return ax

