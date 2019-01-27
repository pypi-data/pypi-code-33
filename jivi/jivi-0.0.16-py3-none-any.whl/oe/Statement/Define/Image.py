from jivi.oe.Statement.Define.Widget import Widget
class Image(Widget):
	type = 'image'
	def __init__(self,*a,**b):
		Widget.__init__(self,*a,**b)