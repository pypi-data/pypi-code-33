import copy

################################################################################################################
#
#  The DefaultGeoTiffHandler knows how to handle the search into BigQuery, and the cropping of GeoTiffs.
#  Resource data layers that require no special conditions will use this Handler. This Handler will also handle
#  jp2 files (such as Sentinel). So, in that regard, the naming is slightly in error.
#
#  The api_config object is a dictionary of any parameters in which its method may require during processing.
#  For instance, search() uses api_config to place its table_id of metadata.
#
#
# The process method operates on the ImageObjects to convert them from one set of files, the bands, to the packed,
# stacked, cropped, masked, and color_tabled, files. In this regard, the request, a SpacetimeBuilder can be reused
# for the response.

################################################################################################################

class geotiff_search_handler(object):

    def __init__(self, global_objects, logger):
        self._global_objects = global_objects
        self._logger = logger

    def query_resource_meta_with_polygon(self, parameter_values, polygon, query_parameters, meta_search_config):
        table_id = meta_search_config["metadata_table_id"]
        additional_where_conditions = meta_search_config["additional_where_conditions"]
        serverside_type_maps = meta_search_config["serverside_type_maps"]
        parameters_to_use = [q for q in query_parameters if q.name not in meta_search_config["exclude_parameters_from_metadata_search"]]

        where_conditions = [] if additional_where_conditions is None else copy.deepcopy(additional_where_conditions)
        ordered_conditions = []

        # If we use the parameters, we do so by adding to the where conditions. The one exceptions is that if a
        # parameter of type RANGE is given one of the special ORDERED values, e.g., QueryParameters.ORDERED.FIRST.
        # In that case, we solve this by adding a ordered_condition. First
        for q in parameters_to_use:
            if q.is_ordered(parameter_values[q.name]):
                ordered_conditions.append(q.ordered_condition(parameter_values[q.name], serverside_type_maps))
            else:
                where_conditions.append(q.where_conditions(parameter_values[q.name], serverside_type_maps))

        # Polygon Search conditions
        if polygon is not None:
            where_conditions.append("(south_lat <= {value})".format(value=min(polygon.lats())))
            where_conditions.append("(west_lon <= {value})".format(value=min(polygon.lngs())))
            where_conditions.append("(north_lat >= {value})".format(value=max(polygon.lats())))
            where_conditions.append("(east_lon >= {value})".format(value=max(polygon.lngs())))

        where_semicolon, ordered_conditions_string = ";", ""
        if len(ordered_conditions) != 0:
            where_semicolon = ""
            ordered_conditions_string = "ORDER BY {};".format(",".join(ordered_conditions))

        query = """
            #standardSQL
            SELECT *
            FROM `{table_id}`
            WHERE {where_conditions}{where_semicolon}
            {ordered_conditions}
            """.format(
            table_id=table_id,
            where_conditions=" AND ".join(where_conditions),
            where_semicolon=where_semicolon,
            ordered_conditions=ordered_conditions_string
        )

        self._logger.info("Running query for Resource from table {}: {}".format(table_id, query))
        query_job = self._global_objects.bigquery_client()._client.query(query)
        rows = [row for row in query_job]
        if len(ordered_conditions) != 0 and len(rows) != 0:
            rows = [rows[0]]

        self._logger.info("Found {} results (after selecting for ordered conditions.)".format(len(rows)))
        self._logger.debug("Showing up to 10 results.")
        for row in rows[:10]:
            self._logger.debug("Found row: {}".format(row))
        return rows
