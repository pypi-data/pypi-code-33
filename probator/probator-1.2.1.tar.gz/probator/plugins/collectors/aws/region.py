from datetime import datetime

from botocore.exceptions import ClientError
from munch import munchify

from probator.database import db
from probator.plugins.collectors.aws import AWSBaseRegionCollector
from probator.plugins.types.resources import (
    AMI, BeanStalk, EBSSnapshot, EBSVolume, EC2Instance, ELB, ENI, LoadBalancer, VPC, RDSInstance
)
from probator.utils import to_utc_date, isoformat
from probator.wrappers import retry, rollback


class AWSEC2InstanceCollector(AWSBaseRegionCollector):
    name = 'AWS EC2 Instance Collector'

    def run(self):
        self.update_instances()

    @rollback
    @retry
    def update_instances(self):
        """Update list of EC2 Instances for the account / region

        Returns:
            `None`
        """
        self.log.debug(f'Updating EC2Instances for {self.account.account_name}/{self.region}')
        ec2 = self.session.resource('ec2', region_name=self.region)

        try:
            existing_instances = EC2Instance.get_all(self.account, self.region)
            instances = {}
            api_instances = {x.id: x for x in ec2.instances.all()}

            for instance_id, instance_data in api_instances.items():
                tags = {tag['Key']: tag['Value'] for tag in instance_data.tags or {}}
                properties = {
                    'launch_date': to_utc_date(instance_data.launch_time).isoformat(),
                    'state': instance_data.state['Name'],
                    'instance_type': instance_data.instance_type,
                    'public_ip': getattr(instance_data, 'public_ip_address', None),
                    'public_dns': getattr(instance_data, 'public_dns_address', None),
                    'private_ip': instance_data.private_ip_address,
                    'private_dns': getattr(instance_data, 'private_dns_name', None),
                    'ami_id': instance_data.image_id
                }

                if instance_data.instance_id in existing_instances:
                    instance = existing_instances[instance_id]

                    if instance_data.state['Name'] not in ('terminated', 'shutting-down'):
                        instances[instance_id] = instance

                        # Add object to transaction if it changed
                        if instance.update_resource(properties=properties, tags=tags):
                            self.log.debug(f'Updating info for instance {instance}')
                            db.session.add(instance.resource)
                else:
                    # New instance, if its not in state=terminated
                    if instance_data.state['Name'] in ('terminated', 'shutting-down'):
                        continue

                    properties['created'] = isoformat(datetime.now())
                    instance = EC2Instance.create(
                        instance_data.instance_id,
                        account_id=self.account.account_id,
                        location=self.region,
                        properties=properties,
                        tags=tags
                    )

                    instances[instance.resource.resource_id] = instance
                    self.log.debug(f'Added new EC2Instance {instance}')

            # Check for deleted instances
            ik = set(list(instances.keys()))
            eik = set(list(existing_instances.keys()))

            for instance_id in eik - ik:
                instance = existing_instances[instance_id]
                self.log.debug(f'Deleted EC2Instance {instance}')
                db.session.delete(instance.resource)

            db.session.commit()

        finally:
            del ec2


