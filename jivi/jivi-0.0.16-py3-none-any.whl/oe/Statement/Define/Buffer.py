from jivi.oe.Statement.Define.Widget import Widget
class Buffer(Widget):
	type = 'buffer'
	def __init__(self,*a,**b):
		Widget.__init__(self,*a,**b)