import json
import time
import tempfile
import rasterio
import six
import aether_shared.sharedconfig as cfg
from google.cloud import bigquery
from aether_shared.utilities.geometry_utils import geometry_utils
from aether.dataobjects.AEPolygon import AEPolygon
from aether.base.QueryParameter import QueryParameter
from aether_shared.api_global_objects import api_global_objects
from aether_shared.utilities.geotiff_utils import geotiff_utils
from PIL import Image
import numpy as np
import math, random
from scipy.misc import imresize

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResourceRow():
    def __init__(self, parameters, filestub, associated_filestubs, id, bounds=None):
        self.parameters = parameters
        self.filestub = filestub
        self.associated_filestubs = associated_filestubs
        self.id = id
        self.bounds = bounds

class resource_manager(object):

    def __init__(self, global_objects):
        self._global_objects = global_objects

    @staticmethod
    def _resource_generic_geotiff_schema():
        _SCHEMA = [
            bigquery.SchemaField('resource_id', 'STRING', mode='required', description="Unique 32 digit alphanumeric"),
            bigquery.SchemaField('resource_name', 'STRING', mode='required', description="Resource name"),
            bigquery.SchemaField('resource_filestub', 'STRING', mode='required', description="Location of file stub"),
            bigquery.SchemaField('resource_associated_filestubs', 'STRING', mode='required', description="Addition files associated with this resource, e.g., color tables or masks, as json string"),
            #bigquery.SchemaField('total_size', 'INTEGER', mode='required', description="The total size of this scene in bytes."),
            bigquery.SchemaField('count', 'INTEGER', mode='required', description="Quantity of bands, e.g., 1"),
            bigquery.SchemaField('crs', 'STRING', mode='required', description="Coordinate Reference System constructor dictionary as string, e.g., {'init': u'epsg:5070'}"),
            bigquery.SchemaField('dtype', 'STRING', mode='required', description="Datatype of bands as a python dtype, e.g., 'uint8'"),
            bigquery.SchemaField('driver', 'STRING', mode='required', description="GeoTiff driver, e.g., 'GTiff'"),
            bigquery.SchemaField('transform', 'STRING', mode='required', description="GeoTiff transform tuple in order (a, b, c, d, e, f) as string."),
            bigquery.SchemaField('height', 'INTEGER', mode='required', description="Height of image, dimension 1 for [n_d1, n_d2, n_bands]"),
            bigquery.SchemaField('width', 'INTEGER', mode='required', description="Width of image, dimension 0 for [n_d1, n_d2, n_bands]"),
            bigquery.SchemaField('nodata', 'STRING', mode='required', description="Contents of the nodata field as json."),
            bigquery.SchemaField('north_lat', 'FLOAT', mode='required', description="The northern latitude of the bounding box of this scene."),
            bigquery.SchemaField('south_lat', 'FLOAT', mode='required', description="The southern latitude of the bounding box of this scene."),
            bigquery.SchemaField('west_lon', 'FLOAT', mode='required', description="The western longitude of the bounding box of this scene."),
            bigquery.SchemaField('east_lon', 'FLOAT', mode='required', description="The eastern longitude of the bounding box of this scene."),
        ]
        return _SCHEMA

    @staticmethod
    def _resource_generic_geotiff_to_schema_values(raster):
        values = dict(
            count=raster.meta["count"],
            crs=str(raster.meta["crs"].data),
            dtype=str(raster.meta["dtype"]),
            transform=str(raster.meta["transform"]),
            height=raster.meta["height"],
            width=raster.meta["width"],
            nodata=str(raster.meta["nodata"]),
            driver=str(raster.meta["driver"])
        )
        return values


    ###################################################################################################################
    #
    # The following methods manage the creation and upload of Resource Data Files to BigQuery.
    #
    # They are intended to be used once at the onset of a new Resource layer creation. For example, the Cropland Data
    #  Layer was added to the BigQuery meta dataset using the following code:
    #
    # This code defines the resource as having one query specification, 'year', which is an TIMEDATE form, and which
    # is_required=True. This code creates a new BigQuery table for this resource, using the generic geotiff schema and
    # adding a schema column for year. This allows a user to query for this additional parameter, for example, during
    # polygon extraction.
    #
    # As of December 28, 2017
    #
    #     resource_name = "cropland_data_layer"
    #
    #     query_parameters = [
    #         QueryParameter("year", QueryParameter.Type.TIMEDATE, True, QueryParameter.Collect.MANY, ["2016"], "Calendar Year of the Cropland Data Layer (published in January of the following year)."),
    #     ]
    #
    #     stub_location_format = "gs://ae_data_platform_resources/cropland_data_layer/{year}/cropland_data_layer_{year}.tif"
    #     associated_stubs_format = ["gs://ae_data_platform_resources/cropland_data_layer/{year}/cropland_data_layer_{year}.tif.vat.dbf"]
    #
    #     resource_rows = []
    #     for year in ["2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016"]:
    #         parameters=dict(year=year)
    #         resource_rows.append(ResourceRow(
    #             parameters=parameters,
    #             filestub=stub_location_format.format(**parameters),
    #             associated_filestubs=[s.format(**parameters) for s in associated_stubs_format],
    #             id = self._global_objects.filemanager()._alphanumeric_id_generator(),
    #         ))
    # resource_manager(global_objects).create_new_resource(resource_name, query_parameters)
    # resource_manager(global_objects).add_row_to_resource(resource_name, resource_name, resource_rows, query_parameters)
    #
    # This code inserts the raster meta data from filestub into the BigQuery database, while also including the
    # searchable parameter 'year' to this particular file resource. Associated_filestubs are other files
    # associated with the geotiff, such as color tables or masks, so that downstream clients can make use of them.
    # The processes use stubs, so the resource location can be on the Google Cloud Storage buckets as gs:// urls,
    # or urls accessible via https://. In principal, a user could host their own resources behind a user:// url as
    # well.
    #
    ###################################################################################################################

    def create_new_resource(self, table_name, query_parameters):
        # Ensure that the Dataset exists in BigQuery that will hold the newly created table.
        dataset = self._global_objects.bigquery_client()._client.dataset(cfg._default_resource_metadata_dataset_name)
        if dataset is None:
            logger.error('Dataset {} does not exist.'.format(cfg._default_resource_metadata_dataset_name))
            return

        # Generate the Schema from defaults and query_parameters
        schema = self._resource_generic_geotiff_schema()
        for q in query_parameters:
            mode = "required" if q.is_required else "nullable"
            type = q.bigquery_query_type_map(q.type)
            schema.append(bigquery.SchemaField(q.name, type, mode=mode, description=q.description))

        # Create the table in BigQuery
        table_ref = dataset.table(table_name)
        table = bigquery.Table(table_ref)
        table.schema = schema

        if self._global_objects.bigquery_client().table_exists(table):
            logger.info('Table already exists: {}.'.format(table_name))
            return

        self._global_objects.bigquery_client().create_table(table)
        logger.info('Created Resource at Table name: {}.'.format(table_name))

    def add_row_to_resource(self, table_name, resource_name, resource_rows, query_parameters):
        dataset = self._global_objects.bigquery_client()._client.dataset(cfg._default_resource_metadata_dataset_name)
        table_ref = dataset.table(table_name)

        # Create a CSV as String from the ResourceRows
        # The headers include the geotiff standard headers, plus any included in the QueryParameters
        csv = ""
        headers = [s._name for s in self._resource_generic_geotiff_schema()]
        [headers.append(q.name) for q in query_parameters]
        csv += ",".join([self._escape_string(h) for h in headers]) + "\n"

        # Needs to get the resource meta data.
        for row in resource_rows:
            file_obj = self._global_objects.filemanager().retrieve_stub(row.filestub)
            with rasterio.open(file_obj.name) as src:
                values = self._resource_generic_geotiff_to_schema_values(src)
                values.update(dict(
                    resource_name=resource_name,
                    resource_id=row.id,
                    resource_filestub=row.filestub,
                    resource_associated_filestubs=str(row.associated_filestubs),
                ))

                # Bounds are either explicitly given using ResourceRow, or inferred from the raster.
                # To explicitly provide them will be more exact, and less likely to accidentally use bounds that include
                # additional mask.
                if row.bounds is None:
                    values.update(geometry_utils.transform_to_latlng(
                        src.meta["crs"], [AEPolygon().from_bounds(src.bounds)])[0].to_latlng_bounds())
                else:
                    values.update(row.bounds)

                for p in query_parameters:
                    if p.is_required or (not p.is_required and p.name in row.parameters.keys()):
                        values[p.name] = row.parameters[p.name]
                    else:
                        values[p.name] = ""
                logger.info("Adding Resource Row with meta dataset values: {}".format(values))
                line = ",".join([self._escape_string(values[h]) for h in headers])
                csv += line + "\n"
        csv_file = six.BytesIO(csv)

        job_config = bigquery.LoadJobConfig()
        job_config.source_format = 'CSV'
        job_config.skip_leading_rows = 1
        job = self._global_objects.bigquery_client().load_table_from_file(csv_file, table_ref, job_config=job_config)
        job.result()
        logger.info('Loaded {} rows into {}:{}.'.format(job.output_rows, cfg._default_resource_metadata_dataset_name, resource_name))

    @staticmethod
    def _escape_string(s):
        return json.dumps(s)

    ###################################################################################################################
    #
    # Examples for the Tiling and Uploading of a Large Resource: Cropland Data Layer
    #
    ###################################################################################################################

    def _tile_large_resource(self):
        resource_name = "cropland_data_layer"
        years = ["2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016"]

        # This information could be retrieved automatically from the BigQuery table for the original resource.
        query_parameters = [
            QueryParameter("year", QueryParameter.Type.TIMEDATE, True, QueryParameter.Collect.MANY, ["2016"], "Calendar Year of the Cropland Data Layer (published in January of the following year)."),
        ]

        stub_location_format = "gs://ae_data_platform_resources/cropland_data_layer/{year}/cropland_data_layer_{year}.tif"
        associated_stubs_format = ["gs://ae_data_platform_resources/cropland_data_layer/{year}/cropland_data_layer_{year}.tif.vat.dbf"]

        # Preliminary information for tiling and creating of temporary "tiled" BigQuery table.
        tiled_stub_format = \
            "gs://ae_data_platform_resources/cropland_data_layer/{year}/cropland_data_layer_{year}_lat_{s}_to_{n}_lng_{w}_to_{e}.tif"
        tiled_table_name = resource_name + "_tiled"
        self.create_new_resource(tiled_table_name, query_parameters)

        # Parameters for reporting.
        summary_image_scale = 100.0

        for year in years:
            logger.info("YEAR: {}".format(year))
            parameter_values=dict(year=year)

            stub = stub_location_format.format(**parameter_values)
            file_obj = self._global_objects.filemanager().retrieve_stub(stub)
            associated_stubs = [s.format(**parameter_values) for s in associated_stubs_format]

            start_time = time.time()
            with rasterio.open(file_obj.name) as src:
                resource_polygon = geometry_utils.transform_geotiff_meta_bounds_into_latlng(src.meta["crs"], src.bounds)
                bounds = resource_polygon.to_bounds() # (left, bottom, right, top)

                summary_map = np.zeros(
                    (int(src.height / summary_image_scale), int(src.width / summary_image_scale)), dtype=np.uint8)

                logger.info("Resource extent: Lat {} to {}, Lng {} to {}".format(bounds[1], bounds[3], bounds[0], bounds[2]))

                lat_range = range(int(math.floor(bounds[1])), int(math.floor(bounds[3])) + 1)
                lng_range = range(int(math.floor(bounds[0])), int(math.floor(bounds[2])) + 1)
                logger.info("Creating 1 degree slices:")
                logger.info("Southern Latitudes: {}".format(lat_range))
                logger.info("Western Longitudes: {}".format(lng_range))

                resource_rows = []
                for lat_i in range(0, len(lat_range)):
                    for lng_i in range(0, len(lng_range)):
                        w = lng_range[lng_i]
                        s = lat_range[lat_i]
                        e = lng_range[lng_i] + 1
                        n = lat_range[lat_i] + 1
                        print("{} and {}, accumulated time (min) {}".format(w, n, time.time()-start_time))
                        polygon = AEPolygon().from_bounds((w, s, e, n))
                        utm_polygon = geometry_utils.transform_latlng_to_pixels(src.meta["crs"], [polygon])[0]
                        band_data, band_mask, band_meta, window, in_crop_pixels = \
                            geotiff_utils.extract_polygon_from_tiff(src, utm_polygon, inscribed_polygons_only=True)

                        if window is None:
                            logger.info("{} to {}, {} to {}: Window is None (outside Resource bounds).".format(w, e, s, n))
                            continue

                        pixels = AEPolygon().from_lats_and_lngs(
                            lats=[p + window[1][0] for p in in_crop_pixels.lats()],
                            lngs=[p + window[0][0] for p in in_crop_pixels.lngs()],
                        )

                        utm_pixels = []
                        for point in pixels.lnglats():
                            y, x, _, _ = src.window_bounds(((point[0], point[0]), (point[1], point[1])))
                            utm_pixels.append([x, y])
                        utm_pixels_polygon = AEPolygon().from_latlngs(utm_pixels)
                        bounds_polygon = geometry_utils.transform_to_latlng(src.meta["crs"], [utm_pixels_polygon])[0]

                        logger.info("{} to {}, {} to {}: Window is {}.".format(w, e, s, n, window))

                        # Create a temporary file with the band_data and band_mask fused.
                        # Upload that to the resources bucket
                        destination_stub = tiled_stub_format.format(year=year, n=n, s=s, w=w, e=e)
                        temporary_file = tempfile.NamedTemporaryFile(delete=True)
                        geotiff_utils.write_geotiff_components_to_tiff(
                            band_data, band_mask, band_meta, temporary_file.name, color_tables=None)

                        self._global_objects.filemanager().upload_stub(temporary_file, destination_stub)

                        # Create the resource row for the BigQuery entry.
                        parameters=dict(year=year)
                        resource_rows.append(ResourceRow(
                            parameters=parameters,
                            filestub=destination_stub,
                            associated_filestubs=associated_stubs,
                            id = self._global_objects.filemanager()._alphanumeric_id_generator(),
                            bounds=bounds_polygon.to_latlng_bounds(),
                        ))

                        # Generate summary map
                        tile_shape = summary_map[
                                     int(window[0][0]/summary_image_scale):int(window[0][1]/summary_image_scale),
                                     int(window[1][0]/summary_image_scale):int(window[1][1]/summary_image_scale)].shape

                        if tile_shape[0] != 0 and tile_shape[1] != 0:
                            image_rescaled = imresize(band_data[:,:,0], tile_shape, interp='nearest', mode=None)
                            mask_rescaled = np.array(imresize(band_mask, tile_shape, interp='nearest', mode=None), dtype=bool)
                            logger.info("Rescale tile: Median: {}, Sum {}.".format(np.median(image_rescaled), np.sum(image_rescaled)))

                            summary_map[
                            int(window[0][0]/summary_image_scale):int(window[0][1]/summary_image_scale),
                            int(window[1][0]/summary_image_scale):int(window[1][1]/summary_image_scale)][mask_rescaled] = image_rescaled[mask_rescaled]

                Image.fromarray(summary_map, mode="L").save("{}_{}.jpg".format(year,time.time()-start_time))
                print("Done accumulated time (sec) {}".format(time.time()-start_time))
                self.add_row_to_resource(tiled_table_name, resource_name, resource_rows, query_parameters)


    def _test_tiled_resource(self):
        import aether as ae
        years = ["2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016"]

        n_tests = 10

        ae.SessionConfig.getInstance().uuid = "W30yqP7xHgf1kBAghBSyVG8B6Xl1"
        ae.SessionConfig.getInstance()._switch_service_locality(to_local=True)

        for i in range(n_tests):
            logger.info("Running Test {}".format(i))

            year = random.choice(years)
            query_parameters = dict(year=year)

            # Lat Range: 23-48; Lng range -122-69
            lat = random.choice(range(24, 47))
            lng = random.choice(range(-121, -68))
            coordinates = [[lat + .743454, lng + .7003187],
                            [lat + .943454, lng + .7003187],
                            [lat + .943454, lng + .50031870000001],
                            [lat + .743454, lng + .50031870000001],
                            [lat + .743454, lng + .7003187]]
            polygon = AEPolygon().from_latlngs(coordinates)
            logger.info("Year {} Using {}".format(year, coordinates))

            resource_name = "cropland_data_layer_tiled"
            spacetime_builder = ae.Resource(resource_name).search(polygon, query_parameters)
            spacetime_builder = ae.Sky().crop(spacetime_builder)
            spacetime = ae.Sky().download(spacetime_builder)
            tiled = ae.Spacetime.from_pb(spacetime)

            resource_name = "cropland_data_layer"
            spacetime_builder = ae.Resource(resource_name).search(polygon, query_parameters)
            spacetime_builder = ae.Sky().crop(spacetime_builder)
            spacetime = ae.Sky().download(spacetime_builder)
            original = ae.Spacetime.from_pb(spacetime)

            assert tiled.as_numpy().shape == original.as_numpy().shape
            assert np.sum(tiled.as_numpy() != original.as_numpy()) == 0

# resource_manager(api_global_objects())._tile_large_resource()
# resource_manager(api_global_objects())._test_tiled_resource()