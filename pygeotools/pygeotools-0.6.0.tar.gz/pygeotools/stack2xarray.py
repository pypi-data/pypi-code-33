#! /usb/bin/env python

import sys
from pygeotools.lib import malib, geolib, timelib
import xarray as xr

stack_fn=sys.argv[1]

stack = malib.DEMStack(stack_fn=stack_fn)

stack_ds = stack.get_ds()
dims = ('time','y','x')
#Need to scrub date_list, can't have identical dates in xarray
dt_list = timelib.fix_repeat_dt(stack.date_list)
stack_coord = geolib.get_xy_1D(stack_ds)
coords = {'time':dt_list, 'x':stack_coord[0], 'y':stack_coord[1]}
#Create the xarray DataArray
xra = xr.DataArray(stack.ma_stack, coords=coords, dims=dims)

#Chunking
#import dask.array as da
#chunk_size=256
#xra = xra.chunk(chunks={'x':chunk_size,'y':chunk_size})
#xra.mean(dim='time').compute()

#xra.mean(dim='time')
#xra.interpolate_na(dim='time')
#xra['time.season']
#xra.groupby('time.month').mean(axis=0)

#Need to recreate datearray 
