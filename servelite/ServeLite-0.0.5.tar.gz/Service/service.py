import json
from flask import Flask, g
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.automap import automap_base
from flask_restless import APIManager
import hashlib
import time
from threading import Thread

from Service.config import default
from Service.models import Base, get_session, Tables, Fields, APIs
from exceptions import *
from Service.communicator import Communicator
from auth import generate_key, signature

class baseService:
    """
    service基类
    实现了CORS, 线程记录, 公钥私钥读取/生成, hash读取/生成, 蓝图注册, flask线程
    """
    def __init__(self, server_name, config):
        self.config = config
        self.config['server_name'] = server_name
        self.app = Flask(__name__)
        self.app.service = self
        CORS(self.app)

        # 线程管理
        self.running = False  # flask运行标志
        self.threads = {}

        # session管理
        self.engine = create_engine(self.config['uri'])
        self.session_factory = scoped_session(sessionmaker(self.engine))

        @self.app.before_request
        def init_session():
            g.session = self.session_factory()

        @self.app.after_request
        def close_session():
            g.session.close()

        # 读取公钥私钥
        try:
            with open(self.config['pubkey_file'], 'r') as f:
                self.config['pubkey'] = f.read()
            with open(self.config['privkey_file'], 'r') as f:
                self.config['privkey'] = f.read()
            print('*Load RSA keys from file')
        except FileNotFoundError:
            print('*Generating RSA keys...')
            generate_key(self.config['pubkey_file'], self.config['privkey_file'])
            print('Open {0} and {1} to check keys'.format(self.config['pubkey_file'], self.config['privkey_file']))
            with open(self.config['pubkey_file'], 'r') as f:
                self.config['pubkey'] = f.read()
            with open(self.config['privkey_file'], 'r') as f:
                self.config['privkey'] = f.read()

        # 签名
        self.signature = signature(self.config['pubkey'], self.config['privkey'])

        # 生成hash
        if 'hash' not in self.config['service_info'].keys():
            hash_gen = hashlib.md5()
            hash_gen.update(self.config['pubkey'].encode('utf-8'))
            self.config['service_info']['hash'] = hash_gen.hexdigest()

    def register_blueprint(self, blueprint, **options):
        """
        代理app对象注册蓝图

        提供CORS支持
        :param blueprint:
        :return:
        """
        CORS(blueprint)
        self.app.register_blueprint(blueprint, **options)

    def run(self, host=None, port=None, debug=None, **options):
        """
        运行服务
        挂起一个运行flask的线程, 参数为flask运行参数

        使用多线程是因为run会阻塞线程，service线程需要执行其他操作

        注意：
            debug模式将关闭reload！
        reload依赖于signal机制，不能运行于独立线程。未来可能会找到其他解决方案。
        :return:
        """
        options['use_reloader'] = False
        thread = Thread(target=self.app.run, args=(host, port, debug), kwargs=options)
        thread.start()
        self.running = True
        self.threads['flask'] = thread

