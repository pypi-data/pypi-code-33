# import aether as ae
# from aether_shared.utilities.geometry_utils import geometry_utils
# from flask import current_app
#
# from api.gis.geotiff_transforms_handler import geotiff_transforms_handler
# from utilities.polygon_utils import polygon_utils
# from utilities.tiler_utils import tiler_utils
# from aether_shared.utilities.api_utils import api_utils
# from PIL import Image
#
# import numpy as np
# import rasterio
# import json
# import tempfile
#
# import logging
# logger = logging.getLogger(__name__)
#
#
# class DynamicTileMaker(object):
#
#     def __init__(self, uuid, zoom, resource_name, bands_to_render):
#         self.uuid = uuid
#         self.zoom = zoom
#         self.resource_name = resource_name
#         self.bands_to_render = bands_to_render
#
#         ae.GlobalConfig.set_user(uuid)
#         ae.GlobalConfig._switch_service_locality(to_local=True)
#         ae.GlobalConfig.hostport = "127.0.0.1:5003"
#
#
#     def render(self, bounds):
#         xy_tiles = tiler_utils.bounds_to_xyz_tileset(bounds, self.zoom)
#         poly_tiles = [ae.AEPolygon(tiler_utils.tile_xyz_to_latlng_polygon_coordinates(t, self.zoom)) for t in xy_tiles]
#
#         bands_downloaded = self.bands_to_render + ["QA"]
#
#         resource_name = self.bands_to_render
#         query_parameters = dict(
#             date_acquired=[ae.QueryParameter.Ordered.LAST],
#             bands=bands_downloaded,
#             spacecraft_id=["LANDSAT_8"]
#         )
#
#         for tile in poly_tiles:
#             centroid = polygon_utils.centroid_of_bounds(tile.to_bounds())
#
#             epsilon = 0.0001
#             b = [centroid[1] - epsilon, centroid[0] - epsilon, centroid[1] + epsilon, centroid[0] + epsilon]
#             coordinates = polygon_utils.coordinates_from_bounds(b)
#             centroid_polygon = ae.AEPolygon(coordinates)
#
#             # Each band is compiled and cached independently.
#             layer_cache = {}
#             with ae.SkySession() as sky:
#                 spacetime_builder = \
#                     sky.Resource(resource_name).search(centroid_polygon, query_parameters)
#                 if len(spacetime_builder.timestamps) == 0:
#                     return dict(centroid=json.dumps(centroid), n_tiles_added=0)
#
#                 s = ae.Spacetime(spacetime_builder, sky)
#                 b0 = s.generate_mask(ts_i=0)
#                 b0 = np.expand_dims((b0 == 255), axis=-1)
#
#                 # Get the mask from the QA band.
#                 b_mask = bands_downloaded.index("QA")
#                 with rasterio.open(s.getSrcFilename(ts_i=0, b_i=b_mask)) as mask_src:
#                     with rasterio.open(s.get_reference_crs().name) as ref_src:
#                         utm_bounds = ref_src.bounds
#                         p = ae.AEPolygon().from_bounds(utm_bounds)
#                         p = geometry_utils.transform_to_latlng(ref_src.meta["crs"], [p])
#                         image_bounds = p[0].to_bounds()
#
#                         # Tiles use the XYZ standard (first line creates xy, second line creates latlng into AEPolygons,
#                         # third line creates pixels.)
#
#                         n_tiles_added = 0
#                         for band in self.bands_to_render:
#                             b_i = bands_downloaded.index(band)
#                             with rasterio.open(s.getSrcFilename(ts_i=0, b_i=b_i)) as src_i:
#                                 for tile_i in range(len(utm_tiles)):
#                                     xyz_str = "{resource}/{zoom}/{x}/{y}/".format(
#                                         resource=resource_name, zoom=zoom, x=xy_tiles[tile_i][0], y=xy_tiles[tile_i][1],
#                                     ).lower()
#                                     xyz_band_str = "{resource}/{zoom}/{x}/{y}/{band}/".format(
#                                         resource=resource_name, zoom=zoom, x=xy_tiles[tile_i][0], y=xy_tiles[tile_i][1],
#                                         band=band,
#                                     ).lower()
#                                     self.png_tile_cache = api_utils.simple_cache_get(current_app, 'png_tile_cache', {})
#                                     self.png_layer_cache = api_utils.simple_cache_get(current_app, 'png_layer_cache', {})
#
#                                     if xyz_str in self.png_tile_cache or xyz_band_str in self.png_layer_cache:
#                                         continue
#
#                                     crop_data, _, crop_meta = \
#                                         geotiff_transforms_handler.geotiff_window_read(src_i, utm_tiles[tile_i], make_mask=False)
#                                     crop_mask, _, _ = \
#                                         geotiff_transforms_handler.geotiff_window_read(mask_src, utm_tiles[tile_i], make_mask=False)
#
#                                     crop_polygon = geotiff_transforms_handler.map_crop_into_latlng_bounds(
#                                         src_i, crop_meta["transform"], utm_tiles[tile_i])
#
#                                     data_type = crop_meta["dtype"]
#                                     scale_factor = _bit_depth_scale_factor[data_type]
#                                     crop_data = np.squeeze(np.uint8(crop_data * 255. / scale_factor), axis=2)
#                                     crop_mask = np.squeeze(np.uint8((crop_mask!=1) * 255.), axis=2)
#
#                                     mask = Image.fromarray(crop_mask, mode="L")
#                                     image = Image.fromarray(crop_data, mode="L")
#                                     image.putalpha(mask)
#                                     # image.show()
#
#                                     temporary_file = tempfile.NamedTemporaryFile(delete=False, suffix=".PNG")
#                                     image.save(temporary_file.name)
#
#                                     logger.info("Adding to cache: {} the filename {}".format(xyz_band_str, temporary_file.name))
#                                     if xyz_band_str not in self.png_layer_cache:
#                                         self.png_layer_cache[xyz_band_str] = dict(is_complete=False, parts=[])
#                                     self.png_layer_cache[xyz_band_str]["parts"].append(dict(
#                                         polygon_bounds=crop_polygon.to_bounds(),
#                                         png_filename=temporary_file.name,
#                                     ))
#                                     api_utils.simple_cache_set(current_app, 'png_layer_cache', self.png_layer_cache)
#
#
#         utm_tiles = geometry_utils.transform_latlng_to_pixels(ref_src.meta["crs"], poly_tiles)
#
#
#
#
#         # To conserve space, this routine will compile the images band by band, storing as PNG for each.
#         layer_cache = {}
#         with ae.SkySession() as sky:
#             spacetime_builder = \
#                 sky.Resource(resource_name).search(polygon, query_parameters)
#             if len(spacetime_builder.timestamps) == 0:
#                 return dict(centroid=json.dumps(centroid), n_tiles_added=0)
#
#             s = ae.Spacetime(spacetime_builder, sky)
#             b0 = s.generate_mask(ts_i=0)
#             b0 = np.expand_dims((b0 == 255), axis=-1)
#
#             # Get the mask from the QA band.
#             b_mask = bands_downloaded.index("QA")
#             with rasterio.open(s.getSrcFilename(ts_i=0, b_i=b_mask)) as mask_src:
#                 with rasterio.open(s.get_reference_crs().name) as ref_src:
#                     utm_bounds = ref_src.bounds
#                     p = ae.AEPolygon().from_bounds(utm_bounds)
#                     p = geometry_utils.transform_to_latlng(ref_src.meta["crs"], [p])
#                     image_bounds = p[0].to_bounds()
#
#                     # Tiles use the XYZ standard (first line creates xy, second line creates latlng into AEPolygons,
#                     # third line creates pixels.)
#
#                     n_tiles_added = 0
#                     for band in self.bands_to_render:
#                         b_i = bands_downloaded.index(band)
#                         with rasterio.open(s.getSrcFilename(ts_i=0, b_i=b_i)) as src_i:
#                             for tile_i in range(len(utm_tiles)):
#                                 xyz_str = "{resource}/{zoom}/{x}/{y}/".format(
#                                     resource=resource_name, zoom=zoom, x=xy_tiles[tile_i][0], y=xy_tiles[tile_i][1],
#                                 ).lower()
#                                 xyz_band_str = "{resource}/{zoom}/{x}/{y}/{band}/".format(
#                                     resource=resource_name, zoom=zoom, x=xy_tiles[tile_i][0], y=xy_tiles[tile_i][1],
#                                     band=band,
#                                 ).lower()
#                                 self.png_tile_cache = api_utils.simple_cache_get(current_app, 'png_tile_cache', {})
#                                 self.png_layer_cache = api_utils.simple_cache_get(current_app, 'png_layer_cache', {})
#
#                                 if xyz_str in self.png_tile_cache or xyz_band_str in self.png_layer_cache:
#                                     continue
#
#                                 crop_data, _, crop_meta = \
#                                     geotiff_transforms_handler.geotiff_window_read(src_i, utm_tiles[tile_i], make_mask=False)
#                                 crop_mask, _, _ = \
#                                     geotiff_transforms_handler.geotiff_window_read(mask_src, utm_tiles[tile_i], make_mask=False)
#
#                                 crop_polygon = geotiff_transforms_handler.map_crop_into_latlng_bounds(
#                                     src_i, crop_meta["transform"], utm_tiles[tile_i])
#
#                                 data_type = crop_meta["dtype"]
#                                 scale_factor = _bit_depth_scale_factor[data_type]
#                                 crop_data = np.squeeze(np.uint8(crop_data * 255. / scale_factor), axis=2)
#                                 crop_mask = np.squeeze(np.uint8((crop_mask!=1) * 255.), axis=2)
#
#                                 mask = Image.fromarray(crop_mask, mode="L")
#                                 image = Image.fromarray(crop_data, mode="L")
#                                 image.putalpha(mask)
#                                 # image.show()
#
#                                 temporary_file = tempfile.NamedTemporaryFile(delete=False, suffix=".PNG")
#                                 image.save(temporary_file.name)
#
#                                 logger.info("Adding to cache: {} the filename {}".format(xyz_band_str, temporary_file.name))
#                                 if xyz_band_str not in self.png_layer_cache:
#                                     self.png_layer_cache[xyz_band_str] = dict(is_complete=False, parts=[])
#                                 self.png_layer_cache[xyz_band_str]["parts"].append(dict(
#                                     polygon_bounds=crop_polygon.to_bounds(),
#                                     png_filename=temporary_file.name,
#                                 ))
#                                 api_utils.simple_cache_set(current_app, 'png_layer_cache', self.png_layer_cache)
#
#             for tile_i in range(len(utm_tiles)):
#                 xyz_str = "{resource}/{zoom}/{x}/{y}/".format(
#                     resource=resource_name, zoom=zoom, x=xy_tiles[tile_i][0], y=xy_tiles[tile_i][1],
#                 ).lower()
#
#                 self.png_layer_cache = api_utils.simple_cache_get(current_app, 'png_layer_cache', {})
#                 if xyz_str in self.png_tile_cache:
#                     continue
#
#                 potential_thread_error_occurred = False
#                 tile_numpy = []
#                 for band in self.bands_to_render:
#                     xyz_band_str = "{resource}/{zoom}/{x}/{y}/{band}/".format(
#                         resource=resource_name, zoom=zoom, x=xy_tiles[tile_i][0], y=xy_tiles[tile_i][1],
#                         band=band,
#                     ).lower()
#
#                     self.png_layer_cache = api_utils.simple_cache_get(current_app, 'png_layer_cache', {})
#                     if xyz_band_str not in self.png_layer_cache:
#                         potential_thread_error_occurred = True
#                         break
#
#                     tile_numpy.append(np.array(Image.open(self.png_layer_cache[xyz_band_str])))
#
#                 if potential_thread_error_occurred or len(tile_numpy) == 0:
#                     continue
#
#                 foreground = np.transpose(np.stack([t[:,:,0] for t in tile_numpy], axis=0), axes=[1,2,0])
#                 mask = np.uint8(255 * np.bitwise_or(*([t[:,:,1]==255 for t in tile_numpy])))
#                 image = Image.fromarray(foreground, mode="RGB")
#                 mask = Image.fromarray(mask, mode="L")
#                 image.putalpha(mask)
#                 image.show()
#
#                 temporary_file = tempfile.NamedTemporaryFile(delete=False, suffix=".PNG")
#                 image.save(temporary_file.name)
#
#                 logger.info("Adding to cache: {} the filename {}".format(xyz_str, temporary_file.name))
#                 self.png_tile_cache[xyz_str] = temporary_file.name
#                 api_utils.simple_cache_set(current_app, 'png_tile_cache', self.png_tile_cache)
#
#                 self.not_on_client_side.append(xyz_str)
#                 api_utils.simple_cache_set(current_app, 'not_on_client_side', self.not_on_client_side)
#
#                 n_tiles_added += 1
