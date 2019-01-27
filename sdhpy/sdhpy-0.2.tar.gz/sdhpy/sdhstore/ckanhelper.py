import ckanapi

from sdhpy.errors import CkanAuthError


def get_store_user(apikey, url="https://store.smartdatahub.io"):
    ckan = ckanapi.RemoteCKAN(url, apikey, "Smart Data Hub Python Client")
    current_user = ckan.action.current_user_show()
    if not current_user["user"]:
        raise CkanAuthError("Invalid Store API key provided")
    return current_user

def get_dataset(apikey, name_or_id, url="https://store.smartdatahub.io"):
    ckan = ckanapi.RemoteCKAN(url, apikey, "Smart Data Hub Python Client")
    dataset_object = ckan.action.package_show(id=name_or_id)
    return dataset_object

def get_resource(apikey, id, url="https://store.smartdatahub.io"):
    ckan = ckanapi.RemoteCKAN(url, apikey, "Smart Data Hub Python Client")
    resource_object = ckan.action.resource_show(id=id)
    return resource_object


def get_ckan(apikey, url="https://store.smartdatahub.io"):
    return ckanapi.RemoteCKAN(url, apikey, "Smart Data Hub Python Client")


def search_resource_by_tbl_and_db(apikey, db, tbl, url="https://store.smartdatahub.io"):
    ckan = ckanapi.RemoteCKAN(url, apikey, "Smart Data Hub Python Client")
    resource_object = ckan.action.resource_search(query=["table:"+tbl.lower(), "database:" + db.lower()])
    return resource_object

def search_resources_by_db(apikey, db, url="https://store.smartdatahub.io"):
    ckan = ckanapi.RemoteCKAN(url, apikey, "Smart Data Hub Python Client")
    resource_object = ckan.action.resource_search(query=["database:" + db.lower()])
    return resource_object