# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.


from cloudvolumes.resource import Resource, Collection


class Provider(Resource):
    pass


class ProviderList(Collection):
    resource = Provider
    resource_type = "providers"

    def __init__(self, client):
        self._client = client


class CVRegion(Resource):
    pass


class CVRegionList(Collection):
    resource = CVRegion
    resource_type = "cv_regions"

    def __init__(self, client):
        self._client = client


class Region(Resource):
    pass


class RegionList(Collection):
    resource = Region
    resource_type = "regions"

    def __init__(self, client):
        self._client = client
