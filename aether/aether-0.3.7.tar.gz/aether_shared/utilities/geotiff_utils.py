import rasterio
from rasterio.crs import CRS
import tifffile
import copy
import logging
import numpy as np
import json

class geotiff_utils(object):

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

    # # Extracts a polygon region from the GeoTiff, i.e., a window read.
    # @staticmethod
    # def extract_polygon_from_tiff(data, utm_polygon, inscribed_polygons_only=True):
    #     window, in_crop_pixels = geometry_utils.map_from_utm_polygons_to_pixels(data, utm_polygon, return_none_if_out_of_bounds=inscribed_polygons_only)
    #
    #     # window will be none if return_none_if_out_of_bounds is true, and the utm pixel is entirely outside the range
    #     # of the image.
    #     if window is None:
    #         return None, None, None, None, None
    #
    #     local_data, local_mask, local_window = geotiff_utils._geotiff_window_read(data, window, in_crop_pixels)
    #
    #     meta = data.profile.copy()
    #     meta.update(dict(
    #         width=local_data.shape[1],
    #         height=local_data.shape[0],
    #         affine=data.window_transform(local_window),
    #         transform=data.window_transform(local_window),
    #     ))
    #     geotiff_utils._update_tiff_blocksize_if_necessary(local_data.shape, meta)
    #     geotiff_utils._update_driver_to_gtiff_if_necessary(meta)
    #     return local_data, local_mask, meta, window, in_crop_pixels

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
        colormap = {int(k):v for k,v in colormap.iteritems()}
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
        if "crs" in metadata and (isinstance(metadata["crs"], str) or isinstance(metadata["crs"], unicode)):
            metadata["crs"] = CRS.from_string(metadata["crs"])
        return metadata