class AWSEBSVolumeCollector(AWSBaseRegionCollector):
    name = 'AWS EBS Volume Collector'

    def run(self):
        self.update_volumes()

    @rollback
    @retry
    def update_volumes(self):
        """Update list of EBS Volumes for the account / region

        Returns:
            `None`
        """
        self.log.debug(f'Updating EBSVolumes for {self.account.account_name}/{self.region}')
        ec2 = self.session.resource('ec2', region_name=self.region)

        try:
            existing_volumes = EBSVolume.get_all(self.account, self.region)
            volumes = {x.id: x for x in ec2.volumes.all()}

            for data in list(volumes.values()):
                properties = {
                    'create_time': data.create_time,
                    'encrypted': data.encrypted,
                    'iops': data.iops or 0,
                    'kms_key_id': data.kms_key_id,
                    'size': data.size,
                    'state': data.state,
                    'snapshot_id': data.snapshot_id,
                    'volume_type': data.volume_type,
                    'attachments': sorted(x['InstanceId'] for x in data.attachments)
                }
                tags = {t['Key']: t['Value'] for t in data.tags or {}}

                if data.id in existing_volumes:
                    vol = existing_volumes[data.id]
                    if vol.update_resource(properties=properties, tags=tags):
                        self.log.debug(f'Changed detected for EBSVolume {vol}')

                else:
                    vol = EBSVolume.create(
                        data.id,
                        account_id=self.account.account_id,
                        location=self.region,
                        properties=properties,
                        tags=tags
                    )

                    self.log.debug(f'Added new EBSVolume {vol}')
            db.session.commit()

            vk = set(list(volumes.keys()))
            evk = set(list(existing_volumes.keys()))

            for volume_id in evk - vk:
                vol = existing_volumes[volume_id]
                self.log.debug(f'Deleted EBSVolume {vol}')
                db.session.delete(vol.resource)

            db.session.commit()

        finally:
            del ec2


class AWSEBSSnapshotCollector(AWSBaseRegionCollector):
    name = 'AWS EBS Snapshot Collector'

    def run(self):
        self.update_snapshots()

    @rollback
    @retry
    def update_snapshots(self):
        """Update list of EBS Snapshots for the account / region

        Returns:
            `None`
        """
        self.log.debug(f'Updating EBSSnapshots for {self.account.account_name}/{self.region}')
        ec2 = self.session.resource('ec2', region_name=self.region)

        try:
            existing_snapshots = EBSSnapshot.get_all(self.account, self.region)
            snapshots = {x.id: x for x in ec2.snapshots.filter(OwnerIds=[self.account.account_number])}

            for data in list(snapshots.values()):
                properties = {
                    'create_time': data.start_time,
                    'encrypted': data.encrypted,
                    'kms_key_id': data.kms_key_id,
                    'state': data.state,
                    'state_message': data.state_message,
                    'volume_id': data.volume_id,
                    'volume_size': data.volume_size,
                }
                tags = {t['Key']: t['Value'] for t in data.tags or {}}

                if data.id in existing_snapshots:
                    snapshot = existing_snapshots[data.id]
                    if snapshot.update_resource(properties=properties, tags=tags):
                        self.log.debug(f'Change detected for EBSSnapshot {snapshot}')

                else:
                    snapshot = EBSSnapshot.create(
                        data.id,
                        account_id=self.account.account_id,
                        location=self.region,
                        properties=properties,
                        tags=tags
                    )

                    self.log.debug(f'Added new EBSSnapshot {snapshot}')

            db.session.commit()

            vk = set(list(snapshots.keys()))
            evk = set(list(existing_snapshots.keys()))

            for snapshot_id in evk - vk:
                snapshot = existing_snapshots[snapshot_id]
                self.log.debug(f'Deleted EBSSnapshot {snapshot}')
                db.session.delete(snapshot.resource)

            db.session.commit()

        finally:
            del ec2


class AWSAMICollector(AWSBaseRegionCollector):
    name = 'AWS AMI Collector'

    def run(self):
        self.update_amis()

    @rollback
    @retry
    def update_amis(self):
        """Update list of AMIs for the account / region

        Returns:
            `None`
        """
        self.log.debug(f'Updating AMIs for {self.account.account_name}/{self.region}')
        ec2 = self.session.resource('ec2', region_name=self.region)

        try:
            existing_images = AMI.get_all(self.account, self.region)
            images = {x.id: x for x in ec2.images.filter(Owners=['self'])}

            for data in list(images.values()):
                properties = {
                    'architecture': data.architecture,
                    'description': data.description,
                    'name': data.name,
                    'platform': data.platform or 'Linux',
                    'state': data.state,
                }
                tags = {tag['Key']: tag['Value'] for tag in data.tags or {}}

                if data.id in existing_images:
                    ami = existing_images[data.id]
                    if ami.update_resource(properties=properties, tags=tags):
                        self.log.debug(f'Changed detected for AMI {ami}')
                else:
                    ami = AMI.create(
                        data.id,
                        account_id=self.account.account_id,
                        location=self.region,
                        properties=properties,
                        tags=tags
                    )

                    self.log.debug(f'Added new AMI {ami}')
            db.session.commit()

            # Check for deleted instances
            ik = set(list(images.keys()))
            eik = set(list(existing_images.keys()))

            for image_id in eik - ik:
                ami = existing_images[image_id]
                self.log.debug('Deleted AMI {ami}')
                db.session.delete(ami.resource)

            db.session.commit()

        finally:
            del ec2


