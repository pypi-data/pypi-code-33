import inspect
from privatebroker.exceptions import Exception, BrokerException
from abc import ABCMeta, abstractmethod


class private_method(ABCMeta):
	
	__instances = {}
	
	__broker = {}
	
	
	def __add_broker(self, class_, methods, *args, **kwargs):
		self.__broker[class_] = methods

	
	def broker(self, class_, func):
		try:
			func == str()
			return self.__broker[class_][func]
		
		except KeyError:
			err = "broker has no private methods for " + str(class_ ) + """\n
the broker takes 2 values: broker(class_, "name_function")"""
			raise BrokerException(err)
	

	
	def __call__(cls, class_, methods, *args, **kwargs):
		
		patter = inspect.getmro(class_)[1] if len(inspect.getmro(class_)) > 2 else object
		
		if class_ not in cls.__instances:
			
			cls.__instances[class_] = type(
				
				class_.__name__,
				
				(patter,),
				
				dict(class_.__dict__)
			)
		
		cls.__add_broker(
			cls.__instances[class_],
			methods
			)

		setattr(
			cls.__instances[class_],
			cls.broker.__name__,
			cls.broker
			)
		
		for k, v in methods.items():
			
			excep = Exception(class_, k)
			
			setattr(
				cls.__instances[class_], 
				k,
				excep.private_exception
				)
		
		return cls.__instances[class_]

	
	
class PrivateClassBroker(metaclass=private_method):
	pass


class PrivateBroker(ABCMeta):
	
	__line = {}
	__methods = {}
	
	
	@classmethod
	def privatemethod(cls, func):
		
		cls.__methods[func.__name__] = func
		
		return func
	
	def privateclass(cls, *args, **kwargs):
		
		PrivateBroker._PrivateBroker__line[cls] = PrivateBroker._PrivateBroker__methods
		
		broker  = PrivateClassBroker(
					cls,
					PrivateBroker._PrivateBroker__line[cls]
					)
		return broker


privatemethod = PrivateBroker.privatemethod
privateclass = PrivateBroker.privateclass




