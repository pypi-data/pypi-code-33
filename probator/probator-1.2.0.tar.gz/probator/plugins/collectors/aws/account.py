from collections import namedtuple
from copy import deepcopy

from botocore.exceptions import ClientError
from munch import munchify
from probator.database import db
from probator.plugins.collectors.aws import AWSBaseAccountCollector
from probator.plugins.types.resources import S3Bucket, CloudFrontDist, DNSZone, DNSRecord
from probator.utils import get_resource_id
from probator.wrappers import retry, rollback

BucketInfo = namedtuple('BucketInfo', ('region', 'website', 'tags'))


class AWSRoute53Collector(AWSBaseAccountCollector):
    name = 'AWS Route53 Collector'

    def run(self):
        try:
            self.update_route53()

        finally:
            del self.session

    @rollback
    @retry
    def update_route53(self):
        """Update list of Route53 DNS Zones and their records for the account

        Returns:
            `None`
        """
        self.log.debug(f'Updating Route53 information for {self.account.account_name}')

        # region Update zones
        existing_zones = DNSZone.get_all(self.account)
        zones = self.__fetch_route53_zones()
        for resource_id, data in zones.items():
            tags = data.pop('tags')
            if resource_id in existing_zones:
                zone = DNSZone.get(resource_id)
                if zone.update_resource(properties=data, tags=tags):
                    self.log.debug(f'Change detected for Route53 zone {self.account.account_name}/{zone.name}')
                    zone.save()
            else:
                DNSZone.create(
                    resource_id,
                    account_id=self.account.account_id,
                    properties=data,
                    tags=tags
                )

                self.log.debug(f'Added Route53 zone {self.account.account_name}/{data.name}')

        db.session.commit()

        zk = set(zones.keys())
        ezk = set(existing_zones.keys())

        for resource_id in ezk - zk:
            zone = existing_zones[resource_id]

            db.session.delete(zone.resource)
            self.log.debug(f'Deleted Route53 zone {self.account.account_name}/{zone.name}')
        db.session.commit()
        # endregion

        # region Update resource records
        for zone_id, zone in DNSZone.get_all(self.account).items():
            existing_records = {rec.id: rec for rec in zone.children}
            records = self.__fetch_route53_zone_records(zone.get_property('zone_id').value)

            for record_id, data in records.items():
                if record_id in existing_records:
                    record = existing_records[record_id]
                    if record.update_resource(properties=data):
                        self.log.debug(f'Changed detected for DNSRecord {self.account.account_name}/{zone.name}/{data.name}')
                        record.save()
                else:
                    record = DNSRecord.create(
                        record_id,
                        account_id=self.account.account_id,
                        properties=data
                    )
                    self.log.debug(f'Added new DNSRecord {self.account.account_name}/{zone.name}/{data.name}')
                    zone.add_child(record)
            db.session.add(zone.resource)
            db.session.commit()

            rk = set(records.keys())
            erk = set(existing_records.keys())

            for resource_id in erk - rk:
                record = existing_records[resource_id]
                zone.delete_child(record)
                self.log.debug(f'Deleted Route53 record {self.account.account_name}/{zone_id}/{record.name}')
            db.session.commit()
        # endregion

    # region Helper functions
    def __fetch_route53_zones(self):
        """Return a list of all DNS zones hosted in Route53

        Returns:
            :obj:`list` of `dict`
        """
        done = False
        marker = None
        zones = {}
        route53 = self.session.client('route53')

        try:
            while not done:
                if marker:
                    response = route53.list_hosted_zones(Marker=marker)
                else:
                    response = route53.list_hosted_zones()

                if response['IsTruncated']:
                    marker = response['NextMarker']
                else:
                    done = True

                for zone_data in response['HostedZones']:
                    zones[get_resource_id('r53z', zone_data['Id'])] = {
                        'name': zone_data['Name'].rstrip('.'),
                        'source': f'AWS/{self.account.account_name}',
                        'comment': zone_data['Config']['Comment'] if 'Comment' in zone_data['Config'] else None,
                        'zone_id': zone_data['Id'],
                        'private_zone': zone_data['Config']['PrivateZone'],
                        'tags': self.__fetch_route53_zone_tags(zone_data['Id'])
                    }

            return munchify(zones)

        finally:
            del route53

    def __fetch_route53_zone_records(self, zone_id):
        """Return all resource records for a specific Route53 zone

        Args:
            zone_id (`str`): Name / ID of the hosted zone

        Returns:
            `dict`
        """
        route53 = self.session.client('route53')

        done = False
        next_name = next_type = None
        records = {}

        try:
            while not done:
                if next_name and next_type:
                    response = route53.list_resource_record_sets(
                        HostedZoneId=zone_id,
                        StartRecordName=next_name,
                        StartRecordType=next_type
                    )
                else:
                    response = route53.list_resource_record_sets(HostedZoneId=zone_id)

                if response['IsTruncated']:
                    next_name = response['NextRecordName']
                    next_type = response['NextRecordType']
                else:
                    done = True

                if 'ResourceRecordSets' in response:
                    for record in response['ResourceRecordSets']:
                        # Cannot make this a list, due to a race-condition in the AWS api that might return the same
                        # record more than once, so we use a dict instead to ensure that if we get duplicate records
                        # we simply just overwrite the one already there with the same info.
                        record_id = self._get_resource_hash(zone_id, record)
                        if 'AliasTarget' in record:
                            value = record['AliasTarget']['DNSName']
                            records[record_id] = {
                                'name': record['Name'].rstrip('.'),
                                'type': 'ALIAS',
                                'ttl': 0,
                                'value': [value]
                            }
                        else:
                            value = [y['Value'] for y in record['ResourceRecords']]
                            records[record_id] = {
                                'name': record['Name'].rstrip('.'),
                                'type': record['Type'],
                                'ttl': record['TTL'],
                                'value': value
                            }

            return munchify(records)

        finally:
            del route53

    def __fetch_route53_zone_tags(self, zone_id):
        """Return a dict with the tags for the zone

        Args:
            zone_id (`str`): ID of the hosted zone

        Returns:
            :obj:`dict` of `str`: `str`
        """
        route53 = self.session.client('route53')

        try:
            return {
                tag['Key']: tag['Value'] for tag in
                route53.list_tags_for_resource(
                    ResourceType='hostedzone',
                    ResourceId=zone_id.split('/')[-1]
                )['ResourceTagSet']['Tags']
            }

        finally:
            del route53

    @staticmethod
    def _get_resource_hash(zone_name, record):
        """Returns the last ten digits of the sha256 hash of the combined arguments. Useful for generating unique
        resource IDs

        Args:
            zone_name (`str`): The name of the DNS Zone the record belongs to
            record (`dict`): A record dict to generate the hash from

        Returns:
            `str`
        """
        record_data = deepcopy(record)
        if type(record_data.get('GeoLocation', None)) == dict:
            record_data['GeoLocation'] = ':'.join(f'{k}={v}' for k, v in record_data['GeoLocation'].items())

        args = [
            zone_name,
            record_data.get('Name', 0),
            record_data.get('Type', 0),
            record_data.get('Weight', 0),
            record_data.get('Region', 0),
            record_data.get('GeoLocation', 0),
            record_data.get('Failover', 0),
            record_data.get('HealthCheckId', 0),
            record_data.get('TrafficPolicyInstanceId', 0)
        ]

        return get_resource_id('r53r', args)
    # endregion


