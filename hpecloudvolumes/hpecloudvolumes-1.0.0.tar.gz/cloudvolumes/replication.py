# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.


from cloudvolumes.resource import Resource, Collection
from cloudvolumes.cloud_volumes import CloudVolume, CloudVolumeList
from cloudvolumes.regions import Region, CVRegion


class ReplicaSnapshot(Resource):
    def __init__(self, id, replica_volume, attrs=None, client=None, collection=None):
        super().__init__(id, attrs, client, collection)
        self.replica_volume = replica_volume

    def clone(self, name, region, iops=None, private_cloud=None, existing_cloud_subnet=None, private_cloud_resource_group=None,
              schedule=None, retention=None, cloud_account_id=None):
        obj = self._client.post_replication_stores_ident_replica_volumes_vol_ref_clone(
            self.replica_volume.replication_store.id,
            self.replica_volume.id,
            name,
            self.id,
            region.id if isinstance(region, Region) else region,
            iops=iops,
            private_cloud=private_cloud,
            existing_cloud_subnet=existing_cloud_subnet,
            private_cloud_resource_group=private_cloud_resource_group,
            schedule=schedule,
            retention=retention,
            cloud_account_id=cloud_account_id
        )

        return CloudVolume(obj['id'], obj['attributes'], client=self._client, collection=CloudVolumeList(self._client))

    def delete(self):
        self._client.delete_replication_stores_ident_replica_volumes_vol_ref_snapshots_snapshot_ref(
            self.replica_volume.replication_store.id,
            self.replica_volume.id,
            self.id
        )


class ReplicaSnapshotList(Collection):
    resource = ReplicaSnapshot
    resource_type = "replica_snapshots"

    def __init__(self, replica_volume, client=None):
        self.replica_volume = replica_volume
        self._client = client

    def get(self, id):
        raise NotImplementedError()

    def list(self, filters=None):
        return [ReplicaSnapshot(snap['id'], self.replica_volume, snap['attributes'], self._client, self)
                for snap in self._client.get_replication_stores_ident_replica_volumes_vol_ref_snapshots(
                    self.replica_volume.replication_store.id,
                    self.replica_volume.id,
                    filters=filters
                )]


class ReplicaVolume(Resource):
    def __init__(self, id, replication_store, attrs=None, client=None, collection=None, replica_volume_collection=None):
        super().__init__(id, attrs, client, collection)
        self.replication_store = replication_store
        self._replica_volume_collection = replica_volume_collection

    @property
    def replica_volume_collection(self):
        if self._replica_volume_collection is None:
            self.reload()
            self._replica_volume_collection = ReplicaVolumeCollection(
                self.attrs['replica_volume_collection']['id'],
                self.replication_store,
                self.attrs['replica_volume_collection'],
                self._client,
                ReplicaVolumeCollectionList(self.replication_store, self._client)
            )

        return self._replica_volume_collection

    @property
    def snapshots(self):
        return ReplicaSnapshotList(self, self._client).list()

    @property
    def metrics(self):
        return self._client.get_replication_stores_ident_replica_volumes_vol_ref_metrics(self.replication_store.id, self.id)

    def delete(self):
        self._client.delete_replication_stores_ident_replica_volumes_vol_ref(self.replication_store.id, self.id)

    def convert(self, name, region, private_cloud, existing_cloud_subnet, iops=None, schedule=None, retention=None,
                private_cloud_resource_group=None, cloud_account_id=None):
        obj = self._client.post_replication_stores_ident_replica_volumes_vol_ref_convert(
            self.replication_store.id,
            self.id,
            name,
            region.id if isinstance(region, Region) else region,
            private_cloud,
            existing_cloud_subnet,
            iops=iops,
            schedule=schedule,
            retention=retention,
            private_cloud_resource_group=private_cloud_resource_group,
            cloud_account_id=cloud_account_id,
        )
        return CloudVolume(obj['id'], obj['attributes'], client=self._client, collection=CloudVolumeList(self._client))


