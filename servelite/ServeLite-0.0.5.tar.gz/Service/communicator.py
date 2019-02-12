from flask import Flask, Blueprint, jsonify, request
import requests
import time
import json
import base64

from auth import signature, verify
from exceptions import std_res
from Config import JSONKeeper

class Communicator:
    """
    通信模块
    - 定义和维护和注册中心交互的接口
    - 提供带JWT访问注册中心和其他服务的方法
    """
    def __init__(self, app, config):
        self.app = app # type: Flask
        self.config = config
        self.service_info = self.config['service_info'] # type: JSONKeeper
        self.JWT = None
        # 定义和注册中心通信的路由
        # 这些路由将接受注册中心的验证请求和数据更新推送
        # methods默认值为['GET']
        self.routes = {
            'communicate': {
                'prefix': '/communicate',
                'routes': [
                    {
                        'rule': '/confirm',
                        'view_func': self.confirm
                        # 用于接受确认请求, 请求携带一个随机token
                        # 该接口返回私钥摘要的token
                    },
                    {
                        'rule': '/update',
                        'methods': ['POST'],
                        'view_func': self.update
                        # 用于接受注册中心的内容更新推送
                    },
                ]
            },
            'info': {
                'prefix': '/info',
                'routes': [
                    {
                        'rule': '/pubkey',
                        'view_func': self.pubkey
                        # 获取模块公钥
                    }
                ]
            }
        }

        # 注册路由
        for i in self.routes:
            blueprint = Blueprint(i, __name__, url_prefix=self.routes[i]['prefix'])
            routes = self.routes[i]['routes']
            for route in routes:
                blueprint.add_url_rule(
                    route['rule'],
                    methods=route.get('methods', ['GET']),
                    view_func=route['view_func']
                )
            self.app.register_blueprint(blueprint)

    def refresh_JWT(self):
        """
        更新JWT
        :return:
        """
        url = self.service_info.get('get_JWT')
        if not url:
            url = self.update_service_info('get_JWT')
        data = {
            'id': self.service_info['id'],
            'signature': signature(self.config['pubkey'], self.config['privkey'])
        }
        r = requests.post(url, data=data).json()
        self.JWT = {
            'token': r.get('token'),
            'timestamp': r.get('timestamp'),
            'expires': r.get('expires')
        }
        self.config['JWT'] = self.JWT

    def update_service_info(self, keys):
        """
        访问注册中心更新service_info
        注册中心返回值存入service_info并返回这个值
        如果只有一个key，直接返回；如果有多个，返回列表

        service_info的存储位置由注册中心决定
        :param keys:
        :return:
        """
        if type(keys) is str:
            keys = [keys]
        try:
            url = self.service_info.find('reg_url') + self.service_info.find('info_update')
        except TypeError:
            raise ValueError('base_url or info is to be defined')
        if not url:
            raise ValueError('info api is to be defined')
        info = []
        for i in keys:
            try:
                r = requests.get(url + '/' + i) # note: 注册中心需要为约定的info创建接口
                data = r.json()
            # 返回数据结构：
            # { pos: layer1.layer2[.layers], data: value }
            except requests.exceptions.ConnectionError:
                raise ValueError('no info of key: {}'.format(i))
            except json.decoder.JSONDecodeError:
                raise ValueError('response is not jsonable')
            if r.status_code == 404:
                raise ValueError('no info of key: {}'.format(i))
            pos = data.get('pos')
            value = data.get('data')
            if pos: # pos为None时不存储到service_info
                self.service_info.set(pos, value)
            info.append(value)
        if len(info) == 1:
            return info[0]
        return info

    def request_with_JWT(self, path, data=None, *args, **kwargs):
        """
        带jwt访问注册中心, kwargs内容将被作为参数发送
        返回值是返回的json，已经load。
        :param data:
        :param path: 路由 域名会补全
        :param args:
        :param kwargs:
        :return:
        """
        if time.time() > int(self.JWT['timestamp']) + int(self.JWT['expires']):
            self.refresh_JWT()
        r = requests.post(self.service_info['base_url'] + path,
                          data=data, headers={"Authorization": "JWT " + self.JWT['token']})
        try:
            data = r.json()
        except:
            return {'error': 'response is not jsonable'}
        # JWT过期
        return data

    def heartbeat(self):
        """
        向注册中心发送心跳包
        首先需要检测
        :return:
        """
        url = self.service_info.find('heartbeat')
        if not url:
            if not self.service_info.find('confirmed'):
                return # 尚未确认
            else:
                url = self.update_service_info('heartbeat')
        self.request_with_JWT(url)


    #################
    #  routes
    #################
    def confirm(self):
        """
        返回签名进行身份校验。
        """
        return jsonify({
            'signature': signature(self.config['pubkey'], self.config['privkey'])
        })

    def update(self):
        """
        接受一组更改service_info的json
        该方法需要验证发送方签名以确认身份

        接收请求后首先向注册中心获取公钥信息，用公钥解密签名，签名内容应当为公钥字符串。
        注意：由于使用rsa直接签名在request中会因为decode()出现信息丢失，需要在请求时将sign进行base64编码并解码为str传输

        由于service_info是有层级的结构, 数据格式为:
        data = [
            {
                pos: 一级.二级[.n]
                data:
            }
        ]

        :return:
        """
        pubkey = requests.get(self.service_info['info_update'] + '/pubkey').json()['pubkey']
        try:
            sign = request.args.get('signature')
            sign = sign.encode()
            sign = base64.b64decode(sign)
            if sign is None:
                return std_res('400', 'signature is required')
        except ValueError as e:
            return std_res('400', 'unknown error', error_msg=repr(e))
        if not verify(pubkey, sign, pubkey):
            return std_res('403', 'invalid visit')
        data = request.args.get('data')
        for info in data:
            self.service_info.set(info['pos'], info['data'])

    def pubkey(self):
        return jsonify({
            'pubkey': self.config['pubkey']
        })

