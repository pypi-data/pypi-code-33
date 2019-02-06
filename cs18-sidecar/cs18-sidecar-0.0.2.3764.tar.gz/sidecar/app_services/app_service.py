import json
import threading
from abc import ABCMeta, abstractmethod
from logging import Logger
from typing import Optional, List

import more_itertools

from sidecar.app_instance_identifier import AppInstanceIdentifier
from sidecar.aws_session import AwsSession
from sidecar.aws_status_maintainer import AWSStatusMaintainer
from sidecar.aws_tag_helper import AwsTagHelper
from sidecar.const import Const, get_app_selector
from sidecar.kub_api_service import IKubApiService
from sidecar.utils import Utils, CallsLogger


class StaleAppException(Exception):
    pass


class AppService:
    __metaclass__ = ABCMeta

    def __init__(self, logger: Logger):
        self._logger = logger

    @abstractmethod
    def update_network_status(self, app_name: str, status: str):
        raise NotImplementedError

    @abstractmethod
    def get_private_dns_name_by_app_name(self, app_name: str, infra_id: str) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def get_public_dns_name_by_app_name(self, app_name: str, infra_id: str, address_read_timeout: int) -> str:
        raise NotImplementedError

    @abstractmethod
    def try_open_firewall_access_to_instances(self, identifier: AppInstanceIdentifier) -> bool:
        """
        allows public access to sidecar to the instances
        :param identifier:
        :return: whether public access was required
        """
        raise NotImplementedError


class AzureAppService(AppService):
    def __init__(self, logger: Logger):
        super().__init__(logger)

    def update_network_status(self, app_name: str, status: str):
        pass

    def get_private_dns_name_by_app_name(self, app_name: str, infra_id: str) -> Optional[str]:
        pass

    def get_public_dns_name_by_app_name(self, app_name: str, infra_id: str, address_read_timeout: int) -> str:
        pass

    def try_open_firewall_access_to_instances(self, identifier: AppInstanceIdentifier) -> bool:
        return False


class K8sAppService(AppService):
    def __init__(self, api: IKubApiService, sandbox_id: str, own_public_ip: str, logger: Logger):
        super().__init__(logger)
        self._own_public_ip = own_public_ip
        self.sandbox_id = sandbox_id
        self._api = api
        self._lock = threading.RLock()

    @CallsLogger.wrap
    def try_open_firewall_access_to_instances(self, identifier: AppInstanceIdentifier) -> bool:
        return True

    @CallsLogger.wrap
    def get_private_dns_name_by_app_name(self, app_name: str, infra_id: str) -> Optional[str]:
        service = self._get_service_by_app_name(app_name=app_name)
        return "{}.{}".format(service['metadata']['name'], self.sandbox_id)

    @CallsLogger.wrap
    def get_public_dns_name_by_app_name(self, app_name: str, infra_id: str, address_read_timeout: int) -> str:
        dns_name = Utils.retry_on_exception(func=lambda: self._get_public_dns_name_by_app_name(app_name=app_name),
                                            timeout_in_sec=address_read_timeout,
                                            logger=self._logger,
                                            logger_msg="trying to get public dns for app '{}'.".format(app_name))
        return dns_name

    def _get_public_dns_name_by_app_name(self, app_name: str) -> Optional[str]:
        service = self._get_service_by_app_name(app_name=app_name)
        if service["spec"]["type"] != "LoadBalancer":
            return None

        if "status" not in service:
            raise StaleAppException(
                "Cannot get public dns of '{app_name}' "
                "since the service exposing does not have 'status' yet. "
                "service details: {service_details}".format(app_name=app_name, service_details=json.dumps(service)))

        if "loadBalancer" not in service["status"]:
            raise StaleAppException(
                "Cannot get public dns of '{app_name}' "
                "since the service exposing does not have 'status.loadBalancer' yet. "
                "service details: {service_details}".format(app_name=app_name, service_details=json.dumps(service)))

        load_balancer = service["status"]['loadBalancer']
        if "ingress" not in load_balancer:
            raise StaleAppException(
                "Cannot get public dns of '{app_name}' "
                "since the service exposing "
                "does not have 'status.loadBalancer.ingress' yet. "
                "service details: {service_details}".format(
                    app_name=app_name, service_details=json.dumps(service)))

        ingress = next(iter(load_balancer['ingress']), None)
        if ingress and "ip" not in ingress and "hostname" not in ingress:
            raise StaleAppException(
                "Cannot get public dns of '{app_name}' "
                "since the service exposing "
                "does not have 'status.loadBalancer.ingress.ip' or 'status.loadBalancer.ingress.hostname' yet. "
                "service details: {service_details}".format(
                    app_name=app_name, service_details=json.dumps(service)))

        return ingress['ip'] if "ip" in ingress else ingress['hostname']

    @CallsLogger.wrap
    def update_network_status(self, app_name: str, status: str):
        # TODO: rethink it !!! not so good to mark both services when only one got checked
        app_services = [service for service in self._api.get_all_services()
                        if service['spec']['selector'] == {**{get_app_selector(app_name): app_name}}]

        for app_service in app_services:
            annotations = app_service['metadata']['annotations']
            if app_service['metadata'][
                'annotations'] is None or Const.HEALTH_CHECK_STATUS not in annotations:  # backward compatibility
                annotations = {Const.HEALTH_CHECK_STATUS: status}
            else:
                annotations[Const.HEALTH_CHECK_STATUS] = status
            self._api.update_service(name=app_service['metadata']['name'], data={
                'metadata': {
                    'annotations': annotations
                }
            })

    def _get_service_by_app_name(self, app_name: str) -> dict:
        services = self._api.get_all_services()
        service = next(
            iter([service for service in services if
                  service['spec']['selector'] == {**{get_app_selector(app_name): app_name}}]),
            None)
        if service is None:
            raise StaleAppException(
                "Cannot get '{app_name}' since the service exposing it does not exists.".format(
                    app_name=app_name))

        return service


