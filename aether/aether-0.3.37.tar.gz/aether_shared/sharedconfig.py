
########################################################
# Management
########################################################

_project_id = 'aether-185123'

########################################################
# Firebase Management
########################################################

_user_quotas_collections = "user_quotas"

_application_collection = "appsupport_applications"

_user_datamodel_collection = "user_datamodel_collections"
_valid_data_model_types = [ "AEPolygon" ]


########################################################
# Filesystem management Resources
########################################################

_default_resource_metadata_dataset_name = 'ae_data_platform_resource_metadata_dataset'


########################################################
# Filesystem management for universal filemanager
########################################################

_local_filesystem_directory = "data/cloud_storage/"

_cloud_filesystem_resource_bucket = "ae_data_platform_resources"
_cloud_filesystem_user_bucket = "ae_platform_user_responses"

max_disk_cache_size_gb = 5.0
use_disk_cache = True
use_search_local_for_urls = False
max_time_before_expiration_s = 1.0 * 60 * 60