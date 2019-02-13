# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.


from cloudvolumes.resource import Resource, Collection
from cloudvolumes.regions import Region


class Snapshot(Resource):
    def __init__(self, id, cloud_volume, attrs=None, client=None, collection=None):
        super().__init__(id, attrs, client, collection)
        self.cloud_volume = cloud_volume

    def delete(self):
        self._client.delete_cloud_volumes_ident_snapshots_snapshot_ref(self.cloud_volume.id, self.id)

    def clone(self, name, region, iops=None, private_cloud=None, existing_cloud_subnet=None, private_cloud_resource_group=None,
              schedule=None, retention=None, cloud_account_id=None):
        obj = self._client.post_cloud_volumes_ident_clone(
            self.cloud_volume.id,
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

        return CloudVolume(obj['id'], obj['attributes'], client=self._client, collection=self.cloud_volume.collection)

    def restore(self):
        obj = self._client.post_cloud_volumes_ident_restore(self.cloud_volume.id, self.id)
        return CloudVolume(obj['id'], obj['attributes'], client=self._client, collection=self.cloud_volume.collection)


class SnapshotList(Collection):
    resource = Snapshot
    resource_type = "snapshots"

    def __init__(self, cloud_volume, client):
        self.cloud_volume = cloud_volume
        self._client = client

    def get(self, id):
        raise NotImplementedError()

    def list(self, filters=None):
        return [Snapshot(snap['id'], self.cloud_volume, snap['attributes'], self._client, self)
                for snap in self._client.get_cloud_volumes_ident_snapshots(self.cloud_volume.id, filters=filters)]


class CloudVolume(Resource):
    @property
    def snapshots(self):
        return SnapshotList(self, self._client).list()

    @property
    def metrics(self):
        return self._client.get_cloud_volumes_ident_metrics(self.id)['attributes']

    def create(self, name, region, size, iops, perf_policy, schedule, retention, private_cloud, existing_cloud_subnet,
               encryption, volume_type, private_cloud_resource_group=None, cloud_account_id=None):
        obj = self._client.post_cloud_volumes(
            name,
            region.id if isinstance(region, Region) else region,
            size,
            iops,
            perf_policy,
            schedule,
            retention,
            private_cloud,
            existing_cloud_subnet,
            encryption,
            volume_type,
            private_cloud_resource_group=private_cloud_resource_group,
            cloud_account_id=cloud_account_id,
        )
        return CloudVolume(obj['id'], obj['attributes'], client=self._client, collection=self.collection)

    def replicate(self, replication_store=None, replica_volume_collection=None, schedule=None, retention=None):
        from cloudvolumes.replication import ReplicationStore, ReplicaVolumeCollection

        if replication_store is not None and replica_volume_collection is None or replica_volume_collection is not None and replication_store is None:
            raise ValueError("Must specify either 'replication_store' and 'replica_volume_collection' or 'schedule' and 'retention'")

        elif schedule is not None and retention is None or retention is not None and schedule is None:
            raise ValueError("Must specify either 'replication_store' and 'replica_volume_collection' or 'schedule' and 'retention'")

        obj = self._client.post_cloud_volumes_ident_replicate(
            self.id,
            replication_store.id if isinstance(replication_store, ReplicationStore) else replication_store,
            replica_volume_collection.id if isinstance(replica_volume_collection, ReplicaVolumeCollection) else replica_volume_collection,
            schedule=schedule,
            retention=retention
        )

        self.attrs = obj['attributes']

    def convert(self, replication_store, replica_volume_collection):
        from cloudvolumes.replication import ReplicaVolume, ReplicationStore, ReplicaVolumeCollection, ReplicaVolumeList

        obj = self._client.post_cloud_volumes_ident_convert(
            self.id,
            replication_store.id if isinstance(replication_store, ReplicationStore) else replication_store,
            replica_volume_collection.id if isinstance(replica_volume_collection, ReplicaVolumeCollection) else replica_volume_collection,
        )

        return ReplicaVolume(
            obj['id'],
            replication_store,
            obj['attributes'],
            replica_volume_collection=replica_volume_collection,
            client=self._client,
            collection=ReplicaVolumeList(replication_store=replication_store, client=self._client)
        )

    def update(self, name=None, size=None, iops=None, schedule=None, retention=None, multi_initiator=None):
        obj = self._client.patch_cloud_volumes_ident(
            self.id,
            name=name,
            size=size,
            iops=iops,
            schedule=schedule,
            retention=retention,
            multi_initiator=multi_initiator
        )

        return CloudVolume(obj['id'], obj['attributes'], client=self._client, collection=self.collection)

    def attach(self, initiator_ip):
        obj = self._client.post_cloud_volumes_ident_attach(self.id, initiator_ip)
        return CloudVolume(obj['id'], obj['attributes'], client=self._client, collection=self.collection)

    def detach(self, initiator_ip):
        obj = self._client.post_cloud_volumes_ident_detach(self.id, initiator_ip)
        return CloudVolume(obj['id'], obj['attributes'], client=self._client, collection=self.collection)

    def take_snapshot(self, name, description=None):
        obj = self._client.post_cloud_volumes_ident_snapshots(self.id, name, description=description)
        return Snapshot(obj['id'], self, attrs=obj['attributes'], client=self._client, collection=SnapshotList(self, self._client))

    def delete(self, force=False):
        self._client.delete_cloud_volumes_ident(self.id, force=force)


class CloudVolumeList(Collection):
    resource = CloudVolume
    resource_type = "cloud_volumes"

    def __init__(self, client):
        self._client = client