class ReplicaVolumeList(Collection):
    resource = ReplicaVolume
    resource_type = "replica_volumes"

    def __init__(self, replication_store=None, client=None):
        self.replication_store = replication_store
        self._client = client

    def get(self, id):
        obj = self._client.get_replication_stores_ident_replica_volumes_vol_ref(self.replication_store.id, id)
        return ReplicaVolume(obj['id'], self.replication_store, obj['attributes'], self._client, self)

    def list(self, filters=None):
        if self.replication_store is None:
            return [ReplicaVolume(
                        vol['id'],
                        ReplicationStore(
                            vol['attributes']['replication_store']['id'],
                            {'name': vol['attributes']['replication_store']['name']},
                            self._client,
                            self
                        ),
                        vol['attributes'],
                        self._client,
                        self
                    )
                    for vol in self._client.get_replica_volumes(filters=filters)]
        else:
            return [ReplicaVolume(vol['id'], self.replication_store, vol['attributes'], self._client, self)
                    for vol in self._client.get_replication_stores_ident_replica_volumes(self.replication_store.id, filters=filters)]


class ReplicaVolumeCollection(Resource):
    def __init__(self, id, replication_store, attrs=None, client=None, collection=None):
        super().__init__(id, attrs, client, collection)
        self.replication_store = replication_store

    @property
    def replica_volumes(self):
        vols = ReplicaVolumeList(self, self._client)
        vols.replication_store = self.replication_store
        return vols.list()

    def delete(self):
        self._client.delete_replication_stores_ident_replica_volume_collections_volcoll_ref(self.replication_store.id, self.id)

    def set_replication_partnership(self, replication_partnership):
        obj = self._client.patch_replication_stores_ident_replica_volume_collections_volcoll_ref(
            self,
            self.replication_store.id,
            self.id,
            replication_partnership.id if isinstance(replication_partnership, ReplicationPartnership) else replication_partnership,
            self.attrs['replication_direction']
        )

        self.attrs = obj['attributes']

    def set_replication_direction(self, replication_direction, replication_partnership=None):
        if replication_direction not in ['stopped', 'incoming', 'outgoing']:
            raise ValueError('Unknown replication_direction')

        if replication_direction in ['incoming', 'outgoing']:
            if replication_partnership is None:
                raise ValueError("replication_partnership is required when setting direction to 'incoming' or 'outgoing'")

        obj = self._client.patch_replication_stores_ident_replica_volume_collections_volcoll_ref(
            self,
            self.replication_store.id,
            self.id,
            replication_partnership.id if isinstance(replication_partnership, ReplicationPartnership) else replication_partnership,
            replication_direction
        )

        self.attrs = obj['attributes']


class ReplicaVolumeCollectionList(Collection):
    resource = ReplicaVolumeCollection
    resource_type = "replica_volume_collections"

    def __init__(self, replication_store, client=None):
        self.replication_store = replication_store
        self._client = client

    def get(self, id):
        obj = self._client.get_replication_stores_ident_replica_volume_collections_volcoll_ref(self.replication_store.id, id)
        return ReplicaVolumeCollection(obj['id'], self.replication_store, obj['attributes'], self._client, self)

    def list(self, filters=None):
        return [ReplicaVolumeCollection(vc['id'], self.replication_store, vc['attributes'], self._client, self)
                for vc in self._client.get_replication_stores_ident_replica_volume_collections(self.replication_store.id, filters=filters)]


