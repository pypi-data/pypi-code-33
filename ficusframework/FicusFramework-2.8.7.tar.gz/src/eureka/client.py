# -*- coding: utf-8 -*-

import json
import logging
import socket
from urllib.parse import urljoin

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from dns.resolver import query
from ec2_metadata import ec2_metadata

from eureka import __version__
from eureka.exceptions import *
from eureka.statuses import STATUS_STARTING

log = logging.getLogger('Ficus')
scheduler = BackgroundScheduler()


class EurekaClient:
    """
    Application client for Netflix Eureka.
    """

    def __init__(self,
                 app_name,
                 eureka_url,
                 ip_addr=None,
                 port=5000,
                 data_center="MyOwn",
                 eureka_domain_name=None,
                 eureka_port=None,
                 health_check_url=None,
                 status_page_url=None,
                 homepage_url=None,
                 host_name=None,
                 prefer_same_zone=True,
                 region_name=None,
                 secure_port=None,
                 secure_vip_address=None,
                 vip_address=None,
                 lease_renewal_interval_in_seconds=30,
                 lease_expiration_duration_in_seconds=90):
        """

        :param app_name:  服务的名字
        :param data_center: 数据中心,默认是MyOwn
        :param eureka_domain_name: eureka的域名
        :param eureka_port: eureka的端口
        :param eureka_url: eureka的url完整地址
        :param health_check_url: 健康监测的地址 默认是 http://ip:port/actuator/health
        :param status_page_url:  状态监测页面的地址 默认是 http://ip:port/actuator/info
        :param homepage_url: 服务的主业地址 默认是 http://ip:port
        :param host_name:  服务的域名, 默认同 app_name
        :param ip_addr: 服务的ip
        :param port: 服务的端口 默认5000
        :param prefer_same_zone: 期望使用相同zone的服务
        :param region_name: region的名字
        :param secure_port: https的端口
        :param secure_vip_address: https的vip域名 默认同 app_name
        :param vip_address: http的vip域名 默认同 app_name
        :param lease_renewal_interval_in_seconds: 心跳周期,默认是30秒
        :param lease_expiration_duration_in_seconds: 最后一次心跳时间后lease_expiration_duration_in_seconds秒就认为是下线了，默认是90秒
        """

        self.metadata = ec2_metadata
        self.app_name = app_name
        self.ip_addr = ip_addr or get_host_ip()  # 这里如果不填ip地址,就会自己通过upd请求去猜ip地址
        self.data_center = data_center
        self.context = "eureka/v2"
        self.port = port
        self.prefer_same_zone = prefer_same_zone
        self.server_domain_name = eureka_domain_name
        self.eureka_port = eureka_port
        self.eureka_url = eureka_url
        self.eureka_urls = None
        self.vip_address = vip_address or app_name
        self.secure_vip_address = secure_vip_address or app_name
        self.secure_port = secure_port
        self.lease_renewal_interval_in_seconds = lease_renewal_interval_in_seconds
        self.lease_expiration_duration_in_seconds = lease_expiration_duration_in_seconds

        if region_name:
            self.region_name = region_name
        elif data_center == "Amazon":
            self.region_name = self.metadata.region
        else:
            self.region_name = region_name

        if host_name:
            self.host_name = host_name
        elif data_center == "Amazon":
            self.host_name = self.metadata.public_hostname
        else:
            self.host_name = self.ip_addr

        self.homepage_url = homepage_url or f'http://{self.host_name}:{self.port}/'
        self.health_check_url = health_check_url or f'http://{self.host_name}:{self.port}/actuator/health'
        self.status_page_url = status_page_url or f'http://{self.host_name}:{self.port}/actuator/info'

    @property
    def headers(self):
        """
        通用的头信息
        :return:
        """
        return {
            'Content-Type': 'application/json',
            'User-agent': 'python-eureka-client v{}'.format(__version__),
            'accept': 'application/json'
        }

    @property
    def server_urls(self):
        """
        返回eureka的服务地址, 如果填了eureka_url就直接返回, 否则通过eureka_domain等去找
        :return:
        """
        if self.eureka_urls is not None :
            return self.eureka_urls

        # 多个 eureka用逗号分隔的方式
        if self.eureka_url:

            if "," in self.eureka_url:
                # 说明有逗号,也就是多个,需要按照逗号拆分
                tmp = self.eureka_url.split(",")
                self.eureka_urls = list(filter(lambda x:x is not None and ""!=x,tmp))
            else:
                self.eureka_urls = [self.eureka_url]
        else:
            # TODO 这里还没有实现
            self.eureka_urls = []

        return self.eureka_urls

    @property
    def instance_zone(self):
        return self.metadata.availability_zone

    @property
    def instance_id(self):
        """
        返回实例的Id 规则是  host_name:app_name:port
        :return:
        """
        if self.data_center == "Amazon":
            return self.metadata.instance_id
        else:
            return f'{self.host_name}:{self.app_name}:{self.port}'

    def get_zones(self):
        zone_urls = list(self._get_zone_urls(
            f"txt.{self.region_name}.{self.server_domain_name}"))
        urls = list(self._get_zone_urls(f"txt.{url}") for url in zone_urls)
        return {i.split('.')[0]: urls for i in zone_urls}

    def register(self, initial_status=STATUS_STARTING):
        """
        向eureka注册服务
        :param initial_status: 初始化状态,默认是 STARTING
        :return:
        """

        # 数据中心相关的配置
        data_center_info = {
            '@class': 'com.netflix.appinfo.InstanceInfo$DefaultDataCenterInfo',
            'name': self.data_center,
        }

        # 超时相关的配置
        lease_info = {
            'renewalIntervalInSecs': self.lease_renewal_interval_in_seconds,
            'durationInSecs': self.lease_expiration_duration_in_seconds
        }

        # 如果是亚马逊的数据中心,就需要添加特殊的东西
        if self.data_center == "Amazon":
            data_center_info["metadata"] = {
                'ami-launch-index': self.metadata.ami_launch_index,
                'local-hostname': self.metadata.private_hostname,
                'availability-zone': self.metadata.availability_zone,
                'instance-id': self.metadata.instance_id,
                'public-ipv4': self.metadata.public_ipv4,
                'public-hostname': self.metadata.public_hostname,
                'ami-manifest-path': self.metadata.ami_manifest_path,
                'local-ipv4': self.metadata.private_ipv4,
                'ami-id': self.metadata.ami_id,
                'instance-type': self.metadata.instance_type
            }

        # 注册实例时,需要填的东西
        instance = {
            'hostName': self.host_name,
            'app': self.app_name.upper(),
            'ipAddr': self.ip_addr,
            'status': initial_status,
            'dataCenterInfo': data_center_info,
            'healthCheckUrl': self.health_check_url,
            'statusPageUrl': self.status_page_url,
            'instanceId': self.instance_id,
            'homePageUrl': self.homepage_url,
            'vipAddress': self.vip_address,
            'secureVipAddress': self.secure_vip_address,
            'port': {
                '$': self.port,
                '@enabled': 'true'
            },
            'securePort': {
                '$': self.secure_port,
                '@enabled': 'false'
            },
            'leaseInfo': lease_info
        }

        err = None

        # 遍历所有的eureka地址,然后发起注册的请求
        while 0 < len(self.server_urls):
            base_url = self.server_urls[0]
            try:
                # 发起请求
                r = requests.post(self._get_app_url(base_url),
                                  data=json.dumps({'instance': instance}),
                                  headers=self.headers)
                r.raise_for_status()
                return
            except requests.exceptions.ConnectionError as e:
                self.eureka_urls.remove(base_url)
                err = e
            except requests.exceptions.RequestException as e:
                raise RegistrationFailed(str(e))

        self.eureka_urls = None
        raise RegistrationFailed(str(err))

    def update_status(self, status):
        """
        更新实例的状态
        :param status: 参考 statuses.py
        :return:
        """
        err = None

        while 0 < len(self.server_urls):
            base_url = self.server_urls[0]
            try:
                r = requests.put(self._get_status_url(base_url, status))
                r.raise_for_status()
                return
            except requests.exceptions.ConnectionError as e:
                self.eureka_urls.remove(base_url)
                err = e
            except requests.exceptions.RequestException as e:
                raise UpdateFailed(str(e))

        self.eureka_urls = None
        raise UpdateFailed(str(err))

    def heartbeat(self):
        """
        服务心跳
        :return:
        """
        err = None
        r = None
        while 0 < len(self.server_urls):
            base_url = self.server_urls[0]
            try:
                r = requests.put(self._get_instance_url(base_url))
                r.raise_for_status()
                return
            except requests.exceptions.ConnectionError as e:
                self.eureka_urls.remove(base_url)
                err = e
            except requests.exceptions.HTTPError:
                if r.status_code == 404:
                    # 说明已经下线了,重新上线
                    self.register("UP")
                    return
                raise HeartbeatFailed("No instances replied to heartbeat")
            except requests.exceptions.RequestException:
                raise HeartbeatFailed("No instances replied to heartbeat")
        self.eureka_urls = None
        raise UpdateFailed(str(err))

    def start_heartbeat(self):
        """
        开启自动的心跳
        :return: 如果启动成功,返回True. 如果启动失败,返回False
        """

        if scheduler.get_job("eureka_heartbeat") is None:
            scheduler.add_job(self.heartbeat, 'interval', seconds=self.lease_renewal_interval_in_seconds,
                              id="eureka_heartbeat")
            scheduler.start()
            return True

        return False

    def unregister(self):
        """
        服务反注册
        :return:
        """
        err = None

        while 0 < len(self.server_urls):
            base_url = self.server_urls[0]
            try:
                r = requests.delete(self._get_instance_url(base_url))
                r.raise_for_status()
                return
            except requests.exceptions.ConnectionError as e:
                self.eureka_urls.remove(base_url)
                err = e
            except requests.exceptions.RequestException as e:
                raise UnRegistrationFailed(str(e))

        self.eureka_urls = None
        raise UnRegistrationFailed(str(err))

    def get_apps(self):
        """
        获取eureka上的所有apps
        :return:
        """
        return self._get_data('apps')

    def get_app(self, app_id):
        """
        获取eureka上的某一个app
        :param app_id:
        :return:
        """
        return self._get_data(f'apps/{app_id}')

    def get_vip(self, vip_address):
        """
        获取eureka上某个vip下的所有实例
        :param vip_address:
        :return:
        """
        return self._get_data(f'vips/{vip_address}')

    def get_instance_urls(self, vip_address):
        """
        获取eureka上某一个vip下的所有实例的url地址
        :param vip_address:
        :return:
        """

        """{'applications': {'versions__delta': '-1', 'apps__hashcode': 'UP_1_', 'application': [{'name': 
        'SOBEYFICUS-CONFIG-SERVER', 'instance': [{'instanceId': '172.16.179.58:sobeyficus-config-server:8777', 
        'hostName': '172.16.179.58', 'app': 'SOBEYFICUS-CONFIG-SERVER', 'ipAddr': '172.16.179.58', 'status': 'UP', 
        'overriddenStatus': 'UNKNOWN', 'port': {'$': 8777, '@enabled': 'true'}, 'securePort': {'$': 443, '@enabled': 
        'false'}, 'countryId': 1, 'dataCenterInfo': {'@class': 
        'com.netflix.appinfo.InstanceInfo$DefaultDataCenterInfo', 'name': 'MyOwn'}, 'leaseInfo': {
        'renewalIntervalInSecs': 2, 'durationInSecs': 6, 'registrationTimestamp': 1527127431125, 
        'lastRenewalTimestamp': 1527127533000, 'evictionTimestamp': 0, 'serviceUpTimestamp': 1527127430458}, 
        'metadata': {'management.port': '8777', 'jmx.port': '51498'}, 'homePageUrl': 'http://172.16.179.58:8777/', 
        'statusPageUrl': 'http://172.16.179.58:8777/actuator/info', 'healthCheckUrl': 
        'http://172.16.179.58:8777/actuator/health', 'vipAddress': 'sobeyficus-config-server', 'secureVipAddress': 
        'sobeyficus-config-server', 'isCoordinatingDiscoveryServer': 'false', 'lastUpdatedTimestamp': 
        '1527127431125', 'lastDirtyTimestamp': '1527127430229', 'actionType': 'ADDED'}]}]}} """
        instances = self.get_vip(vip_address)

        if instances is None:
            return []

        from jsonpath_rw import parse
        jsonpath_expr = parse("$.applications.application[*].instance[*].homePageUrl")
        urls = jsonpath_expr.find(instances)

        return [url.value for url in urls]

    def get_svip(self, vip_address):
        """
        获取eureka上某一个svip下的所有实例
        :param vip_address:
        :return:
        """
        return self._get_data(f'svips/{vip_address}')

    def get_instance(self, instance_id):
        """
        获取eureka上个某一个实例信息
        :param instance_id:
        :return:
        """
        return self._get_data(f'instances/{instance_id}')

    def get_app_instance(self, app_id, instance_id):
        """
        获取eureka上某一个服务的某一个实例
        :param app_id:
        :param instance_id:
        :return:
        """
        return self._get_data(f'apps/{app_id}/{instance_id}')

    # region 私有方法
    def _get_zone_urls(self, domain):
        records = query(domain, 'TXT')
        for record in records:
            for i in record.string:
                yield i

    def _get_data(self, resource):
        """
        Generic get requests for any instance data, returns dict of payload
        """
        isConnectionError = True
        while 0 < len(self.server_urls):
            base_url = self.server_urls[0]
            try:
                r = requests.get(urljoin(base_url, resource),
                                 headers={'accept': 'application/json',
                                          'accept-encoding': 'gzip'})
                r.raise_for_status()
                return r.json()
            except requests.exceptions.ConnectionError as e:
                self.eureka_urls.remove(base_url)
                isConnectionError = isConnectionError and True
            except requests.exceptions.RequestException as e:
                isConnectionError = False
                if e.response.status_code == 404:
                    return None
        if isConnectionError:
            self.eureka_urls = None

        raise FetchFailed(f"Failed to get {resource} from all instances")

    def _get_status_url(self, base_url, status):
        """
        Returns apps/{app_name}/{instane_id}/status?value={status}
        """
        return urljoin(self._get_instance_url(base_url),
                       f"status?value={status}")

    def _get_instance_url(self, base_url):
        """
        构造服务地址
        Returns apps/{app_name}/{instance_id}
        """
        # 这个地方不适用urljoin 而是使用字符串拼接,在于urljoin遇到 instance_id等于 xxx:xxx:xxx 的 时候连接会出错
        return f"{self._get_app_url(base_url)}/{self.instance_id}"

    def _get_app_url(self, base_url):
        """
        构造请求地址
        Returns apps/{app_name}
        """
        return urljoin(base_url, f"apps/{self.app_name}")


def get_host_ip():
    """
    获取本机的IP地址
    :return:
    """
    try:
        # 创建一个临时的socket连接
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 向自己发送一个udp的请求
        s.connect(('8.8.8.8', 80))
        # 送结果中获取到真实的ip地址
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

    # endregion
