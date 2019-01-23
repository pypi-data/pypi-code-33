import abc

from flask_restful import Resource, reqparse, request
from aether_shared.utilities.api_utils import api_utils
from aether.dataobjects.AEPolygon import AEPolygon

##################################################################################################################
#
# The SearchAPIResource is the basis for all search operations, i.e., searching for imagery or other data layers
# that are within a polygon. More generally, a SearchAPI is one which operates on meta data, and so is not expected
# to result in transfer of large data files across the network. In fact, most often, the SearchAPI processes will
# all perform direct queries into BigQuery, along with other data format or massaging. For example, the Cropland
# Data Layer requires downloading special files (its color tables) when downloaded elsewhere. For this reasons,
# the Cropland Data Layer resource has additional functionality in its operation.
#
# The SearchAPIResource is initialized with:
#  1) The global objects, which handles all cloud mediated communication and data transfers.
#  2) The QueryParameters array describing what additional query parameters this data resource in addition to usual
#      geoTiff query parameters.
#  3) The api_classname which has the .search() method which handles the actual URI processing of the request.
#  4) The api_parameters, a dictionary required at the initialization of the api_classname.
#
# The SearchAPIResource expects REST URI call, and expects one polygon in every URI.
#
##################################################################################################################

class SearchResourceResourceBase(Resource):

    def __init__(self, global_objects, query_parameters, logger):
        self._global_objects = global_objects
        self._query_parameters = query_parameters
        self._logger = logger

    def _bands_in_serverside_terms(self, resource_name, bands):
        return [self._band_replacement[resource_name.upper()][b.upper()] for b in bands]

    def validate_query_values(self, query_parameters, parameter_values):
        for p in query_parameters:
            if p.name not in parameter_values:
                return False, "Request missing value for parameter {}".format(p.name)
            if not p.is_valid_value(parameter_values[p.name]):
                return False, "Request has invalid value for parameter {}: {}".format(p.name, parameter_values[p.name])
        return True, None

    @abc.abstractmethod
    def search(self, parameter_values, polygon):
        pass

    def post(self):
        parser = reqparse.RequestParser(bundle_errors=True)
        parser.add_argument('uuid', type=str, required=True, location='json')
        parser.add_argument("polygon", type=list, required=True, action="append", location='json')
        for q in self._query_parameters:
            q.add_reqparse_arg(parser, 'json')
        args = parser.parse_args()

        if not self._global_objects.authenticator().is_authorized_user(uid=args["uuid"]):
            return api_utils.log_and_return_status(
                "Unauthorized UUID {}".format(args["uuid"]), 401, request, self._logger)

        try:
            polygon = AEPolygon().from_latlngs(args["polygon"])
        except Exception:
            return api_utils.log_and_return_status(
                "Request has incorrectly formed polygon.", 401, request, self._logger, exc_info=True)

        is_valid, msg = self.validate_query_values(self._query_parameters, args)
        if not is_valid:
            return api_utils.log_and_return_status(msg, 401, request, self._logger)

        try:
            response, code = self.search(args, polygon)
            return api_utils.log_and_return_status(response, code, request, self._logger)
        except Exception:
            return api_utils.log_and_return_status(
                "Query failed during search method.", 500, request, self._logger, exc_info=True)
