import tempfile
import aether as ae
from aether_shared.utilities.geotiff_utils import geotiff_utils
from PIL import Image, ImageDraw
import rasterio
import time
import glymur
from aether_shared.utilities.geometry_utils import geometry_utils
import numpy as np
from rasterio.warp import calculate_default_transform, reproject
from rasterio.enums import Resampling
import json
from rasterio.coords import BoundingBox
from rasterio import transform

class geotiff_transforms_handler(object):

    def __init__(self, global_objects, logger):
        self._global_objects = global_objects
        self._logger = logger

    ####################################################################################################
    # This method downloads a series of layers (e.g., bands), applies a crop to match the polygon, then
    # stacks the images into one [x,y,b] geotiff. It then applies a mask and a color table.
    #
    # See RasterLayer proto buffer for more information of its structure.
    ####################################################################################################
    def crop_raster_layer(self, raster_layer, polygon, projection_crs, destination_stub):
        self._logger.info("Starting Job: {}".format(raster_layer))

        temporary_file = self._global_objects.filemanager().retrieve_stub(raster_layer.download_stub)
        self._logger.info("Using temporary file: {}".format(temporary_file.name))

        # Rasterio handles GeoTIFF and JP2 Drivers; but, all writing will be done in GeoTIFF
        with rasterio.open(temporary_file.name) as src:
            utm_polygon = geometry_utils.transform_latlng_to_pixels(src.meta["crs"], [polygon])[0]
            crop_data, crop_mask, crop_meta = self.geotiff_window_read(src, utm_polygon)

            # Now, transform to the new CRS
            if (projection_crs is not None) and (src.crs != projection_crs):
                crop_data, crop_mask, crop_meta = \
                    geotiff_transforms_handler.reproject_geotiff_into_crs(
                        crop_data, crop_mask, crop_meta, utm_polygon, polygon, src, projection_crs)

        color_table = None
        if len(raster_layer.color_table) != 0:
            color_table = {int(k):v for k,v in json.loads(raster_layer.color_table).iteritems()}

        self._logger.info("Writing band to location {}".format(destination_stub))
        f = tempfile.NamedTemporaryFile(delete=True)
        geotiff_utils.write_geotiff_components_to_tiff(crop_data, crop_mask, crop_meta, f.name, color_table=color_table)
        self._global_objects.filemanager().upload_stub(f, destination_stub)
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
            'affine': projected_transform,
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
        print("Loaded window read in time {}".format(time.time()-s))

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
            affine=src.window_transform(polygon_window),
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