class AWSBeanStalkCollector(AWSBaseRegionCollector):
    name = 'AWS BeanStalk Collector'

    def run(self):
        self.update_beanstalks()

    @rollback
    @retry
    def update_beanstalks(self):
        """Update list of Elastic BeanStalks for the account / region

        Returns:
            `None`
        """
        self.log.debug(f'Updating ElasticBeanStalk environments for {self.account.account_name}/{self.region}')
        ebclient = self.session.client('elasticbeanstalk', region_name=self.region)

        try:
            existing_beanstalks = BeanStalk.get_all(self.account, self.region)
            beanstalks = {}
            # region Fetch elastic beanstalks
            for env in ebclient.describe_environments(IncludeDeleted=False)['Environments']:
                # Only get information for HTTP (non-worker) Beanstalks
                if env['Tier']['Type'] == 'Standard':
                    if 'CNAME' in env:
                        beanstalks[env['EnvironmentId']] = {
                            'environment_arn': env['EnvironmentArn'],
                            'properties': {
                                'environment_name': env['EnvironmentName'],
                                'application_name': env['ApplicationName'],
                                'cname': env['CNAME']
                            }
                        }
            # endregion

            for beanstalk_id, data in beanstalks.items():
                properties = data['properties']
                tags = {
                    tag['Key']: tag['Value'] for tag in ebclient.list_tags_for_resource(
                        ResourceArn=data['environment_arn']
                    ).get('ResourceTags')
                }

                if beanstalk_id in existing_beanstalks:
                    beanstalk = existing_beanstalks[beanstalk_id]
                    if beanstalk.update_resource(properties=properties, tags=tags):
                        self.log.debug(f'Change detected for ElasticBeanStalk {beanstalk}')
                else:
                    beanstalk = BeanStalk.create(
                        beanstalk_id,
                        account_id=self.account.account_id,
                        location=self.region,
                        properties=properties,
                        tags=tags
                    )

                    self.log.debug(f'Added new ElasticBeanStalk {beanstalk}')
            db.session.commit()

            bk = set(beanstalks.keys())
            ebk = set(existing_beanstalks.keys())

            for resource_id in ebk - bk:
                beanstalk = existing_beanstalks[resource_id]
                self.log.debug(f'Deleted ElasticBeanStalk {beanstalk}')
                db.session.delete(beanstalk.resource)
            db.session.commit()

        finally:
            del ebclient


