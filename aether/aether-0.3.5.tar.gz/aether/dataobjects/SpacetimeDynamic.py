import numpy as np
import json
import copy
import rasterio
from rasterio.warp import reproject, Resampling
from aether.dataobjects.SpacetimeMixins import SpacetimeMixins

class BoundMethod():

    def __init__(self):
        pass

    def if_placeholder(self):
        pass

    def method(self):
        pass



################################################################################################################
#
# The Spacetime object is a dynamic loading wrapper for a SpacetimeBuilder. The Spacetime object also has a
# number of helper functions, such as PNG image generation, and conversion into Numpy arrays.
#
# The key insight into the Spacetime object is that the SpacetimeBuilder is a lightweight set of URL pointers to
# cloud based objects. As a result, the data must be downloaded to be used locally. The Spacetime object handles
# this, and does so by only downloading data as needed. This helps maintain the lightweight performance of the
# Spacetime ecosystem.
#
# Note: the user may request three slice methods:
#   1) ts=all; bands=[integer subset]
#   2) ts=[integer subset]; bands=all
#   3) ts=[integer subset 1]; bands=[integer subset 2]
# In other words, there is no mix-and-match across ts or bands. The returned object (As a numpy array) should always
# be 4-D [n_ts, n_x, n_y, n_bands].
#
#
# There is no guarantee that the SpacetimeBuilder:
#  a) contains the same number of layers per timestamp.
#  b) contains the same layers for each timestamp.
#  c) containers layer of identical spatial resolution.
#
# Problems a & b require that the Spacetime object check for consistency between operations. I.e., If two timestamps
#  are converted to Numpy arrays, and those timestamps have different numbers of layers, the resulting operation
#  is designed to i) check for consistency and ii) return an error, prior to any downloading, if consistency is not
#  held. An alternative would be to return an array of two Numpy arrays. For this version, we will prioritize simpler
#  blocks of bands.
#
# Problem c requires every layer to be transformed to a reference geospatial frame. The geospatial reference frame is
#  the raster ts=[0]; band=[0]. Note that this band will always be downloaded. This transformation will be done for
#  even cases when all bands are the same spatial resolution. This prevents one-off errors and other troubles of
#  cropping that sometimes leave some rasters one or a few pixels wider or higher than others in the same set.
#
# TODO(astrorobotic): Add the reference geospatial frame as an index element of the SpacetimeBuilder so that the data
#  does not need to be downloaded.
#
# Production notes: This makes obsolete the Sky.download() function as a user-facing functionality. It can be
#  evaluated to be set to deprecate at a future time.
#
################################################################################################################

