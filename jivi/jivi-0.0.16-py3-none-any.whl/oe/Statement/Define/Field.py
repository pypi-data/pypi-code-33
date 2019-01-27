from jivi.oe.Statement.Define.Widget import Widget
from jivi.oe.Statement.helpers import *

class Field(Widget):
	type = 'field'
	def __init__(self,*a,**b):
		Widget.__init__(self,*a,**b)

	def pre_init(self):
		Widget.pre_init(self)
		self.set_variable()
		