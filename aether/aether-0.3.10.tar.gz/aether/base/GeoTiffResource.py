
##################################################################################################
#
# The GeoTiffResource breaks slightly from the Inversion of Control paradigm for constructing
# analytics and their relationships with resources. I.e., search is in theory a meta analytic
# that operates on the resource.
#
# Instead this Resource object provides common user-expected methods that link to whatever way
# the analytics are implemented. This simplifies the user experience and makes it familiar.
#
##################################################################################################
import aether as ae

class GeoTiffResource(object):
    """A :py:class:`~base.GeoTiffResource.GeoTiffResource` is the base class for an imagery-like geospatial resource, named after the common format type.

    This class operates as an interface for information and operations against imagery-like resources, for example,
    resource-specific parameters that can be searched against, and the search operation.

    See also: :py:class:`~base.QueryParameter.QueryParameter`.
    """

    def __init__(self, sky, resource_name, arguments):
        self._resource_name = resource_name
        self._sky = sky
        self._query_parameters = arguments["_query_parameters"]

    def QueryParameters(self):
        """Lists the Resource-specific associated :py:class:`~base.QueryParameter.QueryParameter` which can be searched against."""
        return self._query_parameters

    def search(self, polygon, query_parameters):
        """Searches for timestamps and data of this Resource that matches the query_parameters values. Identical to the search method on the :py:class:`~Sky.Sky` object."""
        return self._sky.search(self._resource_name, polygon, query_parameters)