class SpacetimeDynamic(object):

    def __init__(self, spacetime_builder, sky):
        self._spacetime_builder = spacetime_builder
        self._sky = sky

        self._timestamps = list(sorted(spacetime_builder.timestamps.keys()))

        self._raster_layer_names = {}
        for ts in self._timestamps:
            self._raster_layer_names[ts] = [spacetime_builder.timestamps[ts].layers[i].canonical_name for i in range(len(spacetime_builder.timestamps[ts].layers))]

        self.clear_cache()
        self._reference_crs = None

    def timestamps(self):
        return self._timestamps

    def timestamp(self, ts_i):
        return self._timestamps[ts_i]

    def clear_cache(self, spare_reference=False):
        self._raster_layer_cache = {}
        for ts in range(len(self._timestamps)):
            self._raster_layer_cache[ts] = {}

        if not spare_reference:
            self._reference_crs = None

    # Here, metadata is referenced for each ts_i and b_i explicitly.
    # If ts_i = None and b_i = None, then the metadata of the SpacetimeBuilder is accessed.
    # If ts_i = value1 and b_i = value2, then the metadata of that RasterLayer is accessed.
    def _metadata(self, ts_i, b_i):
        if ts_i is None and b_i is None:
            return self._spacetime_builder.properties
        if ts_i is None or b_i is None:
            return None
        if ts_i is not None and b_i is not None:
            return self._spacetime_builder.timestamps[self.timestamp(ts_i)].layers[b_i].properties
        return None

    def _generate_mask(self, ts_i):
        try:
            src_f = self._download_and_cache_one_layer(ts_i, 0)
            ref_src_f = self.get_reference_crs()
            with rasterio.open(src_f.name) as src:
                mask = src.read_masks(1)
                if src_f != ref_src_f:
                    with rasterio.open(ref_src_f.name) as ref_src:
                        mask = self._reproject_data(mask, src, ref_src)
            return mask
        except:
            return None

    def _has_color_table(self, ts_i, b_i):
        return True if self._generate_color_table(ts_i, b_i) is not None else False

    def _generate_color_table(self, ts_i, b_i):
        try:
            table = json.loads(self._spacetime_builder.timestamps[self.timestamp(ts_i)].layers[b_i].color_table)
            return table
        except:
            return None

    def _normalize_inputs(self, ts, bands):
        if isinstance(ts, int):
            ts = [ts]
        if isinstance(bands, int):
            bands = [bands]
        return ts, bands

    def _download_and_cache_one_layer(self, ts_i, b_i, force=False):
        if force or b_i not in self._raster_layer_cache[ts_i]:
            layer = self._spacetime_builder.timestamps[self.timestamp(ts_i)].layers[b_i]
            self._raster_layer_cache[ts_i][b_i] = self._sky.download_stub(layer.download_stub, as_file_with_suffix=".tif")
        return self._raster_layer_cache[ts_i][b_i]

    def get_reference_crs(self):
        if self._reference_crs is None:
            self._reference_crs = self._download_and_cache_one_layer(ts_i=0, b_i=0)
        return self._reference_crs

    def _reproject_data(self, data, src, ref_src):
        ref_data_size = ref_src.read().shape

        projected = np.zeros(ref_data_size)
        reproject(data, projected,
                  src_transform = src.transform,
                  src_crs = src.crs,
                  dst_transform = ref_src.transform,
                  dst_crs = ref_src.crs,
                  resampling = Resampling.nearest)
        return projected

    def reproject_to_reference(self, src_f, ref_src_f=None):
        if ref_src_f is None:
            ref_src_f = self.get_reference_crs()

        with rasterio.open(src_f.name) as src:
            data = src.read()
            if src_f != ref_src_f:
                with rasterio.open(ref_src_f.name) as ref_src:
                    data = self._reproject_data(data, src, ref_src)
        return data

    # This internal function ensures that the combination of timestamps and bands forms a 4-D numpy array when
    # downloaded. This requires that every timestamp has the same number of bands. The same layers must be in the
    # same timestamps, as well.
    def _validate_slice_is_4cube(self, ts=None, bands=None):
        if ts is None:
            ts = range(len(self._timestamps))
        if len(ts) <= 1:
            return True
        consistent_bands = self._raster_layer_names[self.timestamp(ts[0])]
        if bands is None:
            bands = range(len(consistent_bands))
        consistent_bands = consistent_bands[bands]
        for ts_i in ts[1:]:
            these_bands = self._raster_layer_names[self.timestamp(ts_i)]
            if len(bands) < len(these_bands) or consistent_bands != these_bands[bands]:
                return False
        return True

    # This internal function will download all not yet downloaded raster layers for the range ts=[integer range] and
    # bands=[integer range]. If either of those are None, all timestamps or all bands are downloaded.
    def _download_as_necessary(self, ts=None, bands=None):
        if not self._validate_slice_is_4cube(ts, bands):
            return False

        if ts is None:
            ts = range(len(self._timestamps))

        for ts_i in ts:
            bands_to_get = range(len(self._raster_layer_names[self.timestamp(ts_i)])) if bands is None else copy.deepcopy(bands)
            for b_i in bands_to_get:
                if b_i in self._raster_layer_cache[ts_i]:
                    continue
                self._download_and_cache_one_layer(ts_i, b_i)
        return True

    def getSrcFilename(self, ts_i, b_i):
        if not self._download_as_necessary(ts=[ts_i], bands=[b_i]):
            return None
        return self._raster_layer_cache[ts_i][b_i].name

    def as_numpy(self):
        return self.bands()

    # This will return None if either the download failed, or the request for timestamps and bands do not form a 4-D
    # Numpy array. The function will automatically project into the reference CRS.
    def bands(self, bands=None, ts=None):
        ts, bands = self._normalize_inputs(ts, bands)
        if not self._download_as_necessary(ts=ts, bands=bands):
            return None

        if ts is None:
            ts = range(len(self._timestamps))

        layers = []
        for ts_i in ts:
            bands_to_get = range(len(self._raster_layer_names[self.timestamp(ts_i)])) if bands is None else copy.deepcopy(bands)
            layer = [self.reproject_to_reference(self._raster_layer_cache[ts_i][b_i]) for b_i in bands_to_get]
            layer = np.concatenate(layer, axis=0)
            layer = np.transpose(layer, axes=[1,2,0])
            layers.append(layer)
        layers = np.array(layers) if len(layers) == 1 else np.concatenate(layers, axis=0)

        return layers

    def generate_image(self, ts, bands, transparent=True, show_now=True, save_to=None):
        ts, bands = self._normalize_inputs(ts, bands)

        stack = self.bands(bands, ts)
        color_table = None
        if self._has_color_table(ts_i=ts[0], b_i=bands[0]):
            color_table = self._generate_color_table(ts_i=ts[0], b_i=bands[0])
        mask = self._generate_mask(ts_i=ts[0]) if transparent else None

        SpacetimeMixins.generate_image(stack, len(bands),
                                       mask=mask, color_table=color_table,
                                       show_now=show_now, save_to=save_to)

