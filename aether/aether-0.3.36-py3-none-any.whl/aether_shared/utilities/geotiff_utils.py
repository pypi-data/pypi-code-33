from __future__ import absolute_import
import aether as ae
from rasterio.crs import CRS
from rasterio import transform
import tifffile
import copy
import logging
import numpy as np
from PIL import Image, ImageDraw
import rasterio
import time
import glymur
from aether_shared.utilities.geometry_utils import geometry_utils
import json
import six
from six.moves import range

class geotiff_utils(object):

    # This method handles GeoTiff or JPEG2000 efficiently; and, creates a mask, i.e., unifies these functions.
    @staticmethod
    def geotiff_window_read(src, utm_polygon, make_mask=True):
        polygon_window = src.window(*utm_polygon.to_bounds())

        s = time.time()
        if "driver" in src.meta and src.meta["driver"] == "JPEG2000":
            jp2 = glymur.Jp2k(src.name)
            col_start = int(polygon_window.col_off)
            col_end = int(col_start + polygon_window.width)
            row_start = int(polygon_window.row_off)
            row_end = int(row_start + polygon_window.height)
            crop_data = jp2[row_start:row_end, col_start:col_end]
            if len(crop_data.shape) == 2:
                crop_data = np.expand_dims(crop_data, axis=2)
        else:
            crop_data = src.read(window=polygon_window)
            crop_data = np.transpose(crop_data, axes=[1,2,0])  # To put bands as last dimension.
        print(("Loaded window read in time {}".format(time.time()-s)))

        crop_mask = None
        if make_mask:
            crop_mask = Image.new("1", (crop_data.shape[1], crop_data.shape[0]), False)
            draw = ImageDraw.Draw(crop_mask)
            pixels_polygon = tuple([(x,y) for x,y in geometry_utils.transform_utm_to_pixels(src, utm_polygon).lnglats()])
            draw.polygon(pixels_polygon, fill=(True), outline=(True))

            crop_mask = np.asarray(crop_mask)
            crop_data[~crop_mask] = 0

        # Update profile
        crop_meta = src.profile.copy()
        crop_meta.update(dict(
            width=crop_data.shape[1],
            height=crop_data.shape[0],
            # affine=src.window_transform(polygon_window),
            transform=src.window_transform(polygon_window),
        ))

        geotiff_utils._update_tiff_blocksize_if_necessary(crop_data.shape, crop_meta)
        geotiff_utils._update_driver_to_gtiff_if_necessary(crop_meta)
        return crop_data, crop_mask, crop_meta


    @staticmethod
    def map_crop_into_latlng_bounds(src, src_transform, utm_polygon):
        polygon_window = src.window(*utm_polygon.to_bounds())

        # These values give the pixel locations relative to the post-cropped image, not to the original polygon. The
        # original polygon is represented by the polygon_window values.
        col_off = np.max([0, np.min([src.meta["width"], polygon_window.col_off])])
        col_end = np.max([0, np.min([src.meta["width"], polygon_window.width + polygon_window.col_off])])
        row_off = np.max([0, np.min([src.meta["height"], polygon_window.row_off])])
        row_end = np.max([0, np.min([src.meta["height"], polygon_window.height + polygon_window.row_off])])

        # These values are the location of the cropped window relative to the original polygon.
        actual_col_start = -polygon_window.col_off
        actual_col_end = -polygon_window.col_off + col_end
        actual_row_start = -polygon_window.row_off
        actual_row_end = -polygon_window.row_off + row_end

        xs, ys = transform.xy(src_transform, [actual_row_start, actual_row_end], [actual_col_start, actual_col_end])
        utm_bounds = [xs[0], ys[1], xs[1], ys[0]]

        crop_polygon = geometry_utils.transform_to_latlng(src.meta["crs"], [ae.AEPolygon().from_bounds(utm_bounds)])[0]
        return crop_polygon

    @staticmethod
    def write_geotiff_components_to_tiff(data, mask, meta, local_filename, color_table=None):
        # This flag should not create a .msk file when write_mask() is called.
        with rasterio.Env(GDAL_TIFF_INTERNAL_MASK=True):
            with rasterio.open(local_filename, 'w', **meta) as src:
                for n_band in range(data.shape[2]):
                    src.write(data[:,:,n_band], indexes=n_band+1)
                    if color_table is not None:
                        src.write_colormap(n_band+1, color_table)
                if mask is not None:
                    src.write_mask(mask)
        return True

    @staticmethod
    def write_numpy_to_4d_tiff(data, destination_filename):
        tifffile.imsave(destination_filename, data)

    @staticmethod
    def cropWithinSpacetimeDynamic(spacetime, ts, bands, polygon):
        ts, bands = spacetime._normalize_inputs(ts, bands)
        if not spacetime._download_as_necessary(ts=ts, bands=bands):
            return None

        if ts is None:
            ts = list(range(len(spacetime.timestamps())))

        with rasterio.open(spacetime.get_reference_crs().name) as ref_src:
            crop_data, crop_mask, crop_meta = geotiff_utils.geotiff_window_read(ref_src, polygon, make_mask=False)
            crop_polygon = geotiff_utils.map_crop_into_latlng_bounds(ref_src, crop_meta["transform"], polygon)

        stack = []
        for ts_i in ts:
            layers = []
            bands_to_get = list(range(len(spacetime._raster_layer_names[spacetime.timestamp(ts_i)]))) if bands is None else copy.deepcopy(bands)
            for b_i in bands_to_get:
                if not spacetime._download_as_necessary(ts=[ts_i], bands=[b_i]):
                    return None
                with rasterio.open(spacetime._raster_layer_cache[ts_i][b_i].name) as src_i:
                    crop_data, _, _ = geotiff_utils.geotiff_window_read(src_i, polygon, make_mask=False)
                    layers.append(crop_data)
            layers = np.concatenate(layers, axis=0)
            layers = np.transpose(layers, axes=[1,2,0])
            stack.append(layers)
        stack = np.array(stack) if len(stack) == 1 else np.stack(stack, axis=0)
        return ae.Spacetime(stack, crop_mask, crop_meta), crop_polygon

    @staticmethod
    def read_colormap(src, band=1):
        try:
            logging.getLogger("rasterio").setLevel(logging.WARNING)
            colormap = src.colormap(band)
            logging.getLogger("rasterio").setLevel(logging.INFO)
            return colormap
        except:
            return None

    @staticmethod
    def read_masks(src, band=1):
        try:
            mask = np.array(src.read_masks()[band-1] == 255, dtype=int)
            mask = mask.tolist()
            return mask
        except:
            return None

    @staticmethod
    def clean_json_loads_of_colormap(j):
        colormap = json.loads(j)
        colormap = {int(k):v for k,v in six.iteritems(colormap)}
        return colormap

    # The blocksize sets the size of regions in the GeoTiff that can be window read. When the blocksize is larger than
    # the image height or width, an error will be thrown when rasterio writes the data.
    @staticmethod
    def _update_tiff_blocksize_if_necessary(image_size, meta):
        if "blockxsize" in meta.data and meta.data["blockxsize"] > image_size[0]:
            meta.update(dict(blockxsize=int(2 ** (np.floor(np.log2(image_size[0]))))))
        if "blockysize" in meta.data and meta.data["blockysize"] > image_size[1]:
            meta.update(dict(blockysize=int(2 ** (np.floor(np.log2(image_size[1]))))))

    @staticmethod
    def _update_driver_to_gtiff_if_necessary(meta):
        meta.update({"driver": "GTiff"})
        return meta

    @staticmethod
    def _update_geotiff_dtype(dtype_name, meta):
        meta.update({'dtype': dtype_name})
        return meta

    @staticmethod
    def rasterio_metadata_to_dict(metadata):
        dict_metadata = copy.deepcopy(metadata)
        if "crs" in dict_metadata and isinstance(dict_metadata["crs"], CRS):
            dict_metadata["crs"] = dict_metadata["crs"].to_string()
        return dict_metadata

    @staticmethod
    def rasterio_metadata_from_dict(dict_metadata):
        metadata = copy.deepcopy(dict_metadata)
        if "crs" in metadata and (isinstance(metadata["crs"], str) or isinstance(metadata["crs"], six.text_type)):
            metadata["crs"] = CRS.from_string(metadata["crs"])
        return metadata
