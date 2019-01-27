from jivi.oe.Statement.Define.Widget import Widget
class Rectangle(Widget):
	type = 'rectangle'
	def __init__(self,*a,**b):
		Widget.__init__(self,*a,**b)