


from .Color import Color




class CSSMap(object):

	def __init__(self, *args, **kwargs):
		for k, v in kwargs.items():
			setattr(self, k, v)
	#

	def __bool__(self):
		for k in dir(self):
			if k.startswith("__"):
				continue
			return True
		return False
	#

	def __str__(self):
		ret = []
		for k in dir(self):
			if k.startswith("__"):
				continue

			if len(ret) > 0:
				ret.append(" ")

			ret.append(k.replace("_", "-"))
			ret.append(":")

			v = getattr(self, k)
			if isinstance(v, Color):
				ret.append(v.toHTML())
			elif isinstance(v, (int, float)):
				ret.append(str(v))
			elif isinstance(v, str):
				ret.append(v)
			else:
				raise Exception("Unexpected value type specified for CSS attribute '" + k + "': type " + str(type(v)) + ", value " + repr(v))
			ret.append(";")
		return "".join(ret)
	#

#