class AWSS3Collector(AWSBaseAccountCollector):
    name = 'AWS S3 Collector'

    def run(self):
        self.update_s3buckets()

    @rollback
    @retry
    def update_s3buckets(self):
        """Update list of S3 Buckets for the account

        Returns:
            `None`
        """
        self.log.debug(f'Updating S3Buckets for {self.account.account_name}')
        s3 = self.session.resource('s3')
        s3c = self.session.client('s3')

        try:
            existing_buckets = S3Bucket.get_all(self.account)
            buckets = {bucket.name: bucket for bucket in s3.buckets.all()}

            for bucket in buckets.values():
                bucket_info = self._get_bucket_information(bucket)

                properties = {
                    'website_enabled': bucket_info.website,
                }

                if bucket.name in existing_buckets:
                    bucket = existing_buckets[bucket.name]
                    if bucket.update_resource(properties=properties, tags=bucket_info.tags):
                        self.log.debug(f'Change detected for S3Bucket {bucket}')
                        bucket.save()
                else:
                    # If a bucket has no tags, a boto3 error is thrown. We treat this as an empty tag set
                    bucket = S3Bucket.create(
                        bucket.name,
                        account_id=self.account.account_id,
                        properties=properties,
                        location=bucket_info.region,
                        tags=bucket_info.tags
                    )
                    self.log.debug(f'Added new S3Bucket {bucket}')
            db.session.commit()

            bk = set(list(buckets.keys()))
            ebk = set(list(existing_buckets.keys()))

            for resource_id in ebk - bk:
                bucket = existing_buckets[resource_id]
                self.log.debug(f'Deleted S3Bucket {bucket}')
                db.session.delete(bucket.resource)
            db.session.commit()

        finally:
            del s3, s3c

    @retry
    def _get_bucket_information(self, bucket):
        """Collect extra bucket information

        Args:
            bucket (`S3Bucket`): Boto3 S3Bucket object

        Returns:
            `BucketInfo`
        """
        s3 = self.session.client('s3')

        try:
            # region Bucket Location
            try:
                bucket_region = s3.get_bucket_location(Bucket=bucket.name).get('LocationConstraint', 'us-east-1')

            except ClientError:
                self.log.exception(f'Failed getting bucket location for {self.account.account_name}/{bucket.name}')
                bucket_region = 'Unavailable'
            # endregion

            # region Website configuration
            try:
                website_enabled = True if bucket.Website().index_document else False

            except ClientError as e:
                code = e.response['Error']['Code']
                if code == 'NoSuchWebsiteConfiguration':
                    website_enabled = False

                elif code == 'AccessDenied':
                    self.log.debug(f'Bucket ACL is prevents gathering website information on {self.account.account_name} / {bucket.name}')
                    website_enabled = None

                else:
                    website_enabled = None
            # endregion

            # region Tags
            try:
                tags = {t['Key']: t['Value'] for t in bucket.Tagging().tag_set}

            except ClientError:
                tags = {}
            # endregion

            return BucketInfo(region=bucket_region, website=website_enabled, tags=tags)

        finally:
            del s3


