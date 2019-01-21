# coding=utf8

# Copyright 2018 JDCLOUD.COM
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# NOTE: This class is auto generated by the jdcloud code generator program.

from argparse import RawTextHelpFormatter
from cement.ext.ext_argparse import expose
from jdcloud_cli.controllers.base_controller import BaseController
from jdcloud_cli.client_factory import ClientFactory
from jdcloud_cli.parameter_builder import collect_user_args, collect_user_headers
from jdcloud_cli.printer import Printer
from jdcloud_cli.skeleton import Skeleton


class CpsController(BaseController):
    class Meta:
        label = 'cps'
        help = '云物理服务器'
        description = '''
        cps cli 子命令，云物理服务器相关接口。
        OpenAPI文档地址为：https://docs.jdcloud.com/cn/cloud-physical-server/api/overview
        '''
        stacked_on = 'base'
        stacked_type = 'nested'

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) 地域ID，可调用接口（describeRegiones）获取云物理服务器支持的地域 """, dest='regionId',  required=False)),
            (['--device-type'], dict(help="""(string) 实例类型，可调用接口（describeDeviceTypes）获取指定地域的实例类型，例如：cps.c.normal """, dest='deviceType',  required=True)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 查询云物理服务器支持的操作系统 ''',
        description='''
            查询云物理服务器支持的操作系统。

            示例: jdc cps describe-os  --device-type xxx
        ''',
    )
    def describe_os(self):
        client_factory = ClientFactory('cps')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.cps.apis.DescribeOSRequest import DescribeOSRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = DescribeOSRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e.message)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) 地域ID，可调用接口（describeRegiones）获取云物理服务器支持的地域 """, dest='regionId',  required=False)),
            (['--os-type-id'], dict(help="""(string) 操作系统系统类型ID，调用接口（describeOS）获取云物理服务器支持的操作系统 """, dest='osTypeId',  required=True)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 查询物理服务器可预装的软件列表<br/>; 可调用接口（describeOS）获取云物理服务器支持的操作系统列表，根据不同的操作系统类型得到支持的可预装的软件列表<br/>;  ''',
        description='''
            查询物理服务器可预装的软件列表<br/>; 可调用接口（describeOS）获取云物理服务器支持的操作系统列表，根据不同的操作系统类型得到支持的可预装的软件列表<br/>; 。

            示例: jdc cps describe-software  --os-type-id xxx
        ''',
    )
    def describe_software(self):
        client_factory = ClientFactory('cps')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.cps.apis.DescribeSoftwareRequest import DescribeSoftwareRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = DescribeSoftwareRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e.message)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) 地域ID，可调用接口（describeRegiones）获取云物理服务器支持的地域 """, dest='regionId',  required=False)),
            (['--instance-id'], dict(help="""(string) 云物理服务器ID """, dest='instanceId',  required=True)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 查询云物理服务器名称 ''',
        description='''
            查询云物理服务器名称。

            示例: jdc cps describe-instance-name  --instance-id xxx
        ''',
    )
    def describe_instance_name(self):
        client_factory = ClientFactory('cps')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.cps.apis.DescribeInstanceNameRequest import DescribeInstanceNameRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = DescribeInstanceNameRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e.message)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) 地域ID，可调用接口（describeRegiones）获取云物理服务器支持的地域 """, dest='regionId',  required=False)),
            (['--instance-id'], dict(help="""(string) 云物理服务器ID """, dest='instanceId',  required=True)),
            (['--name'], dict(help="""(string) 云物理服务器名称 """, dest='name',  required=False)),
            (['--description'], dict(help="""(string) 云物理服务器描述 """, dest='description',  required=False)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 修改云物理服务器部分信息，包括名称、描述 ''',
        description='''
            修改云物理服务器部分信息，包括名称、描述。

            示例: jdc cps modify-instance  --instance-id xxx
        ''',
    )
    def modify_instance(self):
        client_factory = ClientFactory('cps')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.cps.apis.ModifyInstanceRequest import ModifyInstanceRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = ModifyInstanceRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e.message)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) 地域ID，可调用接口（describeRegiones）获取云物理服务器支持的地域 """, dest='regionId',  required=False)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 查询云物理服务器实例类型 ''',
        description='''
            查询云物理服务器实例类型。

            示例: jdc cps describe-device-types 
        ''',
    )
    def describe_device_types(self):
        client_factory = ClientFactory('cps')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.cps.apis.DescribeDeviceTypesRequest import DescribeDeviceTypesRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = DescribeDeviceTypesRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e.message)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) 地域ID，可调用接口（describeRegiones）获取云物理服务器支持的地域 """, dest='regionId',  required=False)),
            (['--device-type'], dict(help="""(string) 实例类型，可调用（describeDeviceTypes）接口获取指定地域的实例类型，例如：cps.c.normal """, dest='deviceType',  required=True)),
            (['--volume-type'], dict(help="""(string) 磁盘类型，取值范围：system、data """, dest='volumeType',  required=False)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 查询某种实例类型的云物理服务器支持的RAID类型，可查询系统盘RAID类型和数据盘RAID类型 ''',
        description='''
            查询某种实例类型的云物理服务器支持的RAID类型，可查询系统盘RAID类型和数据盘RAID类型。

            示例: jdc cps describe-device-raids  --device-type xxx
        ''',
    )
    def describe_device_raids(self):
        client_factory = ClientFactory('cps')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.cps.apis.DescribeDeviceRaidsRequest import DescribeDeviceRaidsRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = DescribeDeviceRaidsRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e.message)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) 地域ID，可调用接口（describeRegiones）获取云物理服务器支持的地域 """, dest='regionId',  required=False)),
            (['--instance-id'], dict(help="""(string) 云物理服务器ID """, dest='instanceId',  required=True)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 查询单个云物理服务器已安装的RAID信息，包括系统盘RAID信息和数据盘RAID信息 ''',
        description='''
            查询单个云物理服务器已安装的RAID信息，包括系统盘RAID信息和数据盘RAID信息。

            示例: jdc cps describe-instance-raid  --instance-id xxx
        ''',
    )
    def describe_instance_raid(self):
        client_factory = ClientFactory('cps')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.cps.apis.DescribeInstanceRaidRequest import DescribeInstanceRaidRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = DescribeInstanceRaidRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e.message)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) 地域ID，可调用接口（describeRegiones）获取云物理服务器支持的地域 """, dest='regionId',  required=False)),
            (['--instance-id'], dict(help="""(string) 云物理服务器ID """, dest='instanceId',  required=True)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 查询单个云物理服务器硬件监控信息 ''',
        description='''
            查询单个云物理服务器硬件监控信息。

            示例: jdc cps describe-instance-status  --instance-id xxx
        ''',
    )
    def describe_instance_status(self):
        client_factory = ClientFactory('cps')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.cps.apis.DescribeInstanceStatusRequest import DescribeInstanceStatusRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = DescribeInstanceStatusRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e.message)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) 地域ID，可调用接口（describeRegiones）获取云物理服务器支持的地域 """, dest='regionId',  required=False)),
            (['--instance-id'], dict(help="""(string) 云物理服务器ID """, dest='instanceId',  required=True)),
            (['--client-token'], dict(help="""(string) 由客户端生成，用于保证请求的幂等性，长度不能超过36个字符；<br/>; 如果多个请求使用了相同的clientToken，只会执行第一个请求，之后的请求直接返回第一个请求的结果<br/>;  """, dest='clientToken',  required=False)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 重启单个云物理服务器，只能重启running状态的服务器 ''',
        description='''
            重启单个云物理服务器，只能重启running状态的服务器。

            示例: jdc cps restart-instance  --instance-id xxx
        ''',
    )
    def restart_instance(self):
        client_factory = ClientFactory('cps')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.cps.apis.RestartInstanceRequest import RestartInstanceRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = RestartInstanceRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e.message)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) 地域ID，可调用接口（describeRegiones）获取云物理服务器支持的地域 """, dest='regionId',  required=False)),
            (['--instance-id'], dict(help="""(string) 云物理服务器ID """, dest='instanceId',  required=True)),
            (['--client-token'], dict(help="""(string) 由客户端生成，用于保证请求的幂等性，长度不能超过36个字符；<br/>; 如果多个请求使用了相同的clientToken，只会执行第一个请求，之后的请求直接返回第一个请求的结果<br/>;  """, dest='clientToken',  required=False)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 对单个云物理服务器执行关机操作，只能停止running状态的服务器 ''',
        description='''
            对单个云物理服务器执行关机操作，只能停止running状态的服务器。

            示例: jdc cps stop-instance  --instance-id xxx
        ''',
    )
    def stop_instance(self):
        client_factory = ClientFactory('cps')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.cps.apis.StopInstanceRequest import StopInstanceRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = StopInstanceRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e.message)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) 地域ID，可调用接口（describeRegiones）获取云物理服务器支持的地域 """, dest='regionId',  required=False)),
            (['--instance-id'], dict(help="""(string) 云物理服务器ID """, dest='instanceId',  required=True)),
            (['--client-token'], dict(help="""(string) 由客户端生成，用于保证请求的幂等性，长度不能超过36个字符；<br/>; 如果多个请求使用了相同的clientToken，只会执行第一个请求，之后的请求直接返回第一个请求的结果<br/>;  """, dest='clientToken',  required=False)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 对单个云物理服务器执行开机操作，只能启动stopped状态的服务器 ''',
        description='''
            对单个云物理服务器执行开机操作，只能启动stopped状态的服务器。

            示例: jdc cps start-instance  --instance-id xxx
        ''',
    )
    def start_instance(self):
        client_factory = ClientFactory('cps')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.cps.apis.StartInstanceRequest import StartInstanceRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = StartInstanceRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e.message)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) 地域ID，可调用接口（describeRegiones）获取云物理服务器支持的地域 """, dest='regionId',  required=False)),
            (['--instance-id'], dict(help="""(string) 云物理服务器ID """, dest='instanceId',  required=True)),
            (['--client-token'], dict(help="""(string) 由客户端生成，用于保证请求的幂等性，长度不能超过36个字符；<br/>; 如果多个请求使用了相同的clientToken，只会执行第一个请求，之后的请求直接返回第一个请求的结果<br/>;  """, dest='clientToken',  required=False)),
            (['--instance-spec'], dict(help="""(reinstallInstanceSpec) 云物理服务器配置 """, dest='instanceSpec',  required=True)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 重装云物理服务器，只能重装stopped状态的服务器<br/>; - 可调用接口（describeOS）获取云物理服务器支持的操作系统列表; - 可调用接口（describeSoftware）获取云物理服务器支持的软件列表，也可以不预装软件;  ''',
        description='''
            重装云物理服务器，只能重装stopped状态的服务器<br/>; - 可调用接口（describeOS）获取云物理服务器支持的操作系统列表; - 可调用接口（describeSoftware）获取云物理服务器支持的软件列表，也可以不预装软件; 。

            示例: jdc cps reinstall-instance  --instance-id xxx --instance-spec {"":""}
        ''',
    )
    def reinstall_instance(self):
        client_factory = ClientFactory('cps')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.cps.apis.ReinstallInstanceRequest import ReinstallInstanceRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = ReinstallInstanceRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e.message)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) 地域ID，可调用接口（describeRegiones）获取云物理服务器支持的地域 """, dest='regionId',  required=False)),
            (['--instance-id'], dict(help="""(string) 云物理服务器ID """, dest='instanceId',  required=True)),
            (['--client-token'], dict(help="""(string) 由客户端生成，用于保证请求的幂等性，长度不能超过36个字符；<br/>; 如果多个请求使用了相同的clientToken，只会执行第一个请求，之后的请求直接返回第一个请求的结果<br/>;  """, dest='clientToken',  required=False)),
            (['--bandwidth'], dict(help="""(int) 外网带宽，单位Mbps，取值范围[1,200] """, dest='bandwidth', type=int, required=True)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 升级云物理服务器外网带宽，只能操作running或者stopped状态的服务器<br/>; - 不支持未启用外网的服务器升级带宽; - 外网带宽不支持降级;  ''',
        description='''
            升级云物理服务器外网带宽，只能操作running或者stopped状态的服务器<br/>; - 不支持未启用外网的服务器升级带宽; - 外网带宽不支持降级; 。

            示例: jdc cps modify-bandwidth  --instance-id xxx --bandwidth 0
        ''',
    )
    def modify_bandwidth(self):
        client_factory = ClientFactory('cps')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.cps.apis.ModifyBandwidthRequest import ModifyBandwidthRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = ModifyBandwidthRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e.message)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) 地域ID，可调用接口（describeRegiones）获取云物理服务器支持的地域 """, dest='regionId',  required=False)),
            (['--instance-id'], dict(help="""(string) 云物理服务器ID """, dest='instanceId',  required=True)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 查询单台云物理服务器详细信息 ''',
        description='''
            查询单台云物理服务器详细信息。

            示例: jdc cps describe-instance  --instance-id xxx
        ''',
    )
    def describe_instance(self):
        client_factory = ClientFactory('cps')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.cps.apis.DescribeInstanceRequest import DescribeInstanceRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = DescribeInstanceRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e.message)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) 地域ID，可调用接口（describeRegiones）获取云物理服务器支持的地域 """, dest='regionId',  required=False)),
            (['--page-number'], dict(help="""(int) 页码；默认为1 """, dest='pageNumber', type=int, required=False)),
            (['--page-size'], dict(help="""(int) 分页大小；默认为10；取值范围[10, 100] """, dest='pageSize', type=int, required=False)),
            (['--az'], dict(help="""(string) 可用区，精确匹配 """, dest='az',  required=False)),
            (['--name'], dict(help="""(string) 云物理服务器名称，支持模糊匹配 """, dest='name',  required=False)),
            (['--network-type'], dict(help="""(string) 网络类型，精确匹配，目前只支持basic """, dest='networkType',  required=False)),
            (['--device-type'], dict(help="""(string) 实例类型，精确匹配，调用接口（describeDeviceTypes）获取实例类型 """, dest='deviceType',  required=False)),
            (['--status'], dict(help="""(string) 云物理服务器状态，参考云物理服务器状态 """, dest='status',  required=False)),
            (['--filters'], dict(help="""(array: filter) instanceId - 云物理服务器ID，精确匹配，支持多个;  """, dest='filters',  required=False)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 批量查询云物理服务器详细信息<br/>; 支持分页查询，默认每页10条<br/>;  ''',
        description='''
            批量查询云物理服务器详细信息<br/>; 支持分页查询，默认每页10条<br/>; 。

            示例: jdc cps describe-instances 
        ''',
    )
    def describe_instances(self):
        client_factory = ClientFactory('cps')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.cps.apis.DescribeInstancesRequest import DescribeInstancesRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = DescribeInstancesRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e.message)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) 地域ID，可调用接口（describeRegiones）获取云物理服务器支持的地域 """, dest='regionId',  required=False)),
            (['--client-token'], dict(help="""(string) 由客户端生成，用于保证请求的幂等性，长度不能超过36个字符；<br/>; 如果多个请求使用了相同的clientToken，只会执行第一个请求，之后的请求直接返回第一个请求的结果<br/>;  """, dest='clientToken',  required=False)),
            (['--instance-spec'], dict(help="""(instanceSpec) 描述云物理服务器配置 """, dest='instanceSpec',  required=True)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 创建一台或多台指定配置的云物理服务器<br/>; - 地域与可用区<br/>;   - 调用接口（describeRegiones）获取云物理服务器支持的地域与可用区<br/>; - 实例类型<br/>;   - 调用接口（describeDeviceTypes）获取物理实例类型列表<br/>;   - 不能使用已下线、或已售馨的实例类型<br/>; - 操作系统和预装软件<br/>;   - 可调用接口（describeOS）获取云物理服务器支持的操作系统列表<br/>;   - 可调用接口（describeSoftware）获取云物理服务器支持的软件列表，也可以不预装软件<br/>; - 存储<br/>;   - 数据盘多种RAID可选，可调用接口（describeDeviceRaids）获取服务器支持的RAID列表<br/>; - 网络<br/>;   - 网络类型目前只支持basic<br/>;   - 线路目前只支持bgp<br/>;   - 支持不启用外网，如果启用外网，带宽范围[1,200] 单位Mbps<br/>; - 其他<br/>;   - 购买时长，可按年或月购买，最少购买时长1个月，最长36个月（3年）<br/>;   - 密码设置参考公共参数规范<br/>;  ''',
        description='''
            创建一台或多台指定配置的云物理服务器<br/>; - 地域与可用区<br/>;   - 调用接口（describeRegiones）获取云物理服务器支持的地域与可用区<br/>; - 实例类型<br/>;   - 调用接口（describeDeviceTypes）获取物理实例类型列表<br/>;   - 不能使用已下线、或已售馨的实例类型<br/>; - 操作系统和预装软件<br/>;   - 可调用接口（describeOS）获取云物理服务器支持的操作系统列表<br/>;   - 可调用接口（describeSoftware）获取云物理服务器支持的软件列表，也可以不预装软件<br/>; - 存储<br/>;   - 数据盘多种RAID可选，可调用接口（describeDeviceRaids）获取服务器支持的RAID列表<br/>; - 网络<br/>;   - 网络类型目前只支持basic<br/>;   - 线路目前只支持bgp<br/>;   - 支持不启用外网，如果启用外网，带宽范围[1,200] 单位Mbps<br/>; - 其他<br/>;   - 购买时长，可按年或月购买，最少购买时长1个月，最长36个月（3年）<br/>;   - 密码设置参考公共参数规范<br/>; 。

            示例: jdc cps create-instances  --instance-spec {"":""}
        ''',
    )
    def create_instances(self):
        client_factory = ClientFactory('cps')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.cps.apis.CreateInstancesRequest import CreateInstancesRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = CreateInstancesRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e.message)

    @expose(
        arguments=[
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 查询云物理服务器地域列表 ''',
        description='''
            查询云物理服务器地域列表。

            示例: jdc cps describe-regiones 
        ''',
    )
    def describe_regiones(self):
        client_factory = ClientFactory('cps')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.cps.apis.DescribeRegionesRequest import DescribeRegionesRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = DescribeRegionesRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e.message)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) 地域ID，可调用接口（describeRegiones）获取云物理服务器支持的地域 """, dest='regionId',  required=False)),
            (['--az'], dict(help="""(string) 可用区, 如cn-east-1a；可调用接口（describeRegiones）获取云物理服务器在该地域支持的可用区 """, dest='az',  required=True)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 查询子网 ''',
        description='''
            查询子网。

            示例: jdc cps describe-subnet  --az xxx
        ''',
    )
    def describe_subnet(self):
        client_factory = ClientFactory('cps')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.cps.apis.DescribeSubnetRequest import DescribeSubnetRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = DescribeSubnetRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e.message)

    @expose(
        arguments=[
            (['--api'], dict(help="""(string) api name """, choices=['describe-os','describe-software','describe-instance-name','modify-instance','describe-device-types','describe-device-raids','describe-instance-raid','describe-instance-status','restart-instance','stop-instance','start-instance','reinstall-instance','modify-bandwidth','describe-instance','describe-instances','create-instances','describe-regiones','describe-subnet',], required=True)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 生成单个API接口的json骨架空字符串 ''',
        description='''
            生成单个API接口的json骨架空字符串。

            示例: jdc nc generate-skeleton --api describeContainer ''',
    )
    def generate_skeleton(self):
        skeleton = Skeleton('cps', self.app.pargs.api)
        skeleton.show()
