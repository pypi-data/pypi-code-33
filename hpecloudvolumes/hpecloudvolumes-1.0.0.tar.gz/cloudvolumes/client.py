# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.

import requests
import os

from .exceptions import AuthenticationError, APIError, InternalError, RateLimitingError
from .cloud_volumes import CloudVolumeList
from .regions import ProviderList, RegionList, CVRegionList
from .replication import ReplicationStoreList, OnPremReplicationPartnerList, ReplicationPartnershipList
from .replication import ReplicaVolumeList


class APIClient:

    HEADERS = {'content-type': 'application/json'}

    def __init__(self, geo, email=None, password=None, access_key=None, access_secret=None, hostname="https://hpecloudvolumes.com"):

        if 'CLOUDVOLUMES_HOSTNAME' in os.environ:
            hostname = os.environ['CLOUDVOLUMES_HOSTNAME']

        if 'CLOUDVOLUMES_USER' in os.environ:
            access_key = None
            access_secret = None
            email = os.environ['CLOUDVOLUMES_USER']
            password = os.environ['CLOUDVOLUMES_PASSWORD']

        elif 'CLOUDVOLUMES_ACCESS_KEY' in os.environ:
            email = None
            password = None
            access_key = os.environ['CLOUDVOLUMES_ACCESS_KEY']
            access_secret = os.environ['CLOUDVOLUMES_ACCESS_SECRET']

        self.AUTH_URL = f"{hostname[:8]}{geo}.{hostname[8:]}/auth/login"
        self.BASE_URL = f"{hostname[:8]}{geo}.{hostname[8:]}/api/v2"

        self.login(email=email, password=password, access_key=access_key, access_secret=access_secret)

    def get_geos(self):
        resp = requests.get(f"{self.BASE_URL}/service", headers=self.HEADERS)

        if resp.status_code == 200:
            return {geo: info['label'] for geo, info in resp.json()['data']['attributes']['geos'].items()}

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def login(self, email=None, password=None, access_key=None, access_secret=None):
        """Authenticate to CloudVolumes with user-based authentication (email / password) or token-based authentication (access_key / secret)"""

        if email is not None:
            if password is None:
                raise TypeError("The password is required when performing user-based authentication.")

            body = {"email": email, "password": password}

        elif access_key is not None:
            if access_secret is None:
                raise TypeError("The access_secret is required when performing token-based authentication.")

            body = {"access_key": access_key, "access_secret": access_secret}

        else:
            raise TypeError("Either email or access_secret are required when trying to authenticate.")

        resp = requests.post(
            self.AUTH_URL,
            json=body,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            self._auth = (email if email is not None else access_key, resp.json()['token'])

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_session(self, fields=None):
        """Get information on the current session."""

        query = []

        if fields is not None:
            query.append(f"fields={fields}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/session{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_interfaces(self, filters=None, fields=None, sort=None):
        """Get the list of existing Interfaces."""

        query = []

        if filters is not None:
            query.append(f"filters={filters}")
        if fields is not None:
            query.append(f"fields={fields}")
        if sort is not None:
            query.append(f"sort={sort}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/interfaces{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_cloud_volumes(self, filters=None, fields=None, sort=None):
        """Get the list of existing CloudVolumes."""

        query = []

        if filters is not None:
            query.append(f"filters={filters}")
        if fields is not None:
            query.append(f"fields={fields}")
        if sort is not None:
            query.append(f"sort={sort}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/cloud_volumes{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def post_cloud_volumes(self, name, region_id, size, iops, perf_policy, schedule, retention, private_cloud, existing_cloud_subnet, encryption, volume_type, private_cloud_resource_group=None, cloud_account_id=None, bandwidth=None, automated_connection=None, app_uuid=None, metadata=None):
        """Create a CloudVolume."""

        body = {
            'data': {
                'name': name,
                'region_id': region_id,
                'size': size,
                'iops': iops,
                'perf_policy': perf_policy,
                'schedule': schedule,
                'retention': retention,
                'private_cloud': private_cloud,
                'existing_cloud_subnet': existing_cloud_subnet,
                'encryption': encryption,
                'volume_type': volume_type
            }
        }

        if private_cloud_resource_group is not None:
            body['data']['private_cloud_resource_group'] = private_cloud_resource_group
        if cloud_account_id is not None:
            body['data']['cloud_account_id'] = cloud_account_id
        if bandwidth is not None:
            body['data']['bandwidth'] = bandwidth
        if automated_connection is not None:
            body['data']['automated_connection'] = automated_connection
        if app_uuid is not None:
            body['data']['app_uuid'] = app_uuid
        if metadata is not None:
            body['data']['metadata'] = metadata

        resp = requests.post(
            f'{self.BASE_URL}/cloud_volumes',
            auth=self._auth,
            json=body,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_cloud_volumes_ident(self, ident, fields=None):
        """Get detailed information on the CloudVolume."""

        query = []

        if fields is not None:
            query.append(f"fields={fields}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/cloud_volumes/{ident}{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def delete_cloud_volumes_ident(self, ident, force=None):
        """Delete a CloudVolume."""

        query = []

        if force is not None:
            query.append(f"force={force}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.delete(
            f"{self.BASE_URL}/cloud_volumes/{ident}{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def patch_cloud_volumes_ident(self, ident, name=None, size=None, iops=None, schedule=None, retention=None, multi_initiator=None, metadata=None, app_uuid=None):
        """Update CloudVolume properties."""

        body = {
            'data': {
            }
        }

        if name is not None:
            body['data']['name'] = name
        if size is not None:
            body['data']['size'] = size
        if iops is not None:
            body['data']['iops'] = iops
        if schedule is not None:
            body['data']['schedule'] = schedule
        if retention is not None:
            body['data']['retention'] = retention
        if multi_initiator is not None:
            body['data']['multi_initiator'] = multi_initiator
        if metadata is not None:
            body['data']['metadata'] = metadata
        if app_uuid is not None:
            body['data']['app_uuid'] = app_uuid

        resp = requests.patch(
            f'{self.BASE_URL}/cloud_volumes/{ident}',
            auth=self._auth,
            json=body,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def post_cloud_volumes_ident_attach(self, ident, initiator_ip, connect_to=None):
        """Attach an Initiator (virtual machine) to the given CloudVolume."""

        body = {
            'data': {
                'initiator_ip': initiator_ip
            }
        }

        if connect_to is not None:
            body['data']['connect_to'] = connect_to

        resp = requests.post(
            f'{self.BASE_URL}/cloud_volumes/{ident}/attach',
            auth=self._auth,
            json=body,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def post_cloud_volumes_ident_clone(self, ident, name, snapshot_ref, region_id, iops=None, cloud_account_id=None, schedule=None, retention=None, private_cloud=None, existing_cloud_subnet=None, private_cloud_resource_group=None, bandwidth=None, automated_connection=None, app_uuid=None, metadata=None):
        """Clone a Snapshot of the given CloudVolume."""

        body = {
            'data': {
                'name': name,
                'snapshot_ref': snapshot_ref,
                'region_id': region_id
            }
        }

        if iops is not None:
            body['data']['iops'] = iops
        if cloud_account_id is not None:
            body['data']['cloud_account_id'] = cloud_account_id
        if schedule is not None:
            body['data']['schedule'] = schedule
        if retention is not None:
            body['data']['retention'] = retention
        if private_cloud is not None:
            body['data']['private_cloud'] = private_cloud
        if existing_cloud_subnet is not None:
            body['data']['existing_cloud_subnet'] = existing_cloud_subnet
        if private_cloud_resource_group is not None:
            body['data']['private_cloud_resource_group'] = private_cloud_resource_group
        if bandwidth is not None:
            body['data']['bandwidth'] = bandwidth
        if automated_connection is not None:
            body['data']['automated_connection'] = automated_connection
        if app_uuid is not None:
            body['data']['app_uuid'] = app_uuid
        if metadata is not None:
            body['data']['metadata'] = metadata

        resp = requests.post(
            f'{self.BASE_URL}/cloud_volumes/{ident}/clone',
            auth=self._auth,
            json=body,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def post_cloud_volumes_ident_convert(self, ident, replication_store_id, replica_volume_collection_id):
        """Convert a CloudVolume to a ReplicaVolume."""

        body = {
            'data': {
                'replication_store_id': replication_store_id,
                'replica_volume_collection_id': replica_volume_collection_id
            }
        }

        resp = requests.post(
            f'{self.BASE_URL}/cloud_volumes/{ident}/convert',
            auth=self._auth,
            json=body,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def post_cloud_volumes_ident_detach(self, ident, initiator_ip, force=None):
        """Detach an Initiator (virtual machine) from the given CloudVolume."""

        body = {
            'data': {
                'initiator_ip': initiator_ip
            }
        }

        if force is not None:
            body['data']['force'] = force

        resp = requests.post(
            f'{self.BASE_URL}/cloud_volumes/{ident}/detach',
            auth=self._auth,
            json=body,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_cloud_volumes_ident_metrics(self, ident, min=None, max=None):
        """Retrieve CloudVolume usage metrics."""

        query = []

        if min is not None:
            query.append(f"min={min}")
        if max is not None:
            query.append(f"max={max}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/cloud_volumes/{ident}/metrics{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def post_cloud_volumes_ident_replicate(self, ident, replication_store_id=None, replica_volume_collection_id=None, schedule=None, retention=None):
        """Replicate a CloudVolume through a ReplicaVolumeCollection."""

        body = {
            'data': {
            }
        }

        if replication_store_id is not None:
            body['data']['replication_store_id'] = replication_store_id
        if replica_volume_collection_id is not None:
            body['data']['replica_volume_collection_id'] = replica_volume_collection_id
        if schedule is not None:
            body['data']['schedule'] = schedule
        if retention is not None:
            body['data']['retention'] = retention

        resp = requests.post(
            f'{self.BASE_URL}/cloud_volumes/{ident}/replicate',
            auth=self._auth,
            json=body,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def post_cloud_volumes_ident_restore(self, ident, snapshot_ref):
        """Restore the given CloudVolume to a previous Snapshot."""

        body = {
            'data': {
                'snapshot_ref': snapshot_ref
            }
        }

        resp = requests.post(
            f'{self.BASE_URL}/cloud_volumes/{ident}/restore',
            auth=self._auth,
            json=body,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_cloud_volumes_ident_snapshots(self, ident, filters=None, fields=None, sort=None):
        """List the Snapshots available for the given CloudVolume."""

        query = []

        if filters is not None:
            query.append(f"filters={filters}")
        if fields is not None:
            query.append(f"fields={fields}")
        if sort is not None:
            query.append(f"sort={sort}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/cloud_volumes/{ident}/snapshots{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def post_cloud_volumes_ident_snapshots(self, ident, name, description=None, app_uuid=None):
        """Create a manual Snapshot of the given CloudVolume."""

        body = {
            'data': {
                'name': name
            }
        }

        if description is not None:
            body['data']['description'] = description
        if app_uuid is not None:
            body['data']['app_uuid'] = app_uuid

        resp = requests.post(
            f'{self.BASE_URL}/cloud_volumes/{ident}/snapshots',
            auth=self._auth,
            json=body,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def delete_cloud_volumes_ident_snapshots_snapshot_ref(self, ident, snapshot_ref):
        """Delete the given Snapshot for this CloudVolume."""

        resp = requests.delete(
            f"{self.BASE_URL}/cloud_volumes/{ident}/snapshots/{snapshot_ref}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_regions(self, filters=None, fields=None, sort=None):
        """Get the list of available Regions."""

        query = []

        if filters is not None:
            query.append(f"filters={filters}")
        if fields is not None:
            query.append(f"fields={fields}")
        if sort is not None:
            query.append(f"sort={sort}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/regions{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_regions_ident(self, ident, fields=None):
        """Get detailed Region information."""

        query = []

        if fields is not None:
            query.append(f"fields={fields}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/regions/{ident}{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_cv_regions(self, filters=None, fields=None, sort=None):
        """Get the list of available CVRegions."""

        query = []

        if filters is not None:
            query.append(f"filters={filters}")
        if fields is not None:
            query.append(f"fields={fields}")
        if sort is not None:
            query.append(f"sort={sort}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/cv_regions{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_cv_regions_ident(self, ident, fields=None):
        """Get detailed Cloud Volume Region information."""

        query = []

        if fields is not None:
            query.append(f"fields={fields}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/cv_regions/{ident}{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_providers(self, filters=None, fields=None, sort=None):
        """Get the list of available Providers."""

        query = []

        if filters is not None:
            query.append(f"filters={filters}")
        if fields is not None:
            query.append(f"fields={fields}")
        if sort is not None:
            query.append(f"sort={sort}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/providers{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_providers_ident(self, ident, fields=None):
        """Get detailed Provider information."""

        query = []

        if fields is not None:
            query.append(f"fields={fields}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/providers/{ident}{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_initiators(self, filters=None, fields=None, sort=None):
        """Get the list of Initiators currently attached to CloudVolumes."""

        query = []

        if filters is not None:
            query.append(f"filters={filters}")
        if fields is not None:
            query.append(f"fields={fields}")
        if sort is not None:
            query.append(f"sort={sort}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/initiators{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_initiators_ident(self, ident, fields=None):
        """Get detailed Initiator information."""

        query = []

        if fields is not None:
            query.append(f"fields={fields}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/initiators/{ident}{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_replication_stores(self, filters=None, fields=None, sort=None):
        """Get the list of existing ReplicationStores."""

        query = []

        if filters is not None:
            query.append(f"filters={filters}")
        if fields is not None:
            query.append(f"fields={fields}")
        if sort is not None:
            query.append(f"sort={sort}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/replication_stores{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def post_replication_stores(self, name, cv_region_id, limit_size, volume_type, limit_mbps=None):
        """Create a ReplicationStore."""

        body = {
            'data': {
                'name': name,
                'cv_region_id': cv_region_id,
                'limit_size': limit_size,
                'volume_type': volume_type
            }
        }

        if limit_mbps is not None:
            body['data']['limit_mbps'] = limit_mbps

        resp = requests.post(
            f'{self.BASE_URL}/replication_stores',
            auth=self._auth,
            json=body,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_replication_stores_ident(self, ident, fields=None):
        """Get detailed ReplicationStore information."""

        query = []

        if fields is not None:
            query.append(f"fields={fields}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/replication_stores/{ident}{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def patch_replication_stores_ident(self, ident, name=None, limit_size=None, limit_mbps=None):
        """Update ReplicationStore properties."""

        body = {
            'data': {
            }
        }

        if name is not None:
            body['data']['name'] = name
        if limit_size is not None:
            body['data']['limit_size'] = limit_size
        if limit_mbps is not None:
            body['data']['limit_mbps'] = limit_mbps

        resp = requests.patch(
            f'{self.BASE_URL}/replication_stores/{ident}',
            auth=self._auth,
            json=body,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def delete_replication_stores_ident(self, ident):
        """Delete a ReplicationStore."""

        resp = requests.delete(
            f"{self.BASE_URL}/replication_stores/{ident}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_replication_stores_ident_replica_volume_collections(self, ident, fields=None, filters=None, sort=None):
        """Get the list of ReplicaVolumeCollections available in the given ReplicationStore"""

        query = []

        if fields is not None:
            query.append(f"fields={fields}")
        if filters is not None:
            query.append(f"filters={filters}")
        if sort is not None:
            query.append(f"sort={sort}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/replication_stores/{ident}/replica_volume_collections{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_replication_stores_ident_replica_volume_collections_volcoll_ref(self, ident, volcoll_ref, fields=None, filters=None, sort=None):
        """Get detailed ReplicaVolumeCollections information."""

        query = []

        if fields is not None:
            query.append(f"fields={fields}")
        if filters is not None:
            query.append(f"filters={filters}")
        if sort is not None:
            query.append(f"sort={sort}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/replication_stores/{ident}/replica_volume_collections/{volcoll_ref}{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def delete_replication_stores_ident_replica_volume_collections_volcoll_ref(self, ident, volcoll_ref, fields=None):
        """Delete a ReplicaVolumeCollection from the given ReplicationStore."""

        query = []

        if fields is not None:
            query.append(f"fields={fields}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.delete(
            f"{self.BASE_URL}/replication_stores/{ident}/replica_volume_collections/{volcoll_ref}{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def patch_replication_stores_ident_replica_volume_collections_volcoll_ref(self, ident, volcoll_ref, replication_partnership_id, replication_direction):
        """Change the replication configuration of a ReplicaVolumeCollection."""

        body = {
            'data': {
                'replication_partnership_id': replication_partnership_id,
                'replication_direction': replication_direction
            }
        }

        resp = requests.patch(
            f'{self.BASE_URL}/replication_stores/{ident}/replica_volume_collections/{volcoll_ref}',
            auth=self._auth,
            json=body,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_replication_stores_ident_replica_volumes(self, ident, fields=None, filters=None, sort=None):
        """Get the list of ReplicaVolumes available in the given ReplicationStore."""

        query = []

        if fields is not None:
            query.append(f"fields={fields}")
        if filters is not None:
            query.append(f"filters={filters}")
        if sort is not None:
            query.append(f"sort={sort}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/replication_stores/{ident}/replica_volumes{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_replication_stores_ident_replica_volumes_vol_ref(self, ident, vol_ref, fields=None):
        """Get detailed ReplicaVolume information."""

        query = []

        if fields is not None:
            query.append(f"fields={fields}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/replication_stores/{ident}/replica_volumes/{vol_ref}{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def delete_replication_stores_ident_replica_volumes_vol_ref(self, ident, vol_ref, fields=None):
        """Delete the given ReplicaVolume."""

        query = []

        if fields is not None:
            query.append(f"fields={fields}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.delete(
            f"{self.BASE_URL}/replication_stores/{ident}/replica_volumes/{vol_ref}{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_replication_stores_ident_replica_volumes_vol_ref_metrics(self, ident, vol_ref, min=None, max=None):
        """Retrieve ReplicaVolume usage metrics."""

        query = []

        if min is not None:
            query.append(f"min={min}")
        if max is not None:
            query.append(f"max={max}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/replication_stores/{ident}/replica_volumes/{vol_ref}/metrics{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_replication_stores_ident_replica_volumes_vol_ref_snapshots(self, ident, vol_ref, fields=None, filters=None, sort=None):
        """Get the list of ReplicaSnapshots for the given ReplicaVolume."""

        query = []

        if fields is not None:
            query.append(f"fields={fields}")
        if filters is not None:
            query.append(f"filters={filters}")
        if sort is not None:
            query.append(f"sort={sort}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/replication_stores/{ident}/replica_volumes/{vol_ref}/snapshots{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def delete_replication_stores_ident_replica_volumes_vol_ref_snapshots_snapshot_ref(self, ident, vol_ref, snapshot_ref, fields=None):
        """Delete the given ReplicaSnapshot of this ReplicaVolume."""

        query = []

        if fields is not None:
            query.append(f"fields={fields}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.delete(
            f"{self.BASE_URL}/replication_stores/{ident}/replica_volumes/{vol_ref}/snapshots/{snapshot_ref}{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def post_replication_stores_ident_replica_volumes_vol_ref_clone(self, ident, vol_ref, name, snapshot_ref, region_id, iops, private_cloud, existing_cloud_subnet, private_cloud_resource_group=None, schedule=None, retention=None, cloud_account_id=None, bandwidth=None, automated_connection=None):
        """Clone a ReplicaSnapshot of the given ReplicaVolume."""

        body = {
            'data': {
                'name': name,
                'snapshot_ref': snapshot_ref,
                'region_id': region_id,
                'iops': iops,
                'private_cloud': private_cloud,
                'existing_cloud_subnet': existing_cloud_subnet
            }
        }

        if private_cloud_resource_group is not None:
            body['data']['private_cloud_resource_group'] = private_cloud_resource_group
        if schedule is not None:
            body['data']['schedule'] = schedule
        if retention is not None:
            body['data']['retention'] = retention
        if cloud_account_id is not None:
            body['data']['cloud_account_id'] = cloud_account_id
        if bandwidth is not None:
            body['data']['bandwidth'] = bandwidth
        if automated_connection is not None:
            body['data']['automated_connection'] = automated_connection

        resp = requests.post(
            f'{self.BASE_URL}/replication_stores/{ident}/replica_volumes/{vol_ref}/clone',
            auth=self._auth,
            json=body,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def post_replication_stores_ident_replica_volumes_vol_ref_convert(self, ident, vol_ref, name, region_id, private_cloud, existing_cloud_subnet, iops=None, schedule=None, retention=None, private_cloud_resource_group=None, cloud_account_id=None, bandwidth=None, automated_connection=None):
        """Convert a ReplicaVolume to a CloudVolume."""

        body = {
            'data': {
                'name': name,
                'region_id': region_id,
                'private_cloud': private_cloud,
                'existing_cloud_subnet': existing_cloud_subnet
            }
        }

        if iops is not None:
            body['data']['iops'] = iops
        if schedule is not None:
            body['data']['schedule'] = schedule
        if retention is not None:
            body['data']['retention'] = retention
        if private_cloud_resource_group is not None:
            body['data']['private_cloud_resource_group'] = private_cloud_resource_group
        if cloud_account_id is not None:
            body['data']['cloud_account_id'] = cloud_account_id
        if bandwidth is not None:
            body['data']['bandwidth'] = bandwidth
        if automated_connection is not None:
            body['data']['automated_connection'] = automated_connection

        resp = requests.post(
            f'{self.BASE_URL}/replication_stores/{ident}/replica_volumes/{vol_ref}/convert',
            auth=self._auth,
            json=body,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def post_replication_stores_ident_replica_volumes_vol_ref_restore(self, ident, vol_ref, snapshot_ref):
        """Restore the given ReplicaVolume to a previous Snapshot."""

        body = {
            'data': {
                'snapshot_ref': snapshot_ref
            }
        }

        resp = requests.post(
            f'{self.BASE_URL}/replication_stores/{ident}/replica_volumes/{vol_ref}/restore',
            auth=self._auth,
            json=body,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_replication_stores_ident_cloud_volumes(self, ident, fields=None, filters=None, sort=None):
        """Get the list of CloudVolumes available in the given ReplicationStore."""

        query = []

        if fields is not None:
            query.append(f"fields={fields}")
        if filters is not None:
            query.append(f"filters={filters}")
        if sort is not None:
            query.append(f"sort={sort}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/replication_stores/{ident}/cloud_volumes{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_replica_volumes(self, fields=None, filters=None, sort=None):
        """Get the list of available ReplicaVolumes."""

        query = []

        if fields is not None:
            query.append(f"fields={fields}")
        if filters is not None:
            query.append(f"filters={filters}")
        if sort is not None:
            query.append(f"sort={sort}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/replica_volumes{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_onprem_replication_partners(self, filters=None, fields=None, sort=None):
        """Get the list of available OnPremReplicationPartners."""

        query = []

        if filters is not None:
            query.append(f"filters={filters}")
        if fields is not None:
            query.append(f"fields={fields}")
        if sort is not None:
            query.append(f"sort={sort}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/onprem_replication_partners{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def post_onprem_replication_partners(self, name, group_uid, keys):
        """Create an OnPremReplicationPartner."""

        body = {
            'data': {
                'name': name,
                'group_uid': group_uid,
                'keys': keys
            }
        }

        resp = requests.post(
            f'{self.BASE_URL}/onprem_replication_partners',
            auth=self._auth,
            json=body,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_onprem_replication_partners_ident(self, ident, fields=None):
        """Get detailed OnPremReplicationPartner information."""

        query = []

        if fields is not None:
            query.append(f"fields={fields}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/onprem_replication_partners/{ident}{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def patch_onprem_replication_partners_ident(self, ident, name=None, keys=None):
        """Update OnPremReplicationPartner properties."""

        body = {
            'data': {
            }
        }

        if name is not None:
            body['data']['name'] = name
        if keys is not None:
            body['data']['keys'] = keys

        resp = requests.patch(
            f'{self.BASE_URL}/onprem_replication_partners/{ident}',
            auth=self._auth,
            json=body,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def delete_onprem_replication_partners_ident(self, ident):
        """Delete the given OnPremReplicationPartner."""

        resp = requests.delete(
            f"{self.BASE_URL}/onprem_replication_partners/{ident}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_replication_partnerships(self, filters=None, fields=None, sort=None):
        """Get the list of available ReplicationPartnerships."""

        query = []

        if filters is not None:
            query.append(f"filters={filters}")
        if fields is not None:
            query.append(f"fields={fields}")
        if sort is not None:
            query.append(f"sort={sort}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/replication_partnerships{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def post_replication_partnerships(self, replication_store_id, onprem_replication_partner_id):
        """Create a ReplicationPartnership."""

        body = {
            'data': {
                'replication_store_id': replication_store_id,
                'onprem_replication_partner_id': onprem_replication_partner_id
            }
        }

        resp = requests.post(
            f'{self.BASE_URL}/replication_partnerships',
            auth=self._auth,
            json=body,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def get_replication_partnerships_ident(self, ident, fields=None):
        """Get detailed ReplicationPartnership information."""

        query = []

        if fields is not None:
            query.append(f"fields={fields}")

        query = f"?{'&'.join(query)}" if len(query) > 0 else ''

        resp = requests.get(
            f"{self.BASE_URL}/replication_partnerships/{ident}{query}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())

    def delete_replication_partnerships_ident(self, ident):
        """Delete the given ReplicationPartnership."""

        resp = requests.delete(
            f"{self.BASE_URL}/replication_partnerships/{ident}",
            auth=self._auth,
            headers=self.HEADERS
        )

        if resp.status_code == 200:
            return resp.json()['data']

        elif resp.status_code == 204:
            return

        elif resp.status_code == 429:
            raise RateLimitingError()

        elif resp.status_code in [401, 403]:
            raise AuthenticationError(resp.json())

        elif resp.status_code >= 500:
            raise InternalError()

        else:
            raise APIError(resp.json())


class CloudVolumesClient:
    def __init__(self, geo, email=None, password=None, access_key=None, access_secret=None, hostname="cloudvolumes.hpe.com"):
        self._client = APIClient(email=email, password=password, access_key=access_key, access_secret=access_secret, hostname=hostname, geo=geo)

    @property
    def geos(self):
        return self._client.get_geos()

    @property
    def cloud_accounts(self):
        return [{'id': ca['id'], 'name': ca['name']} for ca in self.session['cloud_accounts']]

    @property
    def session(self):
        return self._client.get_session()['attributes']

    @property
    def cloud_volumes(self):
        return CloudVolumeList(self._client)

    @property
    def providers(self):
        return ProviderList(self._client)

    @property
    def cv_regions(self):
        return CVRegionList(self._client)

    @property
    def regions(self):
        return RegionList(self._client)

    @property
    def replication_stores(self):
        return ReplicationStoreList(self._client)

    @property
    def onprem_replication_partners(self):
        return OnPremReplicationPartnerList(self._client)

    @property
    def replication_partnerships(self):
        return ReplicationPartnershipList(self._client)

    @property
    def replica_volumes(self):
        return ReplicaVolumeList(client=self._client)
