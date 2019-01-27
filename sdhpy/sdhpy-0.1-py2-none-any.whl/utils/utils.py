from sdhpy.sdhstore.ckanhelper import get_dataset, get_resource, search_resource_by_tbl_and_db
from urllib.parse import urlparse
import os

def get_dataset_and_resource_id(store_apikey, **kwargs):
    resource_url = kwargs.get("resource_url", None)
    db_and_tbl = kwargs.get("db_and_tbl", None)
    dataset = kwargs.get("dataset", None)
    dataset_id = kwargs.get("dataset_id", None)
    resource_id = kwargs.get("resource_id", None)

    if (not dataset) and (not resource_id):
        if dataset_id:
            dataset = get_dataset(store_apikey, dataset_id)
            if not resource_id:
                raise ValueError("If dataset_id is specified then also resource_id is required")
        elif resource_id:
            resource = get_resource(store_apikey, resource_id)
            dataset_id = resource["package_id"]
            dataset = get_dataset(store_apikey, dataset_id)
        elif resource_url:
            parsed_url = urlparse(resource_url)
            path = parsed_url.path
            splitted_path = os.path.split(path)
            resource_id = splitted_path[1]
            resource = get_resource(store_apikey, resource_id)
            dataset_id = resource["package_id"]
            dataset = get_dataset(store_apikey, dataset_id)
        elif db_and_tbl:
            db_and_tbl_splitted = db_and_tbl.split(".")
            db = db_and_tbl_splitted[0]
            tbl = db_and_tbl_splitted[1]
            resource_results = search_resource_by_tbl_and_db(store_apikey, db, tbl)
            resource_id = resource_results["results"][0]["id"]
            dataset_id = resource_results["results"][0]["package_id"]
            dataset = get_dataset(store_apikey, dataset_id)
    if not dataset and resource_id:
        raise ValueError("Could not lookup dataset and resource id with specified identifiers")
    else:
        return dataset, resource_id
