#! /usr/bin/env python

import rasterio
import rasterio.features
import rasterio.warp

import sys

fn=sys.argv[1]
#rds = rasterio.open(fn)

#with rasterio.open(fn) as dataset:
dataset = rasterio.open(fn)
a = dataset.read(masked=True)

# Read the dataset's valid data mask as a ndarray.
mask = dataset.dataset_mask()

sys.exit()

# Extract feature shapes and values from the array.
for geom, val in rasterio.features.shapes(mask, transform=dataset.transform):

    # Transform shapes from the dataset's own coordinate
    # reference system to CRS84 (EPSG:4326).
    geom = rasterio.warp.transform_geom(dataset.crs, 'EPSG:4326', geom, precision=6)

    # Print GeoJSON shapes to stdout.
    print(geom)
