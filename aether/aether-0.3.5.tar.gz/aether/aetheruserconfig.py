from aether.base.QueryParameter import QueryParameter, Choice

############################################################################################################
#
# GIS
#
############################################################################################################

_default_projection = "epsg:3857"

############################################################################################################
#
# Services
#
############################################################################################################

_local_hostport = "127.0.0.1:5002"
_default_hostport = "data.runsonaether.com"
_default_protocol = "http://"

_rest_entrypoints = dict(
    SearchResource=dict(entry="/api/v1.0/search/{resource_name}/", method="POST"),
    ClipAndShipResource=dict(entry="/api/v1.0/sky/clip_and_ship/", method="POST"),

    UserAdminInterface=dict(entry="/api/v1.0/sky/user_admin/", method="POST"),
    DataModelData=dict(entry="/api/v1.0/datamodel/data/", method="POST"),

    AppSupportInterface=dict(entry="/api/v1.0/sky/app_support/", method="POST"),
    GatewaySpacetimeBuilder=dict(entry="/api/v1.0/sky/download/", method="POST"),
    SkyApplicationManifest=dict(entry="/api/v1.0/sky/application/", method="POST"),
    SkyFrameworkComponent=dict(entry="/api/v1.0/sky/_sdk/application/{application_name}/", method="POST"),

    EndpointConsumerInterface=dict(entry="/api/v1.0/sky/{uuid}/application/{application_id}/", method="GET"),
)

############################################################################################################
#
# Resources
#
############################################################################################################

reference = dict(
    landsat=dict(
        ULTRA_BLUE      = dict(spatial_resolution_m=30.0),
        BLUE            = dict(spatial_resolution_m=30.0),
        GREEN           = dict(spatial_resolution_m=30.0),
        RED             = dict(spatial_resolution_m=30.0),
        NIR             = dict(spatial_resolution_m=30.0),
        SWIR1           = dict(spatial_resolution_m=30.0),
        SWIR2           = dict(spatial_resolution_m=30.0),
        PANCHROMATIC    = dict(spatial_resolution_m=15.0),
        CIRRUS          = dict(spatial_resolution_m=30.0),
        TIRS1           = dict(spatial_resolution_m=30.0),
        TIRS2           = dict(spatial_resolution_m=30.0),
    ),
    sentinel=dict(
        COASTAL_AEROSOL = dict(spatial_resolution_m=60.0,
                               central_wavelength_um=0.443),
        BLUE            = dict(spatial_resolution_m=10.0,
                               central_wavelength_um=0.490),
        GREEN           = dict(spatial_resolution_m=10.0,
                               central_wavelength_um=0.560),
        RED             = dict(spatial_resolution_m=10.0,
                               central_wavelength_um=0.665),
        VEG_RED_EDGE1   = dict(spatial_resolution_m=20.0,
                               central_wavelength_um=0.705),
        VEG_RED_EDGE2   = dict(spatial_resolution_m=20.0,
                               central_wavelength_um=0.740),
        VEG_RED_EDGE3   = dict(spatial_resolution_m=20.0,
                               central_wavelength_um=0.783),
        NIR             = dict(spatial_resolution_m=10.0,
                               central_wavelength_um=0.842),
        NARROW_NIR      = dict(spatial_resolution_m=20.0,
                               central_wavelength_um=0.865),
        WATER_VAPOR     = dict(spatial_resolution_m=60.0,
                               central_wavelength_um=0.945),
        CIRRUS          = dict(spatial_resolution_m=60.0,
                               central_wavelength_um=1.375),
        SWIR1           = dict(spatial_resolution_m=20.0,
                               central_wavelength_um=1.610),
        SWIR2           = dict(spatial_resolution_m=20.0,
                               central_wavelength_um=2.190)
    ),
)