class AWSCloudFrontCollector(AWSBaseAccountCollector):
    name = 'AWS CloudFront Collector'

    def run(self):
        self.update_cloudfront()

    @rollback
    @retry
    def update_cloudfront(self):
        """Update list of CloudFront Distributions for the account

        Returns:
            `None`
        """
        self.log.debug(f'Updating CloudFront distributions for {self.account.account_name}')
        existing_dists = CloudFrontDist.get_all(self.account, None)
        dists = []

        for data in dists:
            properties = {
                'arn': data['arn'],
                'domain_name': data['name'],
                'origins': data['origins'],
                'enabled': data['enabled'],
                'type': data['type']
            }

            if data['id'] in existing_dists:
                dist = existing_dists[data['id']]

                if dist.update_resource(properties=properties, tags=data['tags']):
                    self.log.debug(f'Updated CloudFrontDist {dist}')
                    dist.save()

            else:
                dist = CloudFrontDist.create(
                    data['id'],
                    account_id=self.account.account_id,
                    properties=properties,
                    tags=data['tags']
                )

                self.log.debug(f'Added new CloudFrontDist {dist}')
        db.session.commit()

        dk = {x['id'] for x in dists}
        edk = set(existing_dists.keys())

        for resource_id in edk - dk:
            dist = existing_dists[resource_id]
            self.log.debug(f'Deleted CloudFrontDist {dist}')
            db.session.delete(dist.resource)
        db.session.commit()

    @retry
    def _fetch_distributions(self):
        cfr = self.session.client('cloudfront')

        try:
            dists = []

            # region Web distributions
            done = False
            marker = None
            while not done:
                if marker:
                    response = cfr.list_distributions(Marker=marker)
                else:
                    response = cfr.list_distributions()

                dl = response['DistributionList']
                if dl['IsTruncated']:
                    marker = dl['NextMarker']
                else:
                    done = True

                if 'Items' in dl:
                    for dist in dl['Items']:
                        origins = []
                        for origin in dist['Origins']['Items']:
                            if 'S3OriginConfig' in origin:
                                origins.append({'type': 's3', 'source': origin['DomainName']})

                            elif 'CustomOriginConfig' in origin:
                                origins.append({'type': 'custom-http', 'source': origin['DomainName']})

                        data = {
                            'id': get_resource_id('cfd', dist['ARN']),
                            'arn': dist['ARN'],
                            'name': dist['DomainName'],
                            'origins': origins,
                            'enabled': dist['Enabled'],
                            'type': 'web',
                            'tags': self.__get_distribution_tags(cfr, dist['ARN'])
                        }
                        dists.append(data)
            # endregion

            # region Streaming distributions
            done = False
            marker = None
            while not done:
                if marker:
                    response = cfr.list_streaming_distributions(Marker=marker)
                else:
                    response = cfr.list_streaming_distributions()

                dl = response['StreamingDistributionList']
                if dl['IsTruncated']:
                    marker = dl['NextMarker']
                else:
                    done = True

                if 'Items' in dl:
                    for x in dl['Items']:
                        dists.append({
                            'id': get_resource_id('cfd', x['ARN']),
                            'arn': x['ARN'],
                            'name': x['DomainName'],
                            'origins': [{'type': 's3', 'source': x['S3Origin']['DomainName']}],
                            'enabled': x['Enabled'],
                            'type': 'rtmp',
                            'tags': self.__get_distribution_tags(cfr, x['ARN'])
                        })
            # endregion
        finally:
            del cfr
        # endregion

    @retry
    def __get_distribution_tags(self, client, arn):
        """Returns a dict containing the tags for a CloudFront distribution

        Args:
            client (botocore.client.CloudFront): Boto3 CloudFront client object
            arn (str): ARN of the distribution to get tags for

        Returns:
            `dict`
        """
        tags = client.list_tags_for_resource(Resource=arn).get('Tags').get('Items')
        return {tag['Key']: tag['Value'] for tag in tags}
