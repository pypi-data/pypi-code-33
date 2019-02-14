import abc
import asyncio
import boto3
import concurrent
import itertools
from collections import defaultdict
from functools import partial

from grapher.core import driver
from grapher.core.constants import (UNAUTHORIZED, LINKS_WITH_CYCLE)

from grapher.aws.pricedb import PRICING_DATABASE


REGIONS = (
    'us-east-1', 'us-east-2', 'us-west-1','us-west-2', 'eu-west-3', 'ca-central-1', 'eu-west-1',
    'eu-central-1', 'eu-west-2', 'sa-east-1', 'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1', 'ap-northeast-3',
    'ap-northeast-2', 'ap-south-1', 'eu-north-1'
)
EC2_TYPE = 'ec2'
SUBNET_TYPE = 'subnet'
ELB_TYPE = 'elb'
TAGS_TYPE = 'tags'
SG_TYPE = 'sg'
ASG_TYPE = 'autoscaling'
LINK_TYPE = 'link'
REGION_TYPE = 'region'
VPC_TYPE = 'vpc'

EC2_ID_NAME = 'InstanceId'
ELB_ID_NAME = 'LoadBalancerName'
TAGS_ID_NAME = 'Value'
SG_ID_NAME = 'GroupId'
ASG_ID_NAME = 'AutoScalingGroupName'
VPC_ID_NAME = 'VpcId'
SUBNET_ID_NAME = 'SubnetId'

ITEM_ID_FIELD = 'key'
LINK_PID_FIELD = 'from'
LINK_ID_FIELD = 'to'
ITEM_TYPE_FIELD = 'category'
ITEM_NAME_FIELD = 'Name'

FUTURE_WAIT_TIMEOUT = 500

# Items in an array.
CHUNK_SIZE = 500

# INFO: general format for commands:
#       data types=ec2
#       data types=ec2,elb

# driver should return empty list: [], list with results: [{}, {}], dictionary with error:
#  {'error': ERROR_DESCRIPTION}


def has_cycles(vertices):
    links = set()
    if not vertices:
        return False
    for t in vertices.split(','):
        edge = tuple(sorted(t.split(':')))
        if edge[0] == edge[1]:
            return True
        if edge not in links:
            links.add(edge)
            continue
        else:
            return True
    return False


def start_loop(callback):
    executor = concurrent.futures.ThreadPoolExecutor(
        max_workers=len(REGIONS)
    )
    loop = asyncio.get_event_loop()
    return [
        loop.run_in_executor(executor, partial(callback, r))
        for r in REGIONS
    ]


class FormatterMixin:
    @staticmethod
    def format_link(cid, pid):
        return {ITEM_TYPE_FIELD: LINK_TYPE, LINK_ID_FIELD: cid, LINK_PID_FIELD: pid}

    def format_data(self, inst, data):
        data = {
            ITEM_ID_FIELD: data[inst.field_id_name],
            ITEM_TYPE_FIELD: inst.inst_type,
            ITEM_NAME_FIELD: data[inst.field_id_name]
        }
        data.update(data)
        return data


class EC2PriceFormatterMixin(FormatterMixin):
    @staticmethod
    def get_price(inst_region, platform, instance_type):
        return PRICING_DATABASE[inst_region.lower()][platform.lower()][instance_type.lower()]

    def format_data(self, inst, data):
        updated = super().format_data(inst, data)
        try:
            updated['price'] = self.get_price(
                data['Placement']['AvailabilityZone'],
                data['Platform'],
                data['InstanceType']
            )
        except KeyError:
            updated['price'] = 0.00
        return updated


class Fetcher(abc.ABC):
    inst_type = None
    field_id_name = None
    formatter = FormatterMixin()

    @abc.abstractmethod
    async def _extract_data(self, response, inst_region):
        yield await None

    @abc.abstractmethod
    async def _instances(self, session, inst_region):
        pass

    def __init__(self, keys, links, flt=None):
        self.links = links
        self.keys = keys
        self.fltr = eval('lambda i: {}'.format(flt)) if flt else None

        if self.fltr:
            assert isinstance(self.fltr, type(lambda x: x))

    def fetch(self, inst_region):
        from timeit import default_timer as timer
        cur = timer()
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        res = loop.run_until_complete(partial(self._fetch, inst_region)())
        print('Region: {}, inst_type - {}, time {}'.format(inst_region, self.inst_type, timer() - cur))
        return res

    def _get_links_queue(self, _from, _to):
        return self.links[tuple([_from, _to])]

    def _format_link(self, cid, pid):
        return self.formatter.format_link(cid, pid)

    async def _format(self, instance):
        return self.formatter.format_data(self, instance)

    async def _fetch(self, inst_region):
        try:
            session = boto3.session.Session(
                aws_access_key_id=self.keys[0], aws_secret_access_key=self.keys[1]
            )

            response = await self._instances(session, inst_region)
            if self.fltr:
                return [i async for i in self._extract_data(response, inst_region) if self.fltr(i)]
            return [i async for i in self._extract_data(response, inst_region)]
        except BaseException as err:
            print(err)
            return {'error': UNAUTHORIZED}