class AWSVPCCollector(AWSBaseRegionCollector):
    name = 'AWS VPC Collector'

    def run(self):
        self.update_vpcs()

    @rollback
    @retry
    def update_vpcs(self):
        """Update list of VPCs for the account / region

        Returns:
            `None`
        """
        self.log.debug(f'Updating VPCs for {self.account.account_name}/{self.region}')

        ec2 = self.session.resource('ec2', region_name=self.region)
        ec2_client = self.session.client('ec2', region_name=self.region)
        existing_vpcs = VPC.get_all(self.account, self.region)

        try:
            vpcs = {x.id: x for x in ec2.vpcs.all()}

            for data in vpcs.values():
                flow_logs = ec2_client.describe_flow_logs(
                    Filters=[
                        {
                            'Name': 'resource-id',
                            'Values': [data.vpc_id]
                        }
                    ]
                ).get('FlowLogs', None)

                if flow_logs and len(flow_logs) > 0:
                    log_status = flow_logs[0]['FlowLogStatus']
                    log_group = flow_logs[0]['LogGroupName']
                else:
                    log_status = 'UNDEFINED'
                    log_group = 'UNDEFINED'

                tags = {t['Key']: t['Value'] for t in data.tags or {}}
                properties = {
                    'cidr_v4': data.cidr_block,
                    'is_default': data.is_default,
                    'state': data.state,
                    'vpc_flow_logs_status': log_status,
                    'vpc_flow_logs_group': log_group
                }

                if data.id in existing_vpcs:
                    vpc = existing_vpcs[data.vpc_id]
                    if vpc.update_resource(properties=properties, tags=tags):
                        self.log.debug(f'Change detected for VPC {vpc}')
                else:
                    vpc = VPC.create(
                        data.id,
                        account_id=self.account.account_id,
                        location=self.region,
                        properties=properties,
                        tags=tags
                    )
                    self.log.debug(f'Added new VPC {vpc}')
            db.session.commit()

            # Removal of VPCs
            vk = set(vpcs.keys())
            evk = set(existing_vpcs.keys())

            for resource_id in evk - vk:
                vpc = existing_vpcs[resource_id]
                self.log.debug(f'Removed VPCs {vpc}')
                db.session.delete(vpc.resource)
            db.session.commit()

        finally:
            del ec2
            del ec2_client


class AWSClassicLoadBalancerCollector(AWSBaseRegionCollector):
    name = 'AWS Classic Load Balancer Collector'

    def run(self):
        self.update_elbs()

    @rollback
    @retry
    def update_elbs(self):
        """Update list of ELBs for the account / region

        Returns:
            `None`
        """
        self.log.debug(f'Updating ELBs for {self.account.account_name}/{self.region}')

        elb = self.session.client('elb', region_name=self.region)
        existing_elbs = ELB.get_all(self.account, self.region)

        try:
            elbs_from_api = {}

            # region Collect Load Balancers
            done = False
            marker = None
            while not done:
                if marker:
                    response = elb.describe_load_balancers(Marker=marker)
                else:
                    response = elb.describe_load_balancers()

                if 'NextMarker' in response:
                    marker = response['NextMarker']
                else:
                    done = True

                for lb in response.get('LoadBalancerDescriptions', []):
                    elb_id = f'elb-{self.account.account_name}:{self.region}:{lb["LoadBalancerName"]}'
                    elbs_from_api[elb_id] = lb

            # endregion

            # Process ELBs known to AWS
            for elb_identifier in elbs_from_api:
                data = elbs_from_api[elb_identifier]

                tags = {tag['Key']: tag['Value'] for tag in data.get('Tags', {})}
                properties = {
                    'name': data['LoadBalancerName'],
                    'dns_name': data['DNSName'],
                    'instances': sorted(instance['InstanceId'] for instance in data['Instances']),
                    'vpc_id': data.get('VPCId', 'no vpc'),
                    'state': 'not_reported',
                    'canonical_hosted_zone_name': data.get('CanonicalHostedZoneName', None)
                }

                if elb_identifier in existing_elbs:
                    elb = existing_elbs[elb_identifier]
                    if elb.update_resource(properties=properties, tags=tags):
                        self.log.debug(f'Updating info for ELB {elb}')
                        db.session.add(elb.resource)
                else:
                    elb = ELB.create(
                        elb_identifier,
                        account_id=self.account.account_id,
                        location=self.region,
                        properties=properties,
                        tags=tags
                    )

                    self.log.debug(f'Added new ELB {elb}')

            # Delete no longer existing ELBs
            elb_keys_from_db = set(list(existing_elbs.keys()))
            elb_keys_from_api = set(list(elbs_from_api.keys()))

            for elb_identifier in elb_keys_from_db - elb_keys_from_api:
                elb = existing_elbs[elb_identifier]
                self.log.debug('Deleted ELB {elb}')
                db.session.delete(elb.resource)
            db.session.commit()

        finally:
            del elb