class AWSAppService(AppService):
    PUBLIC_PORT_ACCESS = "public port access"
    PUBLIC_HEALTH_CHECK = "public health check"

    def __init__(self, session: AwsSession,
                 own_public_ip: str,
                 sandbox_id: str,
                 logger: Logger,
                 default_region: str = None):

        super().__init__(logger)
        self.default_region = default_region
        self._own_public_ip = own_public_ip
        self._sandbox_id = sandbox_id
        self._session = session
        self._lock = threading.RLock()

    @CallsLogger.wrap
    def update_network_status(self, app_name: str, status: str):
        table, item = Utils.retry_on_exception(
            func=lambda: self._get_table(sandbox_id=self._sandbox_id),
            logger=self._logger,
            logger_msg="cannot get public dns for app '{}'.".format(app_name))

        if 'logical-apps' not in item:  # backward compatibility
            item["logical-apps"] = {**{app_name: {Const.HEALTH_CHECK_STATUS: status}}}
        else:
            item["logical-apps"][app_name][Const.HEALTH_CHECK_STATUS] = status

        response = table.update_item(
            Key={Const.SANDBOX_ID_TAG: self._sandbox_id},
            UpdateExpression='set #col = :r',
            ExpressionAttributeValues={':r': item["logical-apps"]},
            ExpressionAttributeNames={"#col": "logical-apps"},
            ReturnValues="UPDATED_NEW"
        )
        if AWSStatusMaintainer.response_failed(response):
            self._logger.info("Error update_network_status(app_name: '{}', status: {})\n"
                              "Response: {}".format(app_name, status, response))

    @CallsLogger.wrap
    def try_open_firewall_access_to_instances(self, identifier: AppInstanceIdentifier) -> bool:

        with self._lock:  # restrict to 1 instance at the time
            ec2 = self._session.get_ec2_resource()

            instance = ec2.Instance(identifier.infra_id)
            security_group_ids = [sg["GroupId"] for sg in instance.security_groups]

            # might be auto scaling group
            if AwsTagHelper.safely_get_tag(instance, Const.EXTERNAL_ELB_DNS_NAME, logger=self._logger):
                security_group_ids = self._get_auto_scaling_group_elb(instance)

            public_access = False

            for security_group_id in security_group_ids:
                permissions = ec2.SecurityGroup(security_group_id).ip_permissions
                external_ports = [port
                                  for port in permissions
                                  if len(port["IpRanges"]) > 0 and len([ip
                                                                        for ip in port["IpRanges"]
                                                                        if "Description" in ip and ip[
                                                                            "Description"] == self.PUBLIC_PORT_ACCESS]) > 0]
                if not external_ports:
                    continue

                sidecar_public_cidr = "{}/32".format(self._own_public_ip.rstrip('\n'))

                new_permissions = []
                for external_port in external_ports:
                    if sidecar_public_cidr in [cidr["CidrIp"] for cidr in external_port["IpRanges"]]:
                        continue

                    new_permissions.append({'IpProtocol': 'tcp',
                                            'FromPort': external_port["FromPort"],
                                            'ToPort': external_port["ToPort"],
                                            'IpRanges': [{
                                                'CidrIp': sidecar_public_cidr,
                                                'Description': self.PUBLIC_HEALTH_CHECK}]})

                if not new_permissions:
                    continue

                self._session.get_ec2_client().authorize_security_group_ingress(
                    GroupId=security_group_id,
                    IpPermissions=new_permissions)

                public_access = True

            return public_access

    @CallsLogger.wrap
    def get_private_dns_name_by_app_name(self, app_name: str, infra_id: str) -> Optional[str]:
        instance = self._session.get_ec2_resource().Instance(infra_id)
        internal_ports = AwsTagHelper.safely_get_tag(resource=instance,
                                                     tag_name=Const.INTERNAL_PORTS,
                                                     logger=self._logger)

        if internal_ports:
            return "{}.{}.sandbox.com".format(app_name, self._sandbox_id)
        else:
            return None

    @CallsLogger.wrap
    def get_public_dns_name_by_app_name(self, app_name: str, infra_id: str, address_read_timeout: int) -> str:
        return Utils.retry_on_exception(func=lambda: self._get_public_dns_name_by_instance_id(instance_id=infra_id),
                                        timeout_in_sec=address_read_timeout,
                                        logger=self._logger,
                                        logger_msg="trying to get public dns for app '{}'.".format(app_name))

    def _get_table(self, sandbox_id: str):
        dynamo_resource = self._session.get_dynamo_resource(default_region=self.default_region)
        table = dynamo_resource.Table(AWSStatusMaintainer.default_table_name)
        item = table.get_item(Key={Const.SANDBOX_ID_TAG: sandbox_id})
        if "Item" not in item:
            raise Exception("dynamodb table is not ready yet")
        return table, item["Item"]

    def _get_public_dns_name_by_instance_id(self, instance_id: str):
        instance = self._session.get_ec2_resource().Instance(instance_id)
        dns = AwsTagHelper.safely_get_tag(instance, Const.EXTERNAL_ELB_DNS_NAME, logger=self._logger)
        if dns:
            return dns

        return instance.public_dns_name

    def _get_auto_scaling_group_elb(self, instance) -> Optional[List[str]]:

        if instance.instance_lifecycle == "spot":
            spot_fleet_id = AwsTagHelper.safely_get_tag(instance, AwsTagHelper.SpotFleetIdTag, self._logger)
            spot_fleet_requests = self._session.get_ec2_client().describe_spot_fleet_requests(
                SpotFleetRequestIds=[spot_fleet_id])
            load_balancer_names = \
                [lb["Name"] for lb in spot_fleet_requests['SpotFleetRequestConfigs'][0]['SpotFleetRequestConfig']['LoadBalancersConfig'][
                    'ClassicLoadBalancersConfig']['ClassicLoadBalancers']]
        else:
            autoscaling_group_name = AwsTagHelper. \
                safely_get_tag(instance, AwsTagHelper.AutoScalingGroupNameTag, self._logger)
            autoscaling_group_response = self._session.get_autoscaling_client() \
                .describe_auto_scaling_groups(AutoScalingGroupNames=[autoscaling_group_name])
            auto_scaling_groups = autoscaling_group_response['AutoScalingGroups'][0]
            if "LoadBalancerNames" in auto_scaling_groups and len(auto_scaling_groups["LoadBalancerNames"]) > 0:
                load_balancer_name = auto_scaling_groups["LoadBalancerNames"][0]
                load_balancer_names = [load_balancer_name]
            else:
                return []

        elb_response = self._session.get_elb_client().describe_load_balancers(LoadBalancerNames=load_balancer_names)
        return list(more_itertools.flatten([elb["SecurityGroups"] for elb in elb_response['LoadBalancerDescriptions']]))
