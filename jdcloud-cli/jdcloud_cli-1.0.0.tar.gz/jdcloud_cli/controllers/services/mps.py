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


class MpsController(BaseController):
    class Meta:
        label = 'mps'
        help = '媒体处理 API'
        description = '''
        mps cli 子命令，媒体处理相关接口。
        OpenAPI文档地址为：https://docs.jdcloud.com/cn/media-processing-service/api/overview
        '''
        stacked_on = 'base'
        stacked_type = 'nested'

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) region id """, dest='regionId',  required=False)),
            (['--status'], dict(help="""(string) task 状态 (PENDING, RUNNING, SUCCESS, FAILED) """, dest='status',  required=False)),
            (['--begin'], dict(help="""(string) 开始时间 时间格式(GMT): yyyy-MM-dd'T'HH:mm:ss.SSS'Z' """, dest='begin',  required=False)),
            (['--end'], dict(help="""(string) 结束时间 时间格式(GMT): yyyy-MM-dd'T'HH:mm:ss.SSS'Z' """, dest='end',  required=False)),
            (['--marker'], dict(help="""(string) 查询标记 """, dest='marker',  required=False)),
            (['--limit'], dict(help="""(int) 查询记录数 [1, 1000] """, dest='limit', type=int, required=False)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 查询截图任务 ''',
        description='''
            查询截图任务。

            示例: jdc mps list-thumbnail-task 
        ''',
    )
    def list_thumbnail_task(self):
        client_factory = ClientFactory('mps')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.mps.apis.ListThumbnailTaskRequest import ListThumbnailTaskRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = ListThumbnailTaskRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e.message)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) region id """, dest='regionId',  required=False)),
            (['--task-id'], dict(help="""(string) 任务ID (readonly) """, dest='taskID',  required=False)),
            (['--status'], dict(help="""(string) 状态 (SUCCESS, ERROR, PENDDING, RUNNING) (readonly) """, dest='status',  required=False)),
            (['--error-code'], dict(help="""(int) 错误码 (readonly) """, dest='errorCode', type=int, required=False)),
            (['--created-time'], dict(help="""(string) 任务创建时间 时间格式(GMT): yyyy-MM-dd’T’HH:mm:ss.SSS’Z’  (readonly) """, dest='createdTime',  required=False)),
            (['--last-updated-time'], dict(help="""(string) 任务创建时间 时间格式(GMT): yyyy-MM-dd’T’HH:mm:ss.SSS’Z’  (readonly) """, dest='lastUpdatedTime',  required=False)),
            (['--source'], dict(help="""(thumbnailTaskSource) NA """, dest='source',  required=True)),
            (['--target'], dict(help="""(thumbnailTaskTarget) NA """, dest='target',  required=True)),
            (['--rule'], dict(help="""(thumbnailTaskRule) NA """, dest='rule',  required=False)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 创建截图任务 ''',
        description='''
            创建截图任务。

            示例: jdc mps create-thumbnail-task  --source {"":""} --target {"":""}
        ''',
    )
    def create_thumbnail_task(self):
        client_factory = ClientFactory('mps')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.mps.apis.CreateThumbnailTaskRequest import CreateThumbnailTaskRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = CreateThumbnailTaskRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e.message)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) region id """, dest='regionId',  required=False)),
            (['--task-id'], dict(help="""(string) task id """, dest='taskId',  required=True)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 获取截图任务 ''',
        description='''
            获取截图任务。

            示例: jdc mps get-thumbnail-task  --task-id xxx
        ''',
    )
    def get_thumbnail_task(self):
        client_factory = ClientFactory('mps')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.mps.apis.GetThumbnailTaskRequest import GetThumbnailTaskRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = GetThumbnailTaskRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e.message)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) region id """, dest='regionId',  required=False)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 获取截图通知 ''',
        description='''
            获取截图通知。

            示例: jdc mps get-notification 
        ''',
    )
    def get_notification(self):
        client_factory = ClientFactory('mps')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.mps.apis.GetNotificationRequest import GetNotificationRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = GetNotificationRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e.message)

    @expose(
        arguments=[
            (['--region-id'], dict(help="""(string) region id """, dest='regionId',  required=False)),
            (['--enabled'], dict(help="""(bool) 是否启用通知 """, dest='enabled',  required=True)),
            (['--endpoint'], dict(help="""(string) 通知endpoint, 当前支持http://和https:// """, dest='endpoint',  required=False)),
            (['--events'], dict(help="""(array: string) 触发通知的事件集合 (mpsTranscodeComplete, mpsThumbnailComplete) """, dest='events',  required=False)),
            (['--notify-strategy'], dict(help="""(string) 重试策略, BACKOFF_RETRY: 退避重试策略, 重试 3 次, 每次重试的间隔时间是 10秒 到 20秒 之间的随机值; EXPONENTIAL_DECAY_RETRY: 指数衰减重试, 重试 176 次, 每次重试的间隔时间指数递增至 512秒, 总计重试时间为1天; 每次重试的具体间隔为: 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 512 ... 512 秒(共167个512) """, dest='notifyStrategy',  required=False)),
            (['--notify-content-format'], dict(help="""(string) 描述了向 Endpoint 推送的消息格式, JSON: 包含消息正文和消息属性, SIMPLIFIED: 消息体即用户发布的消息, 不包含任何属性信息 """, dest='notifyContentFormat',  required=False)),
            (['--input-json'], dict(help='(json) 以json字符串或文件绝对路径形式作为输入参数。\n字符串方式举例：--input-json \'{"field":"value"}\';\n文件格式举例：--input-json file:///xxxx.json', dest='input_json', required=False)),
            (['--headers'], dict(help="""(json) 用户自定义Header，举例：'{"x-jdcloud-security-token":"abc","test":"123"}'""", dest='headers', required=False)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 设置媒体处理通知, 在设置Notification时会对endpoint进行校验, 设置时会对endpoint发一条SubscriptionConfirmation(x-jdcloud-message-type头)的通知, 要求把Message内容进行base64编码返回给系统(body)进行校验 ''',
        description='''
            设置媒体处理通知, 在设置Notification时会对endpoint进行校验, 设置时会对endpoint发一条SubscriptionConfirmation(x-jdcloud-message-type头)的通知, 要求把Message内容进行base64编码返回给系统(body)进行校验。

            示例: jdc mps set-notification  --enabled true
        ''',
    )
    def set_notification(self):
        client_factory = ClientFactory('mps')
        client = client_factory.get(self.app)
        if client is None:
            return

        try:
            from jdcloud_sdk.services.mps.apis.SetNotificationRequest import SetNotificationRequest
            params_dict = collect_user_args(self.app)
            headers = collect_user_headers(self.app)
            req = SetNotificationRequest(params_dict, headers)
            resp = client.send(req)
            Printer.print_result(resp)
        except ImportError:
            print('{"error":"This api is not supported, please use the newer version"}')
        except Exception as e:
            print(e.message)

    @expose(
        arguments=[
            (['--api'], dict(help="""(string) api name """, choices=['list-thumbnail-task','create-thumbnail-task','get-thumbnail-task','get-notification','set-notification',], required=True)),
        ],
        formatter_class=RawTextHelpFormatter,
        help=''' 生成单个API接口的json骨架空字符串 ''',
        description='''
            生成单个API接口的json骨架空字符串。

            示例: jdc nc generate-skeleton --api describeContainer ''',
    )
    def generate_skeleton(self):
        skeleton = Skeleton('mps', self.app.pargs.api)
        skeleton.show()