class EC2Fetcher(Fetcher):
    inst_type = EC2_TYPE
    field_id_name = EC2_ID_NAME
    formatter = EC2PriceFormatterMixin()

    async def _extract_data(self, response, inst_region):
        links_queue = self._get_links_queue(EC2_TYPE, SG_TYPE)
        sg_links = self._get_links_queue(SG_TYPE, EC2_TYPE)
        region_links = self._get_links_queue(REGION_TYPE, EC2_TYPE)
        vpc_links = self._get_links_queue(VPC_TYPE, EC2_TYPE)
        for rec in response['Reservations']:
            for instance in rec['Instances']:
                region_links.append(self._format_link(
                    instance[EC2_ID_NAME], inst_region)
                )
                # Stopped instances don't have VPC ID.
                if instance.get(VPC_ID_NAME):
                    vpc_links.append(self._format_link(
                        instance[EC2_ID_NAME], instance[VPC_ID_NAME])
                    )
                for i in instance['SecurityGroups']:
                    links_queue.append(self._format_link(i[SG_ID_NAME], instance[EC2_ID_NAME]))
                    sg_links.append(self._format_link(instance[EC2_ID_NAME], i[SG_ID_NAME]))

                yield await self._format(instance)

    async def _instances(self, session, inst_region):
        return session.client(self.inst_type, region_name=inst_region).describe_instances()


class RegionFetcher(Fetcher):
    inst_type = REGION_TYPE

    async def _extract_data(self, response, inst_region):
        pass

    async def _instances(self, session, inst_region):
        pass

    def fetch(self, inst_region):
        return [{
            ITEM_ID_FIELD: inst_region,
            ITEM_TYPE_FIELD: self.inst_type,
            ITEM_NAME_FIELD: inst_region
        }]


class ASGFetcher(Fetcher):
    inst_type = ASG_TYPE
    field_id_name = ASG_ID_NAME

    async def _extract_data(self, response, inst_region):
        links_queue = self._get_links_queue(EC2_TYPE, ASG_TYPE)

        for rec in response['AutoScalingGroups']:
            for i in rec['Instances']:
                links_queue.append(self._format_link(i[EC2_ID_NAME], rec[ASG_ID_NAME]))

            yield await self._format(rec)

    async def _instances(self, session, inst_region):
        return session.client(self.inst_type, region_name=inst_region).describe_auto_scaling_groups()


class ELBFetcher(Fetcher):
    inst_type = ELB_TYPE
    field_id_name = ELB_ID_NAME

    async def _extract_data(self, response, inst_region):
        elb_queue = self._get_links_queue(ELB_TYPE, EC2_TYPE)
        ec2_queue = self._get_links_queue(EC2_TYPE, ELB_TYPE)
        sg_queue = self._get_links_queue(ELB_TYPE, SG_TYPE)
        elb_sg_queue = self._get_links_queue(SG_TYPE, ELB_TYPE)
        region_links = self._get_links_queue(REGION_TYPE, ELB_TYPE)

        for instance in response['LoadBalancerDescriptions']:
            region_links.append(self._format_link(
                instance[ELB_ID_NAME], inst_region)
            )
            # Fill ec2 links.
            for i in instance['Instances']:
                elb_queue.append(self._format_link(i[EC2_ID_NAME], instance[ELB_ID_NAME]))
                ec2_queue.append(self._format_link(instance[ELB_ID_NAME], i[EC2_ID_NAME]))

            # Fill sg links.
            for i in instance['SecurityGroups']:
                sg_queue.append(self._format_link(i, instance[ELB_ID_NAME]))
                elb_sg_queue.append(self._format_link(instance[ELB_ID_NAME], i))

            yield await self._format(instance)

    async def _instances(self, session, inst_region):
        return session.client(self.inst_type, region_name=inst_region).describe_load_balancers()


class TAGSFetcher(Fetcher):
    inst_type = TAGS_TYPE

    async def _extract_data(self, response, inst_region):
        result = set()
        for tag in response['Tags']:
            key, value = tag['Key'], tag['Value']
            if key.isalpha():
                queue_type = 'tags-{}'.format(key.lower().strip())
                queue = self._get_links_queue(EC2_TYPE, queue_type)
                queue.append(self._format_link(tag['ResourceId'], value))
            result.add((key, value))

        for key, val in result:
            yield {ITEM_ID_FIELD: val, ITEM_TYPE_FIELD: self.inst_type, 'Key': key, 'Value': val}

    async def _instances(self, session, inst_region):
        return session.client(EC2_TYPE, region_name=inst_region).describe_tags(
            Filters=[{'Name': 'resource-type', 'Values': ['instance']}]
        )