class AWSLoadBalancerCollector(AWSBaseRegionCollector):
    name = 'AWS Load Balancer Collector'

    def run(self):
        self.update_lbs()

    @rollback
    @retry
    def update_lbs(self):
        """Update list of Load Balancers

        Returns:
            `None`
        """
        self.log.debug(f'Updating Load Balancers for {self.account.account_name}/{self.region}')

        elb = self.session.client('elbv2', region_name=self.region)
        existing_lbs = LoadBalancer.get_all(self.account, self.region)
        try:
            lbs_from_api = {}

            # region Collect Load Balancers
            done = False
            marker = None
            while not done:
                if marker:
                    response = elb.describe_load_balancers(Marker=marker)
                else:
                    response = elb.describe_load_balancers()

                if 'NextMarker' in response:
                    marker = response['NextMarker']
                else:
                    done = True

                for lb in response.get('LoadBalancers', []):
                    elb_id = f'awslb-{self.account.account_name}:{self.region}:{lb["LoadBalancerName"]}'
                    lbs_from_api[elb_id] = lb
            # endregion

            # Process ELBs known to AWS
            for lb_identifier, data in lbs_from_api.items():
                tags = {tag['Key']: tag['Value'] for tag in data.get('Tags', {})}
                properties = {
                    'arn': data['LoadBalancerArn'],
                    'name': data['LoadBalancerName'],
                    'dns_name': data['DNSName'],
                    'vpc_id': data.get('VpcId'),
                    'state': data['State']['Code'],
                    'scheme': data['Scheme'],
                    'type': data['Type'],
                }

                if lb_identifier in existing_lbs:
                    elb = existing_lbs[lb_identifier]
                    if elb.update_resource(properties=properties, tags=tags):
                        self.log.debug(f'Updating info for Load Balancer {elb}')
                        db.session.add(elb.resource)
                else:
                    resource_id = f'awslb-{self.account.account_name}:{self.region}:{data["LoadBalancerName"]}'

                    elb = LoadBalancer.create(
                        resource_id,
                        account_id=self.account.account_id,
                        location=self.region,
                        properties=properties,
                        tags=tags
                    )

                    self.log.debug(f'Added new Load Balancer {elb}')

            # Delete no longer existing ELBs
            lb_keys_from_db = set(list(existing_lbs.keys()))
            lb_keys_from_api = set(list(lbs_from_api.keys()))

            for lb_identifier in lb_keys_from_db - lb_keys_from_api:
                lb = existing_lbs[lb_identifier]
                self.log.debug(f'Deleted Load Balancer {lb}')
                db.session.delete(lb.resource)
            db.session.commit()

        finally:
            del elb


class AWSENICollector(AWSBaseRegionCollector):
    name = 'AWS ENI Collector'

    def run(self):
        self.update_enis()

    @rollback
    @retry
    def update_enis(self):
        self.log.debug(f'Updating ENIs for {self.account.account_name}/{self.region}')

        ec2 = self.session.resource('ec2', region_name=self.region)
        existing_enis = ENI.get_all(self.account, self.region)

        try:
            enis = {x.id: x for x in ec2.network_interfaces.all()}
            for iface in enis.values():
                instance_id = None
                if iface.attachment:
                    instance_id = iface.attachment.get('InstanceId', None)

                public_ip = None
                if iface.association_attribute:
                    public_ip = iface.association_attribute.get('PublicIp', None)

                secondary_ips = [ip['PrivateIpAddress'] for ip in iface.private_ip_addresses if not ip['Primary']]

                tags = {tag['Key']: tag['Value'] for tag in iface.tag_set or {}}
                properties = {
                    'vpc_id': iface.vpc_id,
                    'instance_id': instance_id,
                    'status': iface.status,
                    'primary_ip': iface.private_ip_address,
                    'secondary_ips': secondary_ips,
                    'public_ip': public_ip,
                    'attachment_owner': iface.attachment.get('InstanceOwnerId') if iface.attachment else None,
                    'description': iface.description,
                }
                if iface.id in existing_enis:
                    eni = existing_enis[iface.id]
                    if eni.update_resource(properties=properties, tags=tags):
                        self.log.debug(f'Change detected for ENI {eni}')
                else:
                    eni = ENI.create(
                        iface.id,
                        account_id=self.account.account_id,
                        location=self.region,
                        properties=properties,
                        tags=tags
                    )

                    self.log.debug(f'Added new ENI {eni}')

            db.session.commit()

            eni_keys = set(list(enis.keys()))
            existing_eni_keys = set(list(existing_enis.keys()))

            for eni_id in existing_eni_keys - eni_keys:
                eni = existing_enis[eni_id]
                self.log.debug(f'Deleted ENI {eni}')
                db.session.delete(eni.resource)

            db.session.commit()
        finally:
            del ec2