class Service(baseService):
    def __init__(self, server_name, config=None):
        """
        server_name将作为服务在注册中心的名称空间
        """
        baseService.__init__(self, server_name, config if config else default)

        # flask-restless实例
        session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.restless_manager = APIManager(self.app, session=scoped_session(session),
                                           preprocessors=self.config['preprocessors'],
                                           postprocessors=self.config['postprocessors'])

        # 初始化数据库接口
        self.automap_Base = automap_base()
        self.automap_Base.prepare(self.engine, reflect=True)
        for table in self.automap_Base.classes:
            self.restless_manager.create_api(table, url_prefix='/query')

        # declarative_base 供用户声明model时继承
        # 同时可以从model中直接导入base
        self.Base = Base

        # 通信模块
        self.communicator = Communicator(self.app, self.config)

    def register_table_info(self, init):
        """
        每次启动服务或表状态更新时调用该方法先注册中心注册
        todo:
            - 更新注册中心
            - 更新restless接口
        :return:
        """
        tables_to_reg = []
        # 扫描表
        for table in s.Base.metadata.sorted_tables:
            try:
                table_comment = json.loads(table.comment)
            except json.decoder.JSONDecodeError:
                raise WrongTypeInfoComment(table.name)
            table_info = {
                'table_name': table.name,
                'sensitivity': table_comment.get('sensitivity', 5),
                'primary_key': [i.name for i in table.primary_key.columns_autoinc_first],
                'description': table_comment.get('description', None),
                'note': table_comment.get('note', None),
                'fields': []
            }
            for c in table.columns._all_columns:
                column_comment = json.loads(c.comment if c.comment else '{}')
                foreignkey = []
                if len(c.foreign_keys) > 0:
                    foreignkey = [i._colspec for i in c.foreign_keys]
                table_info['fields'].append({
                    'name': c.name,
                    'type': str(c.type),
                    'description': table_comment.get('description', None),
                    'sensitivity': column_comment.get('sensitivity', 5),
                    'note': table_comment.get('note', None),
                    'nullable': c.nullable,
                    'unique': c.unique,
                    'default': c.default,
                    'foreignkey': foreignkey
                })
            # 对比已有info
            session = get_session()
            t = session.query(Tables).filter_by(name=table.name).first() #type: Tables
            if t:
                if t.register_info != json.dumps(table_info):
                    # info变化 提交信息
                    tables_to_reg.append(table_info)
                    t.register_info = json.dumps(table_info)
                    t.register_time = time.time()
                    columns = session.query(Fields).filter_by(table_id=t.id).all()
                    # 检查字段的修改情况 添加新字段
                    for col in table_info['fields']:
                        has_col = False
                        for old_col in columns:
                            if old_col.name == col['name']:
                                has_col = True
                                old_col.sensitivity = col['sensitivity']
                        if not has_col: # 旧表中没有该字段
                            new_col = Fields(
                                table_id=t.id,
                                name=col['name'],
                                sensitivity=col['sensitivity'],
                            )
                            session.add(new_col)
                    # 检查字段删除情况
                    for col in columns:
                        has_col = False
                        for old_col in table_info['fields']:
                            if old_col['name'] == col.name:
                                has_col = True
                        if not has_col:
                            session.delete(col)
                    session.commit()
            else: # 添加新表和字段
                new_table = Tables(
                    name=table.name,
                    sensitivity=table_info['sensitivity'],
                )
                session.add(new_table)
                session.commit()
                for col in table_info['fields']:
                    new_col = Fields(
                        table_id=new_table.id,
                        name=col['name'],
                        sensitivity=col['sensitivity'],
                    )
                    session.add(new_col)
                session.commit()
        # 提交注册中心
        if len(tables_to_reg) == 0:
            return
        self.communicator.request_with_JWT('/api/register-table', data={'table_info': json.dumps(tables_to_reg)})

    @staticmethod
    def check_info_by_md5(new_info, old_info):
        """
        通过md5摘要对比两段info是否相同
        :param new_info:
        :param old_info:
        :return: 不同为False 相同为True
        """
        if len(new_info) != len(old_info):
            return False
        h = hashlib.md5()
        h.update(new_info.encode("utf-8"))
        new_digest = h.hexdigest()
        h.update(old_info.encode("utf-8"))
        old_digest = h.hexdigest()
        return new_digest == old_digest

    def add_api(self, **info):
        """
        api注册装饰器
        调用该方法注册一个api
        该方法不负责创建路由, 路由仍然使用app或blueprint的route装饰器声明
        ?: 如果使用add_url_rule声明怎么使用
        todo:
            - 向注册中心注册api
            - 提交api_info
        :return:
        """
        def decorator(f):
            self.register_api(f, **info)
            return f
        return decorator

    def register_api(self, view_func, **info):
        """
        注册api的实际调用方法
        note: 该方法对蓝图的有效性还没有测试
        目前暂时不支持本地添加文档
        todo: api表查重 info接口提供api信息
        :return:
        """
        rule = None
        for endpoint in self.app.view_functions:
            if self.app.view_functions[endpoint] is view_func:
                for r in self.app.url_map._rules:
                    if r.endpoint == endpoint:
                        rule = r.rule
        if not rule:
            raise NoMatchedEndpoint()
        # 注册信息
        session = get_session()
        api = session.query(APIs).filter_by(rule=rule).first()
        if api:
            return
        api = APIs(
            name=info.get('name', view_func.__name__),
            rule=rule,
            sensitivity=info.get('sensitivity', 5),
            type=info.get('type'),
            description=info.get('description'),
            status=0
        )
        session.add(api)
        session.commit()

        url = self.config['service_info'].get('api_reg')
        if not url:
            url = self.communicator.update_service_info('api_reg')
        self.communicator.request_with_JWT(url, api.info())

    def api(self):
        """
        api装饰器 api必须调用该装饰器

        该装饰器会为api自动添加调用链记录和监控中心通信功能
        使用方式：
            @service.add_api
            @service.app.route()
            @service.api
            def func():
                pass

        todo: 在add_api中检测该装饰器调用
        :return:
        """
        def decorator(f):
            pass
            return f
        return decorator

if __name__ == '__main__':
    s = Service(__name__)
    a = 1