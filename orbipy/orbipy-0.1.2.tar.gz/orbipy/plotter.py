# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 00:02:39 2018

@author: stasb
"""
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
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
    
    @staticmethod
    def create_axes(ax=None,
                    proj_count=0,
                    fsize=(5.,5.),
                    vertical=False):
        if proj_count < 1:
            raise ValueError("Projections wasn't specified")
        
#        second = False
        if ax is None:
            if vertical:
                fig, ax = plt.subplots(proj_count,1,
                                       figsize=(fsize[0],fsize[1]*proj_count))
            else:
                fig, ax = plt.subplots(1,proj_count,
                                       figsize=(fsize[0]*proj_count,fsize[1]))
        else:
#            second = True
            fig = (ax[0] if isinstance(ax, np.ndarray) else ax).figure
        
        return fig, ax

        
    
    def translate_scale(self, 
                        data,
                        centers={'x':0., 'y':0., 'z':0.}):
        cdata = data.copy()
        for c in centers:
            if isinstance(data, pd.DataFrame):
                if c in cdata:
                    cdata[c] -= centers[c]
            else:
                i = mapper.col2idx(c)
                if i < cdata.shape[1]:
                    cdata[:,i] -= centers[c]
        
        cdata = self.scaler.convert_data(cdata)
        return cdata
    
    def plot(self, 
             data, 
             ax=None, 
             projection='x-y',
             color='r',
             label=None,
             **kwargs):
        if ax is None:
            raise RuntimeWarning("plotter.plot: axes wasn't specified")
            return
        
        p = tuple(projection.split('-'))
        
        if isinstance(data, pd.DataFrame):
            h = data[p[0]]
            v = data[p[1]]             
        else:
            i, j = mapper.col2idx(p[0]), mapper.col2idx(p[1])
#            if data.ndim == 3:
#                h, v = data[:,i,:], data[:,j,:]
#            else:
            h, v = data[:,i], data[:,j]
        
        ax.plot(h, v, color, label=label, **kwargs)
            
    def plot_proj(self, data,
                  transcale=True,
                  projections=('x-y','x-z','y-z'),
                  centers={'x':0., 'y':0., 'z':0.},
                  vertical=False,
                  colors='b',
                  ax=None,
                  fsize=(5., 5.),
                  grid=False,
                  xlabel=True,
                  ylabel=True,
                  legend=False,
                  **kwargs):
                
        n = len(projections)
        fig, ax = self.create_axes(ax, n, fsize, vertical)
                            
        if transcale:
            cdata = self.translate_scale(data, centers)
        else:
            cdata = data
        
        for ip, prj in enumerate(projections):
            if n > 1 and ip >= ax.shape[0]:
                break
            p = tuple(prj.split('-'))
                        
            xlbl = '%s, %s'%(p[0], self.get_label(self.scaler.units, mapper.col2cat(p[0])))
            ylbl = '%s, %s'%(p[1], self.get_label(self.scaler.units, mapper.col2cat(p[1])))
#            ylbl2 = '%s, %s'%(mapper.col2cat(p[1]), 
#                              self.get_label(self.scaler.units, mapper.col2cat(p[1])))

            cur_ax = ax[ip] if isinstance(ax, np.ndarray) else ax

            self.plot(cdata, cur_ax, prj, colors[ip%len(colors)], ylbl, **kwargs)                        
            
            if xlabel: cur_ax.set_xlabel(xlbl)
            if ylabel: cur_ax.set_ylabel(ylbl)
#            if ylabel: cur_ax.set_ylabel(ylbl2 if second else ylbl)
            cur_ax.grid(grid)
            if legend: cur_ax.legend()
            
        fig.tight_layout()
        return ax
    
    def plot_manifold(self, data,
                      method='fast',
                      pts=100,
                      projections=('x-y','x-z','y-z'),
                      centers={'x':0., 'y':0., 'z':0.},
                      vertical=False,
                      colors='b',
                      ax=None,
                      fsize=(5., 5.),
                      grid=False,
                      xlabel=True,
                      ylabel=True,
                      legend=False,
                      **kwargs):
        n = len(projections)
        fig, ax = self.create_axes(ax, n, fsize, vertical)

        cdata = self.translate_scale(data, centers)
        
        method = method.lower()
        
        if method == 'fast':
            self.plot_proj(cdata.values[:,2:],
                           False,
                           projections, centers,
                           vertical, colors,
                           ax, fsize, grid,
                           xlabel, ylabel,
                           legend, **kwargs)
        elif method == 'slow':
            for br_idx in cdata.br.unique():
                br = cdata[cdata.br==br_idx]
                for tr in br.tr.unique():
                    self.plot_proj(br[br.tr==tr].values[:,2:],
                                   False,
                                   projections, centers,
                                   vertical, colors,
                                   ax, fsize, grid,
                                   xlabel, ylabel,
                                   legend, **kwargs)
        elif method == 'intr':
            for br_idx in cdata.br.unique():
                br = cdata[cdata.br==br_idx]
                trajs = []
                for tr_idx in br.tr.unique():
                    arr = br[br.tr==tr_idx].values[:,2:]
                    l = np.zeros(arr.shape[0])
                    l[1:] = np.cumsum(np.sum((arr[1:,1:4]-arr[:-1,1:4])**2, axis=1)**0.5)
                    intrp = interp1d(l, arr[:,1:], axis=0, kind='cubic',
#                                     assume_sorted=False, 
                                     fill_value='extrapolate')
                    t = np.linspace(l[0], l[-1], pts)
                    s = intrp(t)
                    trajs.append(np.hstack((t.reshape(-1,1), s)))
                branch = np.stack(tuple(trajs), axis=2)
                
                self.plot_proj(branch,
                               False,
                               projections, centers,
                               vertical, colors,
                               ax, fsize, grid,
                               xlabel, ylabel,
                               legend, **kwargs)
        return ax