resources = dict(
    landsat=dict(
        _query_parameters = [
            QueryParameter("cloud_cover", QueryParameter.Type.FLOAT, False, QueryParameter.Collect.RANGE, [0.0, 1.0], "Excludes scenes with Cloud Fractions outside this range.",),
            QueryParameter("wrs_row", QueryParameter.Type.INT, False, QueryParameter.Collect.ONE, -1, "DO NOT USE. WRS2 Descending Row",),
            QueryParameter("wrs_path", QueryParameter.Type.INT, False, QueryParameter.Collect.ONE, -1, "DO NOT USE. WRS2 Descending Path",),
            QueryParameter("date_acquired", QueryParameter.Type.TIMEDATE, False, QueryParameter.Collect.RANGE, ["1900-01-01", "2050-01-01"], "Excludes dates outside this range."),
            QueryParameter("bands", QueryParameter.Type.STRING, False, QueryParameter.Collect.MANY, ["RED", "GREEN", "BLUE"], "Band numbers returned in query.",
                           choice_values=[
                               Choice("ULTRA_BLUE",   description="Approx 0.435 - 0.451 um; B1 Landsat 8,  Not on LandSat 4/5/7"),
                               Choice("BLUE",         description="Approx 0.452 - 0.512 um; B2 Landsat 8,  B1 LandSat 4/5/7"),
                               Choice("GREEN",        description="Approx 0.533 - 0.590 um; B3 Landsat 8,  B2 LandSat 4/5/7"),
                               Choice("RED",          description="Approx 0.636 - 0.673 um; B4 Landsat 8,  B3 LandSat 4/5/7"),
                               Choice("NIR",          description="Approx 0.851 - 0.879 um; B5 Landsat 8,  B4 LandSat 4/5/7"),
                               Choice("SWIR1",        description="Approx 1.566 - 1.651 um; B6 Landsat 8,  B5 LandSat 4/5/7"),
                               Choice("SWIR2",        description="Approx 2.107 - 2.294 um; B7 Landsat 8,  B7 LandSat 4/5/7"),
                               Choice("PANCHROMATIC", description="Approx 0.503 - 0.676 um; B8 Landsat 8,  B8 LandSat 7, Not on Landsat 4/5."),
                               Choice("CIRRUS",       description="Approx 1.363 - 1.384 um; B9 Landsat 8,  Not on LandSat 4/5/7"),
                               Choice("TIRS1",        description="Approx 10.60 - 11.19 um; B10 Landsat 8, B6 LandSat 4/5/7"),
                               Choice("TIRS2",        description="Approx 11.50 - 12.51 um; B11 Landsat 8, Not on LandSat 4/5/7"),
                               Choice("QA",           description="Quality Assurance Band; only available on Collection 01."),
                           ]),
            QueryParameter("spacecraft_id", QueryParameter.Type.STRING, False, QueryParameter.Collect.MANY, ["LANDSAT_7", "LANDSAT_8"], "Spacecraft name: LANDSAT_4 through LANDSAT_8.",
                           choice_values=[
                               Choice("LANDSAT_4", description="LandSat 4 1982-1993,    https://landsat.usgs.gov/what-are-band-designations-landsat-satellites"),
                               Choice("LANDSAT_5", description="LandSat 5 1984-2013,    https://landsat.usgs.gov/what-are-band-designations-landsat-satellites"),
                               Choice("LANDSAT_7", description="LandSat 7 1999-present, https://landsat.usgs.gov/what-are-band-designations-landsat-satellites"),
                               Choice("LANDSAT_8", description="LandSat 8 2013-present, https://landsat.usgs.gov/what-are-band-designations-landsat-satellites"),
                            ]),
            QueryParameter("collection_number", QueryParameter.Type.STRING, False, QueryParameter.Collect.ONE, "01", "Collection number: either 'PRE' or '01'.",
                           choice_values=[
                               Choice("PRE", description="Calibrated, georectified, atmosphere corrected imagery: https://landsat.usgs.gov/landsat-level-1-standard-data-products"),
                               Choice("01",  description="Raw imagery not atmosphere corrected, minimized calibration."),
                            ]),
        ],
    ),

    sentinel=dict(
        _query_parameters = [
            QueryParameter("cloud_cover", QueryParameter.Type.FLOAT, False, QueryParameter.Collect.RANGE, [0.0, 1.0], "Excludes scenes with Cloud Fractions outside this range."),
            QueryParameter("date_acquired", QueryParameter.Type.TIMEDATE, False, QueryParameter.Collect.RANGE, ["1900-01-01", "2050-01-01"], "Excludes dates outside this range."),
            QueryParameter("bands", QueryParameter.Type.STRING, False, QueryParameter.Collect.MANY, ["BLUE", "GREEN", "RED"], "Band numbers returned in query, B01 through B12, or B8A.",
                           choice_values=[
                               Choice("COASTAL_AEROSOL", description="Approx 0.433 - 0.453 um; Resolution 60m"),
                               Choice("BLUE",            description="Approx 0.458 - 0.522 um; Resolution 10m"),
                               Choice("GREEN",           description="Approx 0.542 - 0.578 um; Resolution 10m"),
                               Choice("RED",             description="Approx 0.650 - 0.680 um; Resolution 10m"),
                               Choice("VEG_RED_EDGE1",   description="Approx 0.697 - 0.712 um; Resolution 20m"),
                               Choice("VEG_RED_EDGE2",   description="Approx 0.732 - 0.747 um; Resolution 20m"),
                               Choice("VEG_RED_EDGE3",   description="Approx 0.773 - 0.793 um; Resolution 20m"),
                               Choice("NIR",             description="Approx 0.784 - 0.899 um; Resolution 10m"),
                               Choice("NARROW_NIR",      description="Approx 0.855 - 0.875 um; Resolution 20m"),
                               Choice("WATER_VAPOR",     description="Approx 0.935 - 0.965 um; Resolution 60m"),
                               Choice("CIRRUS",          description="Approx 1.365 - 1.385 um; Resolution 60m"),
                               Choice("SWIR1",           description="Approx 1.565 - 1.655 um; Resolution 20m"),
                               Choice("SWIR2",           description="Approx 2.100 - 2.280 um; Resolution 20m"),
                           ]),
        ],
    ),

    cropland_data_layer=dict(
        _query_parameters = [
            QueryParameter("year", QueryParameter.Type.STRING, True, QueryParameter.Collect.MANY, ["2016"], "Calendar Year of the Cropland Data Layer (published in January of the following year).",
                           choice_values=[
                               Choice("2016", description="Resolution 30m; Continential US"),
                               Choice("2015", description="Resolution 30m; Continential US"),
                               Choice("2014", description="Resolution 30m; Continential US"),
                               Choice("2013", description="Resolution 30m; Continential US"),
                               Choice("2012", description="Resolution 30m; Continential US"),
                               Choice("2011", description="Resolution 30m; Continential US"),
                               Choice("2010", description="Resolution 30m; Continential US"),
                               Choice("2009", description="Resolution 56m; Continential US"),
                               Choice("2008", description="Resolution 56m; Limited coverage (partial continental US)."),
                           ]),
        ],
    ),
)

# for q in resources["cropland_data_layer"]["_query_parameters"]:
#     print q
