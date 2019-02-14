import json
import boto3
from datetime import date, datetime
from snucovery.errors import (
    UnknownServiceCall, InvalidServiceMappings,
)


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


class AwsServices:
    def __init__(self, profile):
        """Object for collecting Aws Assets

        Describe multiple services within an Aws profile.

        Args:
            profile (str): Aws profile name found in `~/.aws/credentials`

        Self Params:
            profile (str): profile name
            session (obj): Aws Session
            active_service (str): default('ec2')
            client (obj): Aws Service Client

        Examples:
            >>> from aws import AwsService
            >>> aws = AwsServices(profile='test')
            >>> print(aws.scan_services())
        """
        self.profile = profile
        self.session = self.get_session()
        self.active_service = 'ec2'
        self.client = self.get_service_client()

        self.service_mappings = {
            'ec2': {
                'describe_instances': ".Reservations[].Instances[] | {Name: (.Tags[]|select(.Key==\"Name\")|.Value), InstanceId, InstanceType, Region: .Placement.AvailabilityZone, LaunchTime, PrivateDnsName, PrivateIpAddresses: [.NetworkInterfaces[].PrivateIpAddresses[].PrivateIpAddress], PublicIpAddress}",
                'describe_vpcs': ".Vpcs[] | {Name: (.Tags[]|select(.Key==\"Name\")|.Value), VpcId, CidrBlock}"
            },
            'elb': {
                'describe_load_balancers': ".LoadBalancerDescriptions[] | {LoadBalancerName, DNSName}"
            },
            'rds': {
                'describe_db_instances': ".DBInstances[] | {DBName, AvailabilityZone, DBInstanceIdentifier, DBInstanceClass, Engine}"
            },
            'elasticache': {
                'describe_cache_clusters': ".CacheClusters[] | {CacheClusterId, CacheNodeType, Engine, PreferredAvailabilityZone}"
            }
        }

    def set_session(self, profile_name):
        """Set Aws Session

        Instantiates an Aws Session based on the `profile_name`.  The `profile_name`
        must exist within the `~/.aws/credentials` file.

        Args:
            profile_name (str): Aws profile name

        Returns:
            Object :: Boto3.session ( profile_name )
        """
        self.session = boto3.session.Session(profile_name=profile_name)
        if self.session:
            return self.session

    def set_service_client(self, service):
        """Instantiate a boto3.client based on the current session

        Args:
            service (str): Valid boto3.client() parameters.
                           eg: ['ec2', 'elb', 'rds']

        Returns:
            Object :: boto3.client object
        """
        self.client = self.get_session().client(service)
        return self.client

    def get_session(self):
        """Get the current boto3 session

        Attempts to return the current session, if it fails, it will set
        a new session based on the current `profile`

        Returns:
            Object :: boto3.session object
        """
        try:
            return self.session
        except AttributeError:
            return self.set_session(self.profile)

    def get_service_client(self):
        """Get the current Aws service client object

        Attempts to return the current boto3 client.  If it's not set, it will
        create a new service client based on the `active_service`

        Returns:
            Object :: boto3.client object
        """
        try:
            return self.client
        except AttributeError:
            return self.set_service_client(self.active_service)

    def get_service_mappings(self):
        """Get the aws service mappings

        THIS IS NOT THE FINAL FORM
        Need to think about this but it attempts to return the current service
        mappings.  Raises an error if invalid.  The mapping works as follows:

            boto3.client('ec2').describe_instances()
            service_mappings = {
                <service>: {
                    <service_attr>
                }
            }
            boto3.client(<service>).<service_attr>()

        Examples:
            >>> from aws import AwsService
            >>> aws = AwsServices(profile='test')
            >>> aws.service_mappings = {
            ...    'ec2': {
            ...        'describe_instances': ".Reservations[].Instances[] | {Name: (.Tags[]|select(.Key==\"Name\")|.Value), InstanceId, InstanceType, Region: .Placement.AvailabilityZone, LaunchTime, PrivateDnsName, PrivateIpAddresses: .NetworkInterfaces[].PrivateIpAddresses[].PrivateIpAddress, PublicIpAddress}",
            ...        'describe_vpcs': ".Vpcs[] | {Name: (.Tags[]|select(.Key==\"Name\")|.Value), VpcId, CidrBlock}"
            ...        }
            ...    }
            ...
            >>> aws.get_service_mappings()
        """
        if self.service_mappings:
            return self.service_mappings
        raise InvalidServiceMappings

    def scan_services(self):
        """Scan all aws services based on service_mappings

        Returns a ordered dictionary of each mapped service

        Returns:
            Dict :: Dictionary of all mapped aws services
        """
        service_response = dict()
        for service in self.get_service_mappings():
            self.set_service_client(service)
            for service_attr in self.service_mappings[service]:
                service_items = self.scan_service(service_attr)
                if service_items:
                    try:
                        service_response[service].update(
                            {
                                service_attr: service_items
                            }
                        )
                    except KeyError:
                        service_response[service] = dict()
                        service_response[service].update(
                            {
                                service_attr: service_items
                            }
                        )
        return service_response

    def scan_service(self, service_attr, service=None):
        """Scan a specific aws service and service_attr

        Scan service based on the service_attr.  The service attr is the
        service clients method. eg: boto3.client('ec2').describe_instances()

        Args:
            Required:
                service_attr (str): String version of a boto3.client('ec2')
                                    method
            Optional:
                service (str): default(None): If passed, will set a new
                               session client
        """
        if service:
            self.set_service_client(service)
        try:
            return json.loads(
                json.dumps(
                    getattr(self.get_service_client(), service_attr)(),
                    default=json_serial
                    )
                )
        except AttributeError:
            raise UnknownServiceCall
