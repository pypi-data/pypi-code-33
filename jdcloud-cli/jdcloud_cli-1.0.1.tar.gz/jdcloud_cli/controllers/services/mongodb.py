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
from jdcloud_cli.cement.ext.ext_argparse import expose
from jdcloud_cli.controllers.base_controller import BaseController
from jdcloud_cli.client_factory import ClientFactory
from jdcloud_cli.parameter_builder import collect_user_args, collect_user_headers
from jdcloud_cli.printer import Printer
from jdcloud_cli.skeleton import Skeleton


class MongodbController(BaseController):
    class Meta:
        label = 'mongodb'
        help = '京东云数据库MongoDB接口'
        description = '''
        mongodb cli 子命令，数据库MongoDB相关接口。
        OpenAPI文档地址为：https://docs.jdcloud.com/cn/jcs-for-mongodb/api/overview
        '''
        stacked_on = 'base'
        stacked_type = 'nested'

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) Region ID """, dest='regionId',  required=False)),
            (['--page-number'], dict(help="""(int) 页码；默认为1，取值范围：[1,∞) """, dest='pageNumber', type=int, required=False)),
            (['--page-size'], dict(help="""(int) 分页大小；默认为10；取值范围[1, 100] """, dest='pageSize', type=int, required=False)),
            (['--filters'], dict(help="""(array: filter) instanceId - 实例ID, 精确匹配; instanceName - 实例名称, 模糊匹配; instanceStatus - mongodb状态，精确匹配，支持多个.RUNNING：运行, ERROR：错误 ,BUILDING：创建中, DELETING：删除中, RESTORING：恢复中, RESIZING：变配中; chargeMode - 计费类型，精确匹配;  """, dest='filters',  required=False)),
            (['--tag-filters'], dict(help="""(array: tagFilter) Tag筛选条件 """, dest='tagFilters',  required=False)),
            (['--sorts'], dict(help="""(array: sort) createTime - 创建时间,asc（正序），desc（倒序）;  """, dest='sorts',  required=False)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 查询实例信息 ''',
        description='''
            查询实例信息。

            示例: jdc mongodb describe-instances 
        ''',
    )
    def describe_instances(self):
        client_factory = ClientFactory('mongodb')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.mongodb.apis.DescribeInstancesRequest import DescribeInstancesRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = DescribeInstancesRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) Region ID """, dest='regionId',  required=False)),
            (['--instance-spec'], dict(help="""(dBInstanceSpec) 实例规格 """, dest='instanceSpec',  required=True)),
            (['--charge-spec'], dict(help="""(chargeSpec) 付费方式 """, dest='chargeSpec',  required=False)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 创建实例 ''',
        description='''
            创建实例。

            示例: jdc mongodb create-instance  --instance-spec {"":""}
        ''',
    )
    def create_instance(self):
        client_factory = ClientFactory('mongodb')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.mongodb.apis.CreateInstanceRequest import CreateInstanceRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = CreateInstanceRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) Region ID """, dest='regionId',  required=False)),
            (['--instance-id'], dict(help="""(string) Instance ID """, dest='instanceId',  required=True)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 删除实例 ''',
        description='''
            删除实例。

            示例: jdc mongodb delete-instance  --instance-id xxx
        ''',
    )
    def delete_instance(self):
        client_factory = ClientFactory('mongodb')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.mongodb.apis.DeleteInstanceRequest import DeleteInstanceRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = DeleteInstanceRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) Region ID """, dest='regionId',  required=False)),
            (['--instance-id'], dict(help="""(string) Instance ID """, dest='instanceId',  required=True)),
            (['--account-password'], dict(help="""(string) 新密码，必须包含且只支持字母及数字，不少于8字符不超过16字符。 """, dest='accountPassword',  required=True)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 重置密码 ''',
        description='''
            重置密码。

            示例: jdc mongodb reset-password  --instance-id xxx --account-password xxx
        ''',
    )
    def reset_password(self):
        client_factory = ClientFactory('mongodb')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.mongodb.apis.ResetPasswordRequest import ResetPasswordRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = ResetPasswordRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) Region ID """, dest='regionId',  required=False)),
            (['--instance-id'], dict(help="""(string) Instance ID """, dest='instanceId',  required=True)),
            (['--instance-class'], dict(help="""(string) 实例规格，包年包月不允许小于当前规格。 """, dest='instanceClass',  required=True)),
            (['--instance-storage-gb'], dict(help="""(int) 存储空间，包年包月不允许小于当前规格。 """, dest='instanceStorageGB', type=int, required=True)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 变更实例规格 ''',
        description='''
            变更实例规格。

            示例: jdc mongodb modify-instance-spec  --instance-id xxx --instance-class xxx --instance-storage-gb 0
        ''',
    )
    def modify_instance_spec(self):
        client_factory = ClientFactory('mongodb')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.mongodb.apis.ModifyInstanceSpecRequest import ModifyInstanceSpecRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = ModifyInstanceSpecRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) Region ID """, dest='regionId',  required=False)),
            (['--instance-id'], dict(help="""(string) Instance ID """, dest='instanceId',  required=True)),
            (['--instance-name'], dict(help="""(string) 新的实例名称，只支持数字、字母、英文下划线、中文，且不少于2字符不超过32字符。 """, dest='instanceName',  required=True)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 修改实例名称 ''',
        description='''
            修改实例名称。

            示例: jdc mongodb modify-instance-name  --instance-id xxx --instance-name xxx
        ''',
    )
    def modify_instance_name(self):
        client_factory = ClientFactory('mongodb')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.mongodb.apis.ModifyInstanceNameRequest import ModifyInstanceNameRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = ModifyInstanceNameRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) Region ID """, dest='regionId',  required=False)),
            (['--instance-id'], dict(help="""(string) Instance ID """, dest='instanceId',  required=True)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 获取备份策略 ''',
        description='''
            获取备份策略。

            示例: jdc mongodb describe-backup-policy  --instance-id xxx
        ''',
    )
    def describe_backup_policy(self):
        client_factory = ClientFactory('mongodb')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.mongodb.apis.DescribeBackupPolicyRequest import DescribeBackupPolicyRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = DescribeBackupPolicyRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) Region ID """, dest='regionId',  required=False)),
            (['--instance-id'], dict(help="""(string) Instance ID """, dest='instanceId',  required=True)),
            (['--preferred-backup-time'], dict(help="""(string) 备份时间，格式：HH:mmZ- HH:mmZ，只允许间隔时间为1小时的整点. """, dest='preferredBackupTime',  required=True)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 修改备份策略 ''',
        description='''
            修改备份策略。

            示例: jdc mongodb modify-backup-policy  --instance-id xxx --preferred-backup-time xxx
        ''',
    )
    def modify_backup_policy(self):
        client_factory = ClientFactory('mongodb')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.mongodb.apis.ModifyBackupPolicyRequest import ModifyBackupPolicyRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = ModifyBackupPolicyRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) Region ID """, dest='regionId',  required=False)),
            (['--instance-id'], dict(help="""(string) Instance ID """, dest='instanceId',  required=True)),
            (['--backup-id'], dict(help="""(string) 备份ID """, dest='backupId',  required=True)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 数据恢复 ''',
        description='''
            数据恢复。

            示例: jdc mongodb restore-instance  --instance-id xxx --backup-id xxx
        ''',
    )
    def restore_instance(self):
        client_factory = ClientFactory('mongodb')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.mongodb.apis.RestoreInstanceRequest import RestoreInstanceRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = RestoreInstanceRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) Region ID """, dest='regionId',  required=False)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 获取规格 ''',
        description='''
            获取规格。

            示例: jdc mongodb describe-flavors 
        ''',
    )
    def describe_flavors(self):
        client_factory = ClientFactory('mongodb')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.mongodb.apis.DescribeFlavorsRequest import DescribeFlavorsRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = DescribeFlavorsRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) Region ID """, dest='regionId',  required=False)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 获取可用区 ''',
        description='''
            获取可用区。

            示例: jdc mongodb describe-available-zones 
        ''',
    )
    def describe_available_zones(self):
        client_factory = ClientFactory('mongodb')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.mongodb.apis.DescribeAvailableZonesRequest import DescribeAvailableZonesRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = DescribeAvailableZonesRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) Region ID """, dest='regionId',  required=False)),
            (['--page-number'], dict(help="""(int) 页码；默认为1，取值范围：[1,∞) """, dest='pageNumber', type=int, required=False)),
            (['--page-size'], dict(help="""(int) 分页大小；默认为10；取值范围[1, 100] """, dest='pageSize', type=int, required=False)),
            (['--filters'], dict(help="""(array: filter) instanceId - 实例ID, 精确匹配; backupId - 备份ID, 精确匹配;  """, dest='filters',  required=False)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 查看备份 ''',
        description='''
            查看备份。

            示例: jdc mongodb describe-backups 
        ''',
    )
    def describe_backups(self):
        client_factory = ClientFactory('mongodb')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.mongodb.apis.DescribeBackupsRequest import DescribeBackupsRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = DescribeBackupsRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) Region ID """, dest='regionId',  required=False)),
            (['--instance-id'], dict(help="""(string) 实例ID """, dest='instanceId',  required=True)),
            (['--backup-name'], dict(help="""(string) 备份名称 """, dest='backupName',  required=False)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 创建备份 ''',
        description='''
            创建备份。

            示例: jdc mongodb create-backup  --instance-id xxx
        ''',
    )
    def create_backup(self):
        client_factory = ClientFactory('mongodb')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.mongodb.apis.CreateBackupRequest import CreateBackupRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = CreateBackupRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) Region ID """, dest='regionId',  required=False)),
            (['--backup-id'], dict(help="""(string) backup ID """, dest='backupId',  required=True)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 删除备份 ''',
        description='''
            删除备份。

            示例: jdc mongodb delete-backup  --backup-id xxx
        ''',
    )
    def delete_backup(self):
        client_factory = ClientFactory('mongodb')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.mongodb.apis.DeleteBackupRequest import DeleteBackupRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = DeleteBackupRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) Region ID """, dest='regionId',  required=False)),
            (['--backup-id'], dict(help="""(string) backup ID """, dest='backupId',  required=True)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 获取备份下载链接 ''',
        description='''
            获取备份下载链接。

            示例: jdc mongodb backup-download-url  --backup-id xxx
        ''',
    )
    def backup_download_url(self):
        client_factory = ClientFactory('mongodb')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.mongodb.apis.BackupDownloadURLRequest import BackupDownloadURLRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = BackupDownloadURLRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) Region ID """, dest='regionId',  required=False)),
            (['--instance-id'], dict(help="""(string) Instance ID """, dest='instanceId',  required=True)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 查询实例访问白名单 ''',
        description='''
            查询实例访问白名单。

            示例: jdc mongodb describe-security-ips  --instance-id xxx
        ''',
    )
    def describe_security_ips(self):
        client_factory = ClientFactory('mongodb')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.mongodb.apis.DescribeSecurityIpsRequest import DescribeSecurityIpsRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = DescribeSecurityIpsRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) Region ID """, dest='regionId',  required=False)),
            (['--instance-id'], dict(help="""(string) Instance ID """, dest='instanceId',  required=True)),
            (['--modify-mode'], dict(help="""(string) 修改方式,Add 增加白名单,Delete 删除白名单. """, dest='modifyMode',  required=True)),
            (['--security-ips'], dict(help="""(string) IP白名单分组下的IP列表，最多45个以逗号隔开，格式如下：0.0.0.0/0，10.23.12.24（IP），或者10.23.12.24/24（CIDR模式，无类域间路由，/24表示了地址中前缀的长度，范围[1，32]）。 """, dest='securityIps',  required=True)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 修改实例访问白名单 ''',
        description='''
            修改实例访问白名单。

            示例: jdc mongodb modify-security-ips  --instance-id xxx --modify-mode xxx --security-ips xxx
        ''',
    )
    def modify_security_ips(self):
        client_factory = ClientFactory('mongodb')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.mongodb.apis.ModifySecurityIpsRequest import ModifySecurityIpsRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = ModifySecurityIpsRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e)

    @expose(
        arguments=[
            (['--api'], dict(help="""(string) api name """, choices=['describe-instances','create-instance','delete-instance','reset-password','modify-instance-spec','modify-instance-name','describe-backup-policy','modify-backup-policy','restore-instance','describe-flavors','describe-available-zones','describe-backups','create-backup','delete-backup','backup-download-url','describe-security-ips','modify-security-ips',], required=True)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 生成单个API接口的json骨架空字符串 ''',
        description='''
            生成单个API接口的json骨架空字符串。

            示例: jdc nc generate-skeleton --api describeContainer ''',
    )
    def generate_skeleton(self):
        skeleton = Skeleton('mongodb', self.app.pargs.api)
        skeleton.show()
