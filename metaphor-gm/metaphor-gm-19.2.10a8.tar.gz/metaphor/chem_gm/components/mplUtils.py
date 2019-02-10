# -*- coding: ISO-8859-1 -*-
#-------------------------------------------------------------------------------
# $Id$
#
# Copyright 2016 Jean-Luc PLOIX
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#-------------------------------------------------------------------------------
'''
Created on 13 oct. 2016

@author: jeanluc
'''
try:
    from scipy.stats import linregress
except ImportError:
    from ...monal.util.monaltoolbox import linregress
import numpy as np



# def linregress(target):
#     if OKScipy:
#         return linregloc(target)
#     return linregress(target)
    #raise Exception("scipy cannot be imported here") # a modifier pour une solution de contournement

def draw_stat(ax, target, stat="stdDev", pos=(0.05, 0.95)):
    txt = ""
    stat = stat.lower()
    if stat == 'stddev':
        values = target.ix[0] - target.ix[1]
        txt = "StdDev = %g"% np.nanstd(values)
    elif stat == 'r2':
        _, _, r_value, _, _ = linregress(target)
        R2 = r_value**2
        txt = "R2 = %g"% R2
    elif stat == 'xmean':
        value = np.mean(target[0])
        txt = "X mean = %g"% value
    elif stat == 'ymean':
        value = np.mean(target[1])
        txt = "Y mean = %g"% value
    ax.text(pos[0], pos[1], txt, transform=ax.transAxes)

def draw_stat2(ax, lx, ly, stat="stdDev", pos=(0.05, 0.95)):
    txt = ""
    stat = stat.lower()
    if stat == 'stddev':
        values = [x - y for x, y in zip(lx, ly)]
        txt = "StdDev = %g"% np.nanstd(values)
    elif stat == 'r2':
        target = np.array([lx, ly])
        _, _, r_value, _, _ = linregress(target)
        R2 = r_value**2
        txt = "R2 = %g"% R2
    elif stat == 'xmean':
        value = np.mean(lx)
        txt = "X mean = %g"% value
    elif stat == 'ymean':
        value = np.mean(ly)
        txt = "Y mean = %g"% value
    ax.text(pos[0], pos[1], txt, transform=ax.transAxes)

def draw_stdDev(ax, target, pos=(0.05, 0.95)):
    values = target.ix[0] - target.ix[1]
    txt1 = "StdDev = %g"% np.nanstd(values)
    ax.text(pos[0], pos[1], txt1, transform=ax.transAxes)

def draw_stdDev2(ax, lx, ly, pos=(0.05, 0.95)):
    values = lx - ly
    txt1 = "StdDev = %g"% np.nanstd(values)
    ax.text(pos[0], pos[1], txt1, transform=ax.transAxes)

def draw_R2(ax, target, pos=(0.05, 0.95)):
    _, _, r_value, _, _ = linregress(target)
    R2 = r_value**2
    txt2 = "R2 = %g"% R2
    ax.text(pos[0], pos[1], txt2, transform=ax.transAxes)

def draw_R22(ax, lx, ly, pos=(0.05, 0.95)):
    target = np.array([lx, ly])
    _, _, r_value, _, _ = linregress(target)
    R2 = r_value**2
    txt2 = "R2 = %g"% R2
    ax.text(pos[0], pos[1], txt2, transform=ax.transAxes)

def draw_stdDev_R2(ax, target, pos=(0.05, 0.95, 0.90)):
    values = target.ix[0] - target.ix[1]
    _, _, r_value, _, _ = linregress(target)
    R2 = r_value*r_value
    txt1 = "StdDev = %g"% np.nanstd(values)
    ax.text(pos[0], pos[1], txt1, transform=ax.transAxes)
    txt2 = "R2 = %g"% R2
    ax.text(pos[0], pos[2], txt2, transform=ax.transAxes)

class DraggableAnnot():
    
    def __init__(self, annot, press=0, motion=0, release=0):
        self.annot = annot
        self.press = None
        if press:
            self.connect_press()
        if motion:
            self.connect_motion()
        if release:
            self.connect_release()
    
    def connect(self):
        self.connect_press()
        self.connect_motion()
        self.connect_release()
    
    def connect_motion(self):
        self.cidmotion = self.annot.figure.canvas.mpl_connect(
            'button_motion_event', self.on_motion)
    
    def connect_release(self):
        self.cidrelease = self.annot.figure.canvas.mpl_connect(
            'button_release_event', self.on_release)
    
    def connect_press(self):
        self.cidpress = self.annot.figure.canvas.mpl_connect(
            'button_press_event', self.on_press)
    def on_press(self, event):
        if event.inaxes != self.annot.axes:
            return
        contains, attrd = self.annot.contains(event)
        if not contains:
            return
        ann = self.annot
        x0, y0 = ann.get_position()
        self.press = x0, y0, event.xdata, event.ydata

    def on_release(self, event):
        # faut-il un update_offset
        self.press = None
        self.annot.figure.canvas.draw()

    def on_motion(self, event):    
        if (self.press is None) or (event.inaxes != self.annot.axes):
            return
        x0, y0, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress
        self.annot.set_position((x0 + dx, y0 + dy))
        
        self.annot.figure.canvas.draw()
    
    def disconnect(self):
        self.annot.figure.canvas.mpl_disconnect(self.cidpress)
        self.annot.figure.canvas.mpl_disconnect(self.cidrelease)
        self.annot.figure.canvas.mpl_disconnect(self.cidmotion)



if __name__ == '__main__':
    pass