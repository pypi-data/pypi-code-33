#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 13 18:04:48 2018

Programa para ajustar la pendiente a las rampas considerando a partir de un
punto determinado, a voluntad, a ver si mejora la deriva.

Versión parala wiki de EMIR. No reajusta la DC

@author: fgl
"""

import argparse

import numpy as np
from astropy.io import fits
import os


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('images', nargs='+')
    cli = parser.parse_args(args)

    process_images(cli.images)
    pass


def process_images(images, nreject=3):
    # primer punto a considerar de la rampa. -1: 2ª mitad

    tread = 1.055289     # lectura productiva [s]
    tread_nd = 1.048046 # lectura no productiva [s]
    trst = 1.056230       # reset [s]

    ini = True

    for i, fname_fits in enumerate(images):
        data, header = fits.getdata(fname_fits, header=True)
        frsec = header['frsec']
        nfrsec = header['nfrsec']
        print('frsec=', frsec, 'nfrsec=', nfrsec)
        if ini:  # comienzo
            ini = False
            toper = header['toper']
            nrdil = header['nrdil']
            nrdil_nd = header['nrdil_nd']
            nfr = nfrsec - nreject + 1
            exptime = header['exptime']
            # print(toper, nrdil, nrdil_nd, nfrsec, exptime)
            dt = (toper / 1000.0 + nrdil_nd * tread_nd + nrdil*tread) / exptime
            # print(dt)
    #        print (exptime,bzero,bscale)
        if frsec < nreject + 1:
            print('reject', frsec)
            continue
        elif frsec == nreject:
            reglist = np.zeros(nfr, dtype=int)
            sumy = np.zeros((2048,2048))
            sumxy = np.zeros((2048,2048))
    #        print ('\t\t',tread_nd,tread,exptime,nfrsec,dt)
            imgobbl = header['imgobbl']
        j = frsec - nreject
        sumxy += np.float_(data)*(j+1)
        sumy += np.float_(data)
        if frsec == nfrsec:
            data=(sumxy - (nfr + 1)*sumy/2)*12 / (nfr*nfr - 1)/ nfr/dt
            data[data<0]=0

if __name__ == '__main__':

    main()