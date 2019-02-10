
class Adapter:
	def __init__(self, x, y):
		"""
		:param list x: list of input values
		:param list y: list of output values
		"""
		self._x_type = type(x[0])
		self._y_type = type(y[0])