class AWSRDSCollector(AWSBaseRegionCollector):
    name = 'AWS RDS Collector'

    def run(self):
        self.update_rds_instances()

    @rollback
    @retry
    def update_rds_instances(self):
        self.log.debug(f'Updating RDS Instances for {self.account.account_name}/{self.region}')

        rds = self.session.client('rds', region_name=self.region)
        existing_instances = RDSInstance.get_all(self.account, self.region)
        api_instances = self._get_instances()

        try:
            for arn, data in api_instances.items():
                tags = self._get_resource_tags(data.DBInstanceArn)
                properties = {
                    'instance_identifier': data.DBInstanceIdentifier,
                    'instance_class': data.DBInstanceClass,
                    'status': data.DBInstanceStatus,
                    'dbname': data.DBName,
                    'allocated_storage': data.AllocatedStorage,
                    'multi_az': data.MultiAZ,
                    'engine': data.Engine,
                    'engine_version': data.EngineVersion,
                    'encrypted': data.StorageEncrypted,
                }

                if data.DBInstanceArn in existing_instances:
                    instance = existing_instances[data.DBInstanceArn]
                    if instance.update_resource(properties=properties, tags=tags):
                        self.log.debug(f'Changed detected for RDS Instance {instance}')

                else:
                    instance = RDSInstance.create(
                        resource_id=data.DBInstanceArn,
                        account_id=self.account.account_id,
                        location=self.region,
                        properties=properties,
                        tags=tags
                    )
                    self.log.debug(f'Added new RDS Instance {instance}')

                db.session.commit()

                existing_rds_keys = set(existing_instances.keys())
                api_rds_keys = set(api_instances.keys())

                for arn in existing_rds_keys - api_rds_keys:
                    db_inst = existing_instances[arn]
                    self.log.debug(f'Deleted RDS Instance {db_inst}')
                    db.session.delete(db_inst.resource)
                db.session.commit()
        finally:
            del rds

    @retry
    def _get_instances(self):
        instances = {}
        rds = self.session.client('rds', region_name=self.region)
        try:
            done = False
            marker = None

            while not done:
                if marker:
                    response = rds.describe_db_instances(Marker=marker)
                else:
                    response = rds.describe_db_instances()

                if 'Marker' in response:
                    marker = response['Marker']
                else:
                    done = True

                for instance in response.get('DBInstances', []):
                    instances[instance['DBInstanceArn']] = munchify(instance)

            return instances

        finally:
            del rds

    @retry
    def _get_resource_tags(self, instance_arn):
        """Return a list of tags for a given RDS Instance

        Args:
            instance_arn:

        Returns:

        """
        rds = self.session.client('rds', region_name=self.region)

        try:
            response = rds.list_tags_for_resource(ResourceName=instance_arn)
            return {tag['Key']: tag['Value'] for tag in response.get('TagList', [])}

        except ClientError as ex:
            rex = ex.response['Error']['Code']
            if rex == 'InvalidParameterValue':
                return {}
