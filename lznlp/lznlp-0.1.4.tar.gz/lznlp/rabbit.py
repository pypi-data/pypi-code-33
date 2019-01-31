# -*- coding: utf-8 -*-

import logging
import pika
import configparser
import json

FORMAT = '%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT)
log_level = logging.INFO 
logging.getLogger().setLevel(log_level)

config = configparser.ConfigParser()


class JsonCustomEncoder(json.JSONEncoder): 
    
    def default(self, obj): 
     
        if isinstance(obj, datetime): 
            return obj.strftime('%Y-%m-%d %H:%M:%S') 
        elif isinstance(obj, date): 
            return obj.strftime('%Y-%m-%d') 
        elif isinstance(obj, numpy.float32):
            return obj.item()
        else: 
            return json.JSONEncoder.default(self, obj) 


class Rabbit(object):

    """LiangZhiNLP Python RabbitMQ 工具访问的封装类

    :param string host: MQ服务地址，默认localhost

    :param int port: MQ服务端口，默认5672

    :param string user: 连接MQ的用户名，默认guest

    :param string password: 连接MQ的密码，默认guest

    :param string catch_exchange: 消费数据的exchange名称，默认空串

    :param string catch_queue: 消费数据的queue名称，默认空串

    :param string throw_exchange: 生产数据的exchange名称，默认空串

    :param string throw_queue: 生产数据的queue名称，默认空串

    """
    conn_info = {}

    def __init__(self, 
        host='localhost', 
        port=5672, 
        user='guest', 
        password='guest', 
        catch_exchange='', 
        catch_queue='', 
        throw_exchange='', 
        throw_queue=''):
        self.conn_info['host'] = host
        self.conn_info['port'] = port
        self.conn_info['user'] = user
        self.conn_info['password'] = password
        self.conn_info['catch_exchange'] = catch_exchange
        self.conn_info['catch_queue'] = catch_queue
        self.conn_info['throw_exchange'] = throw_exchange
        self.conn_info['throw_queue'] = throw_queue

    def catchRabbit(self, callback, exchange_type = 'direct', durable = True, auto_delete = False, no_ack = True):
        credentials = pika.PlainCredentials(self.conn_info['user'], self.conn_info['password'])
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.conn_info['host'], port=int(self.conn_info['port']), credentials=credentials, heartbeat_interval=0)
        )
        channel_consume = connection.channel()
        logging.info('>>>>>>>>>>>>>>>>>>>>>>>')
        channel_consume.exchange_declare(
            exchange = self.conn_info['catch_exchange'], 
            exchange_type = exchange_type, 
            durable = durable, 
            auto_delete = auto_delete
        )
        channel_consume.queue_declare(
            queue = self.conn_info['catch_queue'], 
            durable = durable
        )
        channel_consume.queue_bind(
            exchange = self.conn_info['catch_exchange'], 
            queue = self.conn_info['catch_queue']
        )
        channel_consume.basic_consume(
            callback,
            queue = self.conn_info['catch_queue'],
            no_ack = no_ack
        )
        
        logging.info('Waiting for messages...')
        try:
            channel_consume.start_consuming()
        except KeyboardInterrupt:
            logging.info("Stop consuming now!")
            channel_consume.stop_consuming()
        connection.close()

    def throwRabbit(self, body, exchange_type = 'direct', durable = True, auto_delete = False):
        credentials = pika.PlainCredentials(self.conn_info['user'], self.conn_info['password'])
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.conn_info['host'], port=int(self.conn_info['port']), credentials=credentials)
        )
        channel_produce = connection.channel()
        channel_produce.exchange_declare(
            exchange = self.conn_info['throw_exchange'], 
            exchange_type = exchange_type, 
            durable = durable, 
            auto_delete = auto_delete
        )
        # channel_produce.queue_declare(
        #     queue = self.conn_info['throw_queue'], 
        #     durable = durable
        # )
        # channel_produce.queue_bind(exchange = self.conn_info['throw_exchange'], queue = self.conn_info['throw_queue'])
        channel_produce.basic_publish(
            exchange = self.conn_info['throw_exchange'], 
            routing_key = self.conn_info['throw_queue'], 
            body=json.dumps(body, cls = JsonCustomEncoder)
        )

        logging.warn("Delivered result data to knowledge queue: " + self.conn_info['throw_queue'])
        logging.info('<<<<<<<<<<<<<<<<<<<<<<<<<')

    #def callback(self, ch, method, properties, body):
        # 触发从mongodb读取全量数据进行dedupe clustering


        # 从结果cluster中找到body的数据

        # 将带cluster id的数据通过生产者发送出去
