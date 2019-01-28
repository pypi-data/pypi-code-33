import json
import select
import struct
import time
import socket
from queue import Queue
import six
from twisted.internet.protocol import Protocol
from .bean import SubscripProtos_pb2, PublishProtos_pb2
from .src.config import SDKConfig
from .src.httpResult import result

global subClientHandler
subClientHandler = None
class AbstractClientSDK(Protocol):
      PARSING_LEN = 0
      PARSING_MSG = 1
      send_queue  = Queue()
      su_bean     = Queue()
      init_sub_flag = False
      topic       = ""
      number_line = 3

      def __init__(self,config):
          try:
              if not config:
                 raise RuntimeError("Parameter is wrong")
          except Exception as  e:
              print(e)
              exit()
          self._config = config
          self.data_buffer = b""
          self.parse_status = self.PARSING_LEN
          self.msg_len = 0
          self.num  = 0


      def connect(self,subCallback="",pubCallback=""):
          self._pubCallback = pubCallback
          self._subCallback = subCallback
          self.login()
          self.connects(self.getPubSubServer(),self.getTcpPort())

      def login(self):
          dataArray = {
              SDKConfig.CLIENT_ID:self.getClientId(),
              SDKConfig.SECRET_KEY:self.getSecret()
          }

          token =  result.post(self.getHttpServer(),dataArray)
          self.setToken(token)

      """
      初始化连接
      """
      def connects(self,host,port):
          timeout = 50
          global subClientHandler
          subClientHandler = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
          subClientHandler.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
          addr = (socket.gethostbyname(host),port)
          try:
                  self.num += 1
                  if subClientHandler.connect_ex(addr) != self.PARSING_LEN:
                      if self.num == 10:
                          exit()
                      self.connect("","")

                  subClientHandler.settimeout(timeout)
                  self.activate()
          except:
            subClientHandler.close()
            raise RuntimeError("tcp connects to  fails ")
      """
      发布消息
      """
      def backPublish(self,topic,jsonData):
          self.validate()
          pro = PublishProtos_pb2.ProtocolEnum.items()
          data = self.builderPubBean(dict(pro)["BACKPUB"], topic, jsonData)
          self.send(data)
          # result = subClientHandler.recv(1024)
          # self.analysis(result)
      """
      订阅
      """
      def subscript(self,topic=""):
          self.validate()
          pro = PublishProtos_pb2.ProtocolEnum.items()
          data = self.builderPubBean(dict(pro)["SUB"], topic, "")
          self.senSug(data)
          self.topic   = topic
          self.init_sub_flag = True
          self.send(data)
      """
       发布消息
      """
      def publish(self,jsonData):
          self.validate()
          pro = PublishProtos_pb2.ProtocolEnum.items()
          data = self.builderPubBean(dict(pro)["PUB"], "", jsonData)
          self.send(data)
      def validate(self):
          if(subClientHandler == None):
             raise RuntimeError("请求先调用connect方法")

      """
      获取的消息
      """
      def builderPubBean(self,number,topic,data):
          publish =  PublishProtos_pb2.PublishBean()
          publish.token = "*"
          publish.topicPath = topic
          publish.protocolType = number
          publish.body   = data
          return publish


      def builderPubBeanToken(self,number):
          publish = PublishProtos_pb2.PublishBean()
          publish.token = self.getToken()
          publish.protocolType = number
          return publish

      """
      连接
      """
      def activate(self):
             print("--------------连接激活"+str(self.num)+"次--------------")
             print("--------------完成订阅--------------")
             self.num += 1
             pro = PublishProtos_pb2.ProtocolEnum.items()
             dataConn = self.builderPubBeanToken(dict(pro)["CONN"])
             self.send(dataConn)
             if self.init_sub_flag == True:
                 pro = PublishProtos_pb2.ProtocolEnum.items()
                 data = self.builderPubBean(dict(pro)["SUB"], self.topic, "")
                 self.sendSig(data)
                 self.su_bean = data
                 subClientHandler.sendall(self.su_bean.get() + self.su_bean.get())
                 result = subClientHandler.recv(1024)
                 self.analysis(result)


      def send(self,data):
              self.sendSig(data)
              if self.send_queue.qsize() == self.number_line:
                  subClientHandler.sendall(self.send_queue.get() + self.send_queue.get() + self.send_queue.get())
              else:
                  subClientHandler.sendall(self.send_queue.get() + self.send_queue.get())
              result = subClientHandler.recv(1024)
              self.analysis(result)

      """
      发的数据前面加消息的长度和消息
      消息的长度编码为 Varint32
      https://blog.csdn.net/lucyTheSlayer/article/details/79722751  可查阅
      """
      def sendSig(self,sig):
        value = len(sig.SerializeToString())
        bits = value & 0x7f
        value >>= 7
        while value:
            self.send_queue.put(six.int2byte(0x80 | bits))
            bits = value & 0x7f
            value >>= 7
        self.send_queue.put(six.int2byte(bits))
        self.send_queue.put(sig.SerializeToString())

      """
      解析返回的数据
      """
      def  analysis(self,data):
              for b in data:
                  if self.parse_status == self.PARSING_LEN:
                      self.data_buffer += six.int2byte(b)
                      if not (b & 0x80):
                          self.msg_len = self.DecodeVarint(self.data_buffer)
                          self.parse_status = self.PARSING_MSG
                          self.data_buffer = b""
                          continue
                  elif self.parse_status == self.PARSING_MSG:
                      self.data_buffer += six.int2byte(b)
                      if len(self.data_buffer) == self.msg_len:
                          sig = SubscripProtos_pb2.ResultBean()
                          sig.ParseFromString(self.data_buffer)
                          self.process(sig)
                          self.data_buffer = b""
                          self.msg_len = 0
                          self.parse_status = self.PARSING_LEN

      def process(self, sig):
          try:
              if sig.message == SDKConfig.ERROR:
                  raise RuntimeError("Insufficient permissions, channel closed ")
              else:
                  print("read 接受到服务器消息：" + str(sig))
          except Exception as e:
              subClientHandler.close()
              print(e)


      def DecodeVarint(self,buffer):
          mask = (1 << 32) - 1
          result_type = int
          result = 0
          shift = 0
          for b in buffer:
              result |= ((b & 0x7f) << shift)
              shift += 7
              if shift >= 64:
                  raise Exception('Too many bytes when decoding varint.')
          result &= mask
          result = result_type(result)
          return result


      def senSug(self,data):
          value = len(data.SerializeToString())
          bits = value & 0x7f
          value >>= 7
          while value:
              self.su_bean.put(six.int2byte(0x80 | bits))
              bits = value & 0x7f
              value >>= 7
          self.su_bean.put(six.int2byte(bits))
          self.su_bean.put(data.SerializeToString())



      def getPubSubServer(self):
          return SDKConfig.PUB_SUB_SERVER + ""
      def getTcpPort(self):
          return SDKConfig.TCP_PORT
      def getToken(self):
           if SDKConfig.ACCESS_TOKEN  in self._config:
               return self._config[SDKConfig.ACCESS_TOKEN]
           self.login()
      def setToken(self,data):
         self._config[SDKConfig.ACCESS_TOKEN] = data
      def getApiServer(self):
          return SDKConfig.API_SERVER
      def getHttpPost(self):
          return SDKConfig.HTTP_PORT
      def getHttpServer(self):
          return self.getApiServer()+":"+str(self.getHttpPost())
      def getClientId(self):
          return self._config[SDKConfig.CLIENT_ID]
      def getSecret(self):
          return self._config[SDKConfig.SECRET_KEY]
