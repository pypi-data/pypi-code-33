"""
    Tools to assist with work request and work order integrations
"""

from ..api_client import ApiClient
from ..rest import ApiException
from ..api import AssetApi
from ..models.assetic3_integration_representations_work_request_spatial_location\
    import  Assetic3IntegrationRepresentationsWorkRequestSpatialLocation
from ..models.assetic3_integration_representations_custom_address\
    import Assetic3IntegrationRepresentationsCustomAddress


class MaintenanceTools(object):
    """
    Class to provide Work Request integration processes
    """

    def __init__(self,api_client=None):
        """
        initialise object
        :param crm: The CRM to integrated to. Currently support "Authority"
        :param api_client: sdk client object, optional
        :param **kwargs: provide any config specific to the CRM
        """
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

        self.logger = api_client.configuration.packagelogger

        self.assetapi = AssetApi()

    def get_location_by_assetguid(self, assetguid):
        """
        Get the address and/or spatial definition for an asset
        :param assetguid: The asset GUID
        :returns:
        """
        try:
            spatial = self.assetapi.asset_search_spatial_information_by_asset_id(
                assetguid)
        except ApiException as e:
            if e.status == 404:
                # no spatial data, but that's ok
                return None
            else:
                msg = "Status {0}, Reason: {1} {2}".format(e.status, e.reason,
                                                           e.body)
                self.logger.error(msg)
                return None, None
        # create address object
        wraddr = Assetic3IntegrationRepresentationsCustomAddress()
        # create spatial location object
        wrsl = Assetic3IntegrationRepresentationsWorkRequestSpatialLocation()

        address = spatial["Data"]["properties"]["AssetPhysicalLocation"]
        if address is not None:
            wraddr.street_number = address["StreetNumber"]
            wraddr.street_address = address["StreetAddress"]
            wraddr.city_suburb = address["CitySuburb"]
            wraddr.state = address["State"]
            wraddr.zip_postcode = address["ZipPostcode"]
            wraddr.country = address["Country"]

        geoms = spatial["Data"]["geometry"]["geometries"]
        for geom in geoms:
            if geom["type"] == "Point":
                wrsl.point_string = "Point({0} {1})".format(
                    str(geom["coordinates"][0]),
                    str(geom["coordinates"][1]))
        return wraddr, wrsl