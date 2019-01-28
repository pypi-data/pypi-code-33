"""
客户端处理类
"""

class SubClientHandler:
      def __init__(self,callback,pubCallback,token):
          self._callback = callback
          self._pubCallback = pubCallback
          self._token = token


