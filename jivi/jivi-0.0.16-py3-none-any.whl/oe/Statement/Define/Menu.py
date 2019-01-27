from jivi.oe.Statement.Define.Widget import Widget
class Menu(Widget):
	type = 'menu'
	def __init__(self,*a,**b):
		Widget.__init__(self,*a,**b)




class Submenu(Widget):
	type = 'sub-menu'
	def __init__(self,*a,**b):
		Widget.__init__(self,*a,**b)