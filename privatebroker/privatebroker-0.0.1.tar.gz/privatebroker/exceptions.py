import sys
import inspect
from abc import ABCMeta, abstractmethod

class PrivateMethodError(Exception):
	pass

class BrokerException(Exception):
	pass

class Exception():
	
	def __init__(self, class_, func, *args, **kwargs):
		self.class_ = class_
		self.args = args
		self.kwargs = kwargs
		self.func = func


	def private_exception(self):
		
		stack = inspect.stack()
		filename = stack[-1].filename
		line = stack[-1].lineno
		
		code = """ in: "{}" ,line: "{}", "{}" - it's a private method of another class. """.format(
						filename, line, func,
					)
		raise PrivateMethodError(code)
