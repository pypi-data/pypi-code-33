from jivi.oe.Statement.Define.Define import Define
class Widget(Define):
	type = 'widget'
	def __init__(self,*a,**b):
		Define.__init__(self,*a,**b)

	def pre_init(self):
		Define.pre_init(self)
		
	def set_variable(self):
		if not self.read_input('datatype','as'):
			if self.read_input('like','like'):
				likeel = self.window.get_widget(self.like)
				if likeel:
					for a,b in likeel.tab.items():
						self.set_if_none(a,b)
	

		