class SGFetcher(Fetcher):
    inst_type = SG_TYPE
    field_id_name = SG_ID_NAME

    async def _extract_data(self, response, inst_region):
        region_links = self._get_links_queue(REGION_TYPE, SG_TYPE)

        for inst_sg in response['SecurityGroups']:
            region_links.append(self._format_link(
                inst_sg[SG_ID_NAME], inst_region)
            )
            yield await self._format(inst_sg)

    async def _instances(self, session, inst_region):
        return session.client(EC2_TYPE, region_name=inst_region).describe_security_groups()


class VPCFetcher(Fetcher):
    inst_type = VPC_TYPE
    field_id_name = VPC_ID_NAME

    async def _extract_data(self, response, inst_region):
        region_links = self._get_links_queue(REGION_TYPE, VPC_TYPE)

        for inst_vpc in response['Vpcs']:
            region_links.append(self._format_link(
                inst_vpc[VPC_ID_NAME], inst_region)
            )

            yield await self._format(vpc)

    async def _instances(self, session, inst_region):
        return session.client(EC2_TYPE, region_name=inst_region).describe_vpcs()


class SubnetFetcher(Fetcher):
    inst_type = SUBNET_TYPE
    field_id_name = SUBNET_ID_NAME

    async def _extract_data(self, response, inst_region):
        vpc_links = self._get_links_queue(VPC_TYPE, SUBNET_TYPE)
        region_links = self._get_links_queue(REGION_TYPE, SUBNET_TYPE)
        for inst_subnet in response['Subnets']:
            vpc_links.append(self._format_link(inst_subnet[self.field_id_name], inst_subnet['VpcId']))
            region_links.append(self._format_link(inst_subnet[self.field_id_name], inst_region))
            yield await self._format(inst_subnet)

    async def _instances(self, session, inst_region):
        return session.client(EC2_TYPE, region_name=inst_region).describe_subnets()


def ec2(keys, links, fltr):
    """Returns generator with a task results as soon as completed."""
    return start_loop(EC2Fetcher(keys, links, fltr).fetch)


def region(keys, links, fltr):
    """Returns generator with a task results as soon as completed."""
    return start_loop(RegionFetcher(keys, links, fltr).fetch)


def elb(keys, links, fltr):
    return start_loop(ELBFetcher(keys, links, fltr).fetch)


def tags(keys, links, fltr):
    return start_loop(TAGSFetcher(keys, links, fltr).fetch)


def sg(keys, links, fltr):
    return start_loop(SGFetcher(keys, links, fltr).fetch)


def asg(keys, links, fltr):
    return start_loop(ASGFetcher(keys, links, fltr).fetch)


def vpc(keys, links, fltr):
    return start_loop(VPCFetcher(keys, links, fltr).fetch)


def subnet(keys, links, fltr):
    return start_loop(SubnetFetcher(keys, links, fltr).fetch)


COLLECTORS = {
    EC2_TYPE: ec2,
    SUBNET_TYPE: subnet,
    ELB_TYPE: elb,
    TAGS_TYPE: tags,
    SG_TYPE: sg,
    ASG_TYPE: asg,
    REGION_TYPE: region,
    VPC_TYPE: vpc
}


class AWSDriver(driver.AbstractDriver):

    def auth(self, key, secret):
        self.keys = key, secret
        self.collected_links = defaultdict(list)

    async def data(self, **kwargs):
        """
        This method should return list of dicts.
        
        :param types: string with a comma separated values: a,b,c 
        :param links: list of comma separated links - ec2:elb, ec2:sg. No cycles are allowed.
        :param kwargs: is a dict with a filters like - ec2="attr1 == 1", elb="attr2 == 2"   
        :return: generator
        """
        types = kwargs['types']
        link_types = kwargs.get('links')
        self.collected_links = defaultdict(list)

        if has_cycles(link_types):
            yield [{'error': LINKS_WITH_CYCLE}]
            return

        filters = {
            key: val for key, val in kwargs.items() if key in COLLECTORS
        }
        aws_types = types.split(',')
        futures = (
            COLLECTORS[aws_type](self.keys, self.collected_links, filters.get(aws_type)) for aws_type in aws_types
                if aws_type in COLLECTORS
        )

        for future in asyncio.as_completed(itertools.chain.from_iterable(futures)):
            result = await asyncio.wait_for(future, timeout=FUTURE_WAIT_TIMEOUT)
            for i in range(0, len(result), CHUNK_SIZE):
                yield result[i:i + CHUNK_SIZE]

        if link_types:
            links = link_types.split(',')
            for link in links:
                type1, type2 = link.split(':')
                data = self.collected_links[tuple([type1, type2])]
                for i in range(0, len(data), CHUNK_SIZE):
                    yield data[i:i + CHUNK_SIZE]
                self.collected_links[tuple([type1, type2])] = []

    async def info(self):
        yield [{
            'driver': 'aws',
            'available_links': ', '.join(['{}:{}'.format(t1, t2) for t1, t2 in self.collected_links])
        }]