class ReplicationStore(Resource):

    @property
    def replica_volumes(self):
        return ReplicaVolumeList(replication_store=self, client=self._client).list()

    @property
    def replica_volume_collections(self):
        return ReplicaVolumeCollectionList(replication_store=self, client=self._client).list()

    @property
    def replication_partnerships(self):
        if 'replication_partnerships' not in self.attrs:
            self.reload()

        return [ReplicationPartnership(p['id'], p, self._client, ReplicationPartnershipList(self._client))
                for p in self.attrs['replication_partnerships']]

    @property
    def onprem_replication_partners(self):
        if 'replication_partnerships' not in self.attrs:
            self.reload()

        return [OnPremReplicationPartner(
                    p['onprem_replication_partner']['id'],
                    p['onprem_replication_partner'],
                    self._client, OnPremReplicationPartnerList(self._client)
                ) for p in self.attrs['replication_partnerships']]

    def create(self, name, cv_region, limit_size, volume_type):
        obj = self._client.patch_replication_stores_ident(
            name,
            cv_region.id if isinstance(cv_region, CVRegion) else cv_region,
            limit_size,
            volume_type
        )

        return ReplicationStore(obj['id'], obj['attributes'], client=self._client, collection=self.collection)

    def update(self, name=None, limit_size=None):
        obj = self._client.patch_replication_stores_ident(
            self.id,
            name=name,
            limit_size=limit_size,
        )

        return ReplicationStore(obj['id'], obj['attributes'], client=self._client, collection=self.collection)

    def delete(self):
        self._client.delete_replication_stores_ident(self.id)


class ReplicationStoreList(Collection):
    resource = ReplicationStore
    resource_type = "replication_stores"

    def __init__(self, client):
        self._client = client


class OnPremReplicationPartner(Resource):

    @property
    def replication_partnerships(self):
        if 'replication_partnerships' not in self.attrs:
            self.reload()

        return [ReplicationPartnership(p['id'], p, self._client, ReplicationPartnershipList(self._client))
                for p in self.attrs['replication_partnerships']]

    @property
    def replication_stores(self):
        if 'replication_partnerships' not in self.attrs:
            self.reload()

        return [ReplicationStore(
                    p['replication_store']['id'],
                    p['replication_store'],
                    self._client, ReplicationStoreList(self._client)
                ) for p in self.attrs['replication_partnerships']]

    def create(self, name, group_uid, keys):
        obj = self._client.post_onprem_replication_partners(
            name,
            group_uid,
            keys
        )

        return OnPremReplicationPartner(obj['id'], obj['attributes'], client=self._client, collection=self.collection)

    def update(self, name=None, keys=None):
        obj = self._client.patch_onprem_replication_partners_ident(
            self.id,
            name=name,
            keys=keys
        )

        return OnPremReplicationPartner(obj['id'], obj['attributes'], client=self._client, collection=self.collection)

    def delete(self):
        self._client.delete_onprem_replication_partners_ident(self.id)


class OnPremReplicationPartnerList(Collection):
    resource = OnPremReplicationPartner
    resource_type = "onprem_replication_partners"

    def __init__(self, client):
        self._client = client


class ReplicationPartnership(Resource):

    def __init__(self, id, attrs=None, client=None, collection=None):
        super().__init__(id, attrs, client, collection)
        self.replication_store = ReplicationStore(self.attrs['replication_store']['id'], self.attrs['replication_store'])
        self.onprem_replication_partner = OnPremReplicationPartner(self.attrs['onprem_replication_partner']['id'], self.attrs['onprem_replication_partner'])
        self._client = client

    def create(self, replication_store, onprem_replication_partner):
        obj = self._client.post_replication_partnerships(
            replication_store.id if isinstance(replication_store, ReplicationStore) else replication_store,
            onprem_replication_partner.id if isinstance(onprem_replication_partner, OnPremReplicationPartner) else onprem_replication_partner,
        )
        return ReplicationPartnership(obj['id'], obj['attributes'], client=self._client, collection=self.collection)

    def delete(self):
        self._client.delete_replication_partnerships_ident(self.id)


class ReplicationPartnershipList(Collection):
    resource = ReplicationPartnership
    resource_type = "replication_partnerships"

    def __init__(self, client):
        self._client = client
