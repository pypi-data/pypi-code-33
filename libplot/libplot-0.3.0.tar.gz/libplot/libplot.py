#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 31 17:15:07 2018

@author: antony
"""
import matplotlib
import os
#matplotlib.use('agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib_venn as mpv
import math
import scipy.stats

ALPHA = 0.8
MARKER_SIZE = 10
BLACK_RGB = (0, 0, 0)

TRANS_GRAY = (0.5, 0.5, 0.5, 0.5)

BLUES = sns.color_palette('Blues', 8)[2:]
GREENS = sns.color_palette('Greens', 8)[2:]

DEFAULT_WIDTH = 8
DEFAULT_HEIGHT = 8

FONT_PATH = '/usr/share/fonts/truetype/msttcorefonts/Arial.ttf'

def setup():
  if os.path.exists(FONT_PATH):
      prop = matplotlib.font_manager.FontProperties(fname=FONT_PATH)
      matplotlib.rcParams['font.family'] = prop.get_name()
  else:
      matplotlib.rcParams['font.family'] = 'Arial' #prop.get_name()
      
  matplotlib.rcParams['axes.unicode_minus'] = False
  matplotlib.rcParams['font.size'] = 14 
  matplotlib.rcParams['mathtext.default'] = 'regular'
  
  sns.set(font="Arial")
  sns.axes_style({'font.family': ['sans-serif'], 'font.sans-serif': ['Arial']})
  sns.set_style("white")
  sns.set_style("ticks")
  sns.set_style({"axes.facecolor": 'none'})



def format_axes(ax, x='', y='', direction='in'):
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.minorticks_on()
    ax.get_yaxis().set_tick_params(which='both', direction=direction)
    ax.get_xaxis().set_tick_params(which='both', direction=direction)
    
def invisible_axes(ax):
    """
    Make axes invisible.
    
    Parameters
    ----------
    ax :
        Matplotlib ax object.
    """
    
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

def new_ax(fig, subplot=(1,1,1), zorder=1, root_ax=None, sharex=None, sharey=None, direction='in'):
    if isinstance(subplot, str):
        if ':' in subplot:
            subplot = tuple(int(c) for c in subplot.split(':'))
        else:
            subplot = tuple(int(c) for c in subplot)
    elif isinstance(subplot, int):
        subplot = tuple((subplot // (10 ** i)) % 10 for i in range(math.ceil(math.log(subplot, 10)) - 1, -1, -1))
    
    if root_ax is not None:
        sharex=root_ax
        sharey=root_ax
        zorder=root_ax.zorder + 10
    
    ax = fig.add_subplot(subplot[0], subplot[1], subplot[2], zorder=zorder, sharex=sharex, sharey=sharey)
  
    ax.patch.set_alpha(0)
    
    if root_ax is not None:
        
        invisible_axes(ax)
    else:
        format_axes(ax, direction=direction)
        
    return ax


def new_base_fig(w=8, h=8):
    if isinstance(w, tuple):
        h = w[1]
        w = w[0]
        
    fig = plt.figure(figsize=(w, h))
    
    return fig


def newfig(w=8, h=8, subplot=(1,1,1), direction='in'):
    return new_fig(w=w, h=h, subplot=subplot, direction=direction)

def new_fig(w=8, h=8, subplot=111, direction='in'):
    fig = new_base_fig(w, h)
    
    ax = new_ax(fig, subplot, direction=direction)
  
    return fig, ax


def grid_size(n):
    return int(np.ceil(np.sqrt(n)))

def polar_fig(w=5, h=5, subplot=111):
    fig = plt.figure(figsize=[w, h])
    #ax = fig.add_subplot(subplot, polar=True)
    return fig

def polar_ax(fig, subplot=111):
    if type(subplot) is tuple:
        ax = fig.add_subplot(subplot[0], subplot[1], subplot[2], polar=True)
    else:
        ax = fig.add_subplot(subplot, polar=True)
    
    return ax

def polar_clock_ax(fig, subplot=111):
    ax = polar_ax(fig, subplot)
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_rgrids([], labels=[])
    ax.set_yticklabels([])
    # Set the grid lines at 0 6 radii
    lines, labels = plt.thetagrids(range(0, 360, 60), list(range(0, 6)))
    ax.tick_params(pad=0.5)
    return ax


def format_legend(ax, cols=6, markerscale=None):
  ax.legend(bbox_to_anchor=[0, 0.95], loc='lower left', ncol=cols, frameon=False, fontsize='small', markerscale=markerscale, handlelength=1, columnspacing=0.5)



def savefig(fig, out, pad=2, dpi=300):
  fig.tight_layout(pad=pad) #rect=[o, o, w, w])
  plt.savefig(out, dpi=dpi)

def hex_to_RGBA(h):
    if isinstance(h, tuple):
        return h
    if isinstance(h, str):
        h = h.replace('#', '')
                      
        if len(h) == 8:
            return tuple(int(h[i:i+2], 16) for i in (0, 2 ,4, 6))
        else:
            return tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))
    else:
        return BLACK_RGB
                  
def hex_to_rgba(h):
    if isinstance(h, tuple):
        return h
    if isinstance(h, str):
        return tuple(x / 255 for x in hex_to_RGBA(h))
    else:
        return BLACK_RGB

def parse_colors(colors):
    return [hex_to_rgba(c) for c in colors]
    
def swarmplot(df, x=None, y=None, hue=None, width=0.1, colors=BLUES, linewidth=0, size=2, orient='v', tint=0, ax=None):
    if ax is None:
        fig, ax = new_fig()
        
    colors = parse_colors(colors)
    colors = get_tint(colors, tint)
    
    print(colors)
      
    sns.swarmplot(x=x, y=y, hue=hue, data=df, palette=colors, size=size, linewidth=linewidth, orient="v", ax=ax)
      
    return ax

def base_boxplot(df, x=None, y=None, hue=None, width=0.1, colors=BLUES, linewidth=1.5, fliersize=2, orient='v', tint=0, ax=None):
    if ax is None:
        fig, ax = new_fig()
      
    #sns.boxplot(x=x, y=y, hue=hue, data=df, width=width, fliersize=fliersize, color=color, linewidth=linewidth, orient="v", saturation=1, ax=ax)
    
    colors = parse_colors(colors)
    
    colors = get_tint(colors, tint)
    
    sns.boxplot(x=x, y=y, hue=hue, data=df, width=width, palette=colors, fliersize=fliersize, linewidth=linewidth, orient="v", saturation=1, ax=ax)
      
    for i in range(0, len(ax.lines)):
        color = colors[i // 6]

        line = ax.lines[i]
        line.set_color(color)
        line.set_markerfacecolor(color)
        line.set_markeredgecolor(color)
        line.set_solid_capstyle('butt')
        
        # Change the outlier style
        if i % 6 == 5:
            line.set_marker('o')
      
    for i in range(4, len(ax.lines), 6):      
        ax.lines[i].set_color('white')
     
    #print(len(ax.artists))
    
    for i in range(0, len(ax.artists)):
        color = colors[i]
        ax.artists[i].set_facecolor(color)
        ax.artists[i].set_edgecolor(color)
            
    return ax


def boxplot(df, x=None, y=None, hue=None, width=0.1, colors=BLUES, linewidth=1.5, fliersize=2, orient='v', tint=0, ax=None):
    ax = base_boxplot(x=x, y=y, hue=hue, df=df, width=width, colors=colors, linewidth=linewidth, fliersize=fliersize, orient=orient, tint=tint, ax=ax)
      
    format_axes(ax, x=x, y=y)
    
    ax.tick_params(axis='x',which='minor',bottom='off')
      
    return ax


def base_violinplot(df, x=None, y=None, hue=None, width=0.4, colors=BLUES, tint=0, fig=None, ax=None):
    if ax is None:
        fig, ax = new_fig()
        
    colors = parse_colors(colors)
    colors=get_tint(colors, tint)
    print(colors)
    
    sns.violinplot(x=x, y=y, hue=hue, data=df, width=width, palette=colors, linewidth=0, orient='v', saturation=1, ax=ax)
      
    format_axes(ax, x=x, y=y)
    
    ax.tick_params(axis='x',which='minor',bottom='off')
      
    return fig, ax


def violinplot(df, x=None, y=None, hue=None, width=0.4, colors=BLUES, tint=0, ax=None):
    fig, ax = base_violinplot(df, x=x, y=y, hue=hue, width=width, colors=colors, tint=tint, ax=ax)
      
    format_axes(ax, x=x, y=y)
      
    return fig, ax

def violinboxplot(df, x=None, y=None, hue=None, width=0.6, colors=BLUES, fig=None, wf=1.5):
    if fig is None:
        if x is not None:
            w = np.unique(df[x]).size
            print(w)
        else:
            w = df.shape[1]
        
        w *= wf
        
        fig = new_base_fig(w=w, h=6)
        
    ax = new_ax(fig)
    
    base_violinplot(df, x=x, y=y, hue=hue, width=width, colors=colors, tint=0.5, ax=ax)
    
    format_axes(ax, x=x, y=y)
    
    ax2 = new_ax(fig, root_ax=ax)
    
    base_boxplot(df, x=x, y=y, hue=hue, width=width/4, colors=colors, ax=ax2)
      
    #invisible_axes(ax2)
      
    return fig


def scatter(x, y, s=MARKER_SIZE, c=None, cmap=None, norm=None, alpha=ALPHA, marker='o', fig=None, ax=None, label=None):
    if ax is None:
        fig, ax = new_fig()
        
    ax.scatter(x, y, s=s, color=c, cmap=cmap, norm=norm, marker=marker, alpha=alpha, label=label)
    
    return fig, ax


def correlation_plot(x, y, marker='o', s=MARKER_SIZE, c=None, cmap=None, norm=None, alpha=ALPHA, xlabel=None, ylabel=None, x1=None, x2=None, fig=None, ax=None):
    if ax is None:
        fig, ax = new_fig()
         
    ax.scatter(x, y, c=c, cmap=cmap, norm=norm, s=s, marker=marker, alpha=alpha)
    
    sns.regplot(x, y, ax=ax, scatter=False)
    
    if xlabel is not None:
        ax.set_xlabel(xlabel)
        
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    
    #if cmap is not None:
    #    add_colorbar(fig, cmap, x1=None, x2=None, norm=norm)
    
    return fig, ax


def plot(x, y, s=MARKER_SIZE, c=None, alpha=ALPHA, fig=None, ax=None, linewidth=1, label='', solid_capstyle='round'):
    if ax is None:
        fig, ax = new_fig()
        
    gcf = ax.plot(x, y, c=c, alpha=alpha, label=label, linewidth=linewidth, solid_capstyle=solid_capstyle)
    
    return fig, ax, gcf


def venn2(s1, s2, l1, l2, fig=None, ax=None):
    if ax is None:
        fig, ax = new_fig()
    
    if not isinstance(s1, set):
        s1 = set(s1)
        
    if not isinstance(s2, set):
        s2 = set(s2)
    
    v = mpv.venn2([s1, s2], set_labels = (l1, l2), ax=ax)
    
    v.get_patch_by_id('10').set_alpha(0.25)
    v.get_patch_by_id('10').set_color('#2ca05a')
    v.get_label_by_id('10').set_color('#2ca05a')
    
    v.get_patch_by_id('11').set_alpha(0.25)
    v.get_patch_by_id('11').set_color('#165044')
    v.get_label_by_id('11').set_color('white')
    
    
    
    v.get_patch_by_id('01').set_alpha(0.25)
    v.get_patch_by_id('01').set_color('#2c5aa0')
    v.get_label_by_id('01').set_color('#2c5aa0')
    
    return fig, ax, v


  



def add_colorbar(fig, cmap, x1=None, x2=None, norm=None):
    cax = fig.add_axes([0.8, 0.1, 0.15, 0.02], zorder=100)
    cb = matplotlib.colorbar.ColorbarBase(cax, cmap=cmap, ticks=[0, 1.0], orientation='horizontal')
    
    if x1 is None:
        if norm is not None:
            x1 = norm.vmin
        else:
            x1 = 0
            
    if x2 is None:
        if norm is not None:
            x2 = norm.vmax
        else:
            x2 = 1
    
    cb.set_ticklabels([x1, x2])
    cb.outline.set_linewidth(0.1)
    cb.ax.tick_params(width=0.1, length=0)


def cart2pol(x, y):
    theta = np.arctan2(y, x)
    rho = np.sqrt(x**2 + y**2)
    return (theta, rho)


def pol2cart(theta, rho):
    x = rho * np.cos(theta)
    y = rho * np.sin(theta)
    return (x, y)


def get_tint(colors, t):
    if isinstance(colors, tuple):
        r = max(0, min(1, (colors[0] + (1 - colors[0]) * t)))
        g = max(0, min(1, (colors[1] + (1 - colors[1]) * t)))
        b = max(0, min(1, (colors[2] + (1 - colors[2]) * t)))
        
        if len(colors) == 4:
            return (r, g, b, colors[3])
        else:
            return (r, g, b)
    elif isinstance(colors, list):
        ret = []
        
        for color in colors:
            r = max(0, min(1, (color[0] + (1 - color[0]) * t)))
            g = max(0, min(1, (color[1] + (1 - color[1]) * t)))
            b = max(0, min(1, (color[2] + (1 - color[2]) * t)))
            
            if len(color) == 4:
                ret.append((r, g, b, color[3]))
            else:
                ret.append((r, g, b))
            
        return ret
    else:
        return colors
    
    
    
def bin_data(x, y, bins=100):
    ys = np.empty(0)
    xs = np.empty(0)
    xs_std = np.empty(0)
    
    idx = 0
    
    tcurrent = 0
    tend = x.max()
    tinc = (tend - x.min()) / bins
    
    n = x.shape[0]
    
    while tcurrent < tend:
        #print(idx)
        tnext = tcurrent + tinc

        # find all points in the bin
        e = y[(x >= tcurrent) & (x < tnext)]
        
        #print(e)
        
        if e.size > 0:
            #m,_ = scipy.stats.mode(e)
            #m = m[0]
            
            #print(e)
            #print(tcurrent, e.mean())
            m = np.mean(e)
            ys = np.append(ys, m)
            xs_std = np.append(xs_std, np.std(e))
        else:
            ys = np.append(ys, 0)
            xs_std = np.append(xs_std, 0)
        
        xs = np.append(xs, tcurrent)
        
        tcurrent = tnext
        
    return xs, ys


def color_labels(ax, colors, indices, color_indices=None):
    """
    Color labels on an axes object.
    
    Parameters
    ----------
    ax : matplotlib axes
        Axes to adjust
    colors : list or array
        List of colors to use for labelling
    indices : list or int
        List of label indices to color. If indices is an int, it will be
        interpreted as a range between 0 and n (exclusive).
    """
    
    if isinstance(indices, int):
        indices = np.array([i for i in range(0, indices)])
        
    if not isinstance(indices, np.ndarray):
        indices = np.array(indices)
        
    if color_indices is None:
        color_indices = indices
        
    if not isinstance(color_indices, np.ndarray):
        color_indices = np.array(color_indices)
    
    for i in range(0, indices.size):
        t = ax.get_yticklabels()[indices[i]]
        t.set_color(colors[color_indices[i]])