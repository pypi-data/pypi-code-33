from __future__ import absolute_import
from __future__ import print_function
import tempfile
from aether_shared.utilities.geotiff_utils import geotiff_utils
import rasterio
from aether_shared.utilities.geometry_utils import geometry_utils
import numpy as np
from rasterio.warp import calculate_default_transform, reproject
from rasterio.enums import Resampling
import json
from rasterio.coords import BoundingBox
import six
from six.moves import range

class geotiff_transforms_handler(object):

    ####################################################################################################
    # This method downloads a series of layers (e.g., bands), applies a crop to match the polygon, then
    # stacks the images into one [x,y,b] geotiff. It then applies a mask and a color table.
    #
    # See RasterLayer proto buffer for more information of its structure.
    ####################################################################################################
    @staticmethod
    def crop_raster_layer(raster_layer, polygon, projection_crs, destination_stub, _filemanager, _logger):
        _logger.info("Starting Job: {}".format(raster_layer))

        temporary_file = _filemanager.retrieve_stub(raster_layer.download_stub)
        _logger.info("Using temporary file: {}".format(temporary_file.name))

        # Rasterio handles GeoTIFF and JP2 Drivers; but, all writing will be done in GeoTIFF
        with rasterio.open(temporary_file.name) as src:
            utm_polygon = geometry_utils.transform_latlng_to_pixels(src.meta["crs"], [polygon])[0]
            crop_data, crop_mask, crop_meta = geotiff_utils.geotiff_window_read(src, utm_polygon)

            # Now, transform to the new CRS
            if (projection_crs is not None) and (src.crs != projection_crs):
                crop_data, crop_mask, crop_meta = \
                    geotiff_transforms_handler.reproject_geotiff_into_crs(
                        crop_data, crop_mask, crop_meta, utm_polygon, polygon, src, projection_crs)

        color_table = None
        if len(raster_layer.color_table) != 0:
            color_table = {int(k):v for k,v in six.iteritems(json.loads(raster_layer.color_table))}

        _logger.info("Writing band to location {}".format(destination_stub))
        f = tempfile.NamedTemporaryFile(delete=True)
        geotiff_utils.write_geotiff_components_to_tiff(crop_data, crop_mask, crop_meta, f.name, color_table=color_table)
        _filemanager.upload_stub(f, destination_stub)
        return destination_stub

    @staticmethod
    def reproject_geotiff_into_crs(crop_data, crop_mask, crop_meta, utm_polygon, polygon, src, projection_crs):
        crop_bounds = BoundingBox(*utm_polygon.to_bounds())

        # The original transform needs to be modified for the crop;
        #  so, transform from and to the same CRS, then re-project.
        original_transform, original_width, original_height = calculate_default_transform(
            src.crs, src.crs, crop_data.shape[1], crop_data.shape[0], *crop_bounds)
        projected_transform, width, height = calculate_default_transform(
            src.crs, projection_crs, crop_data.shape[1], crop_data.shape[0], *crop_bounds)

        reprojected_data = np.zeros((height, width, crop_data.shape[2]), dtype=crop_meta.data["dtype"])
        reprojected_mask = np.zeros((height, width), dtype=np.uint8)

        for i in range(crop_data.shape[2]):
            reproject(
                source=crop_data[:,:,i],
                destination=reprojected_data[:,:,i],
                src_transform=original_transform,
                src_crs=src.crs,
                dst_transform=projected_transform,
                dst_crs=projection_crs,
                resampling=Resampling.nearest)
        reproject(
            source=np.array(crop_mask, dtype=np.uint8),
            destination=reprojected_mask,
            src_transform=original_transform,
            src_crs=src.crs,
            dst_transform=projected_transform,
            dst_crs=projection_crs,
            resampling=Resampling.nearest)
        reprojected_mask = np.array(reprojected_mask, dtype=np.bool)

        crop_meta.update({
            'crs': projection_crs,
            'transform': projected_transform,
            # 'affine': projected_transform,
            'width': width,
            'height': height
        })
        geotiff_utils._update_tiff_blocksize_if_necessary([width, height], crop_meta)
        geotiff_utils._update_driver_to_gtiff_if_necessary(crop_meta)

        # Re-projection can result in a mask around the entirety of the image. And so, we recalculate the
        # polygon pixels inside the new bounds, then extract just that.  The only way I know how to do this is
        # to use the rasterio.window() function, so, that means I need to write band_meta to a temporary meta file.
        with rasterio.open(tempfile.NamedTemporaryFile(delete=True).name, 'w', **crop_meta) as projected_src:
            projected_polygon = geometry_utils.transform_latlng_to_pixels(projection_crs, [polygon])[0]
            projected_window = projected_src.window(*projected_polygon.to_bounds())

            row_start = int(min(max(projected_window.row_off, 0), height))
            col_start = int(min(max(projected_window.col_off, 0), width))
            row_stop = int(max(0, min(projected_window.row_off + projected_window.height, height)))
            col_stop = int(max(0, min(projected_window.col_off + projected_window.width, width)))

            crop_data = reprojected_data[row_start:row_stop, col_start:col_stop]
            crop_mask = reprojected_mask[row_start:row_stop, col_start:col_stop]
            crop_meta.update({
                'width': crop_data.shape[0],
                'height': crop_data.shape[1],
            })
            geotiff_utils._update_tiff_blocksize_if_necessary(crop_data.shape, crop_meta)
            geotiff_utils._update_driver_to_gtiff_if_necessary(crop_meta)

        return crop_data, crop_mask, crop_meta
