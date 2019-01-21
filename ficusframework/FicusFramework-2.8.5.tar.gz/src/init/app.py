import logging
import sys

from flask import Flask
from flask_cors import *

import config
from schedule.utils.log.TaskLogCleanScheduler import TaskLogCleanScheduler

log = logging.getLogger('Ficus')

log.info("=======服务启动开始======")
app = Flask(__name__)
# 设置跨域
CORS(app, supports_credentials=True)

#读取本地配置文件
from config.BootstrapPropertyLoader import load_properties_after_started, init_from_yaml_property,init_from_environ_property
init_from_yaml_property(sys.argv[0])
# 尝试从环境变量中获取 bootstrap里面的信息
init_from_environ_property()

log.info("服务启动,完成本地yaml配置文件读取")

# 注册信息到eureka中
from eureka.client import EurekaClient

# 第一个参数即为注册到eureka中的服务名,要求sobey.开头, 只允许字母数字点号
ec = EurekaClient(config.application_name,
                  eureka_url=config.eureka_default_zone,
                  port=config.server_port or 5000,
                  lease_renewal_interval_in_seconds=2,
                  lease_expiration_duration_in_seconds=6
                  )
# 发起服务注册以及心跳
ec.register("UP")
ec.start_heartbeat()

log.info("服务启动,完成注册中心注册及心跳")

load_properties_after_started(sys.argv[0],ec)

log.info("服务启动,完成配置中心配置文件读取")

# 这一行不能去掉,目的是引入flask的endpoints,并且位置需要在 app = Flask(__name__) 后面
# 引入views
from remote import remote

app.register_blueprint(remote, url_prefix='/')

log.info("服务启动,完成flask框架启动")

# 先加载registry.yml
import registry
registry.load_registry_properties(sys.argv[0], "registry.yml")

# 预先加载根目录下的这个模块,这样才能在程序启动后,自动注册执行器
try:
    import handlers
except:
    pass
log.info("服务启动,完成处理器的预加载")

# 程序启动后,判断是否需要注册执行器
from registry.LoadOnRegistryLoader import registry_after_started
registry_after_started(ec)

log.info("服务启动,完成处理器的注册")

log_cleaner = TaskLogCleanScheduler()
log_cleaner.start()
log.info("服务启动,完成日期清理线程的启动")

import eureka
log.info(f"服务启动:{eureka.client.get_host_ip()}:{config.server_port or 5000}")
log.info("======服务启动完毕======")