# coding:utf8
import sys

if sys.version > '3':
    PY3 = True
else:
    PY3 = False

import pika
import pika.exceptions

class mqapi(object):
    def __init__(self,host,username,password,virtualhost="/",callback=None,port=5672):
        '''
        RabbitMQ 消息队列出书画
        :param host: 主机地址
        :param username: 用户名
        :param password: 密码
        :param virtualhost: virtualhost
        :param callback: 回调地址，发现消息这个可以不填
        :param port: 端口
        '''

        self.user_pwd = pika.PlainCredentials(username, password)
        self.parameters = pika.ConnectionParameters(host=host, credentials=self.user_pwd, heartbeat=0,virtual_host=virtualhost)

        # 定义交换机，设置类型为direct
        # self.channel = self.s_conn.channel()
        self.callback = callback
    def __enter__(self):
        pass
    def send_msg(self,queue_name,body,exchange=''):
        '''
        消息发送
        :param queue_name: queue名称
        :param body: 参数
        :param exchange: exchange
        :return:
        '''
        try:
            self.s_conn = pika.BlockingConnection(self.parameters)  # 创建连接
            self.channel = self.s_conn.channel()
        except pika.exceptions.ConnectionClosed:
            self.s_conn = pika.BlockingConnection(self.parameters)
            self.channel = self.s_conn.channel()
        except :
            self.s_conn = pika.BlockingConnection(self.parameters)
            self.channel = self.s_conn.channel()
        if exchange:
            self.channel.exchange_declare(exchange=exchange, exchange_type='direct',durable=True)
        self.channel.queue_declare(queue=queue_name)  # 声明一个队列，生产者和消费者都要声明一个相同的队列，用来防止万一某一方挂了，另一方能正常运行
        self.channel.basic_publish(exchange=exchange,  # 交换机
                           routing_key=queue_name,  # 路由键，写明将消息发往哪个队列，本例是将消息发往队列hello
                           body=body)  # 生产者要发送的消息
        self.s_conn.close()
    def receive_msg(self,routings,exchange=''):
        '''
        接收消息
        :param routings:
        :param exchange:
        :return:
        '''
        try:
            self.s_conn = pika.BlockingConnection(self.parameters)  # 创建连接
            self.channel = self.s_conn.channel()
        except pika.exceptions.ConnectionClosed:
            self.s_conn = pika.BlockingConnection(self.parameters)
            self.channel = self.s_conn.channel()
        except Exception as e:
            self.s_conn = pika.BlockingConnection(self.parameters)
            channel = self.s_conn.channel()
        if exchange:
            self.channel.exchange_declare(exchange=exchange, exchange_type='direct',durable=True)
        for routing in routings:
            self.channel.queue_declare(queue=routing)  # 声明一个队列，生产者和消费者都要声明一个相同的队列，用来防止万一某一方挂了，另一方能正常运行
            self.channel.queue_bind(exchange=exchange,
                           queue=routing,
                           routing_key=routing)
            self.channel.basic_consume(self.__callback, queue=routing, no_ack=False)
        try:
            self.channel.start_consuming()
        except:
            print(sys.exc_info())
        self.s_conn.close()
    def __callback(self,ch, method, properties, body):
        '''
        回调处理
        :param ch:通道
        :param method:方法
        :param properties:
        :param body:
        :return:
        '''
        # print " [x] Received %r" % (body,)
        # print method.routing_key
        # print method.exchange
        try:
            if self.callback:
                self.callback(method.routing_key,body)
            #回复ack
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except:
            print(sys.exc_info())


    def __exit__(self, exc_type, exc_val, exc_tb):
        print("exit rabbit mq